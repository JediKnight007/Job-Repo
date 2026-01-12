"""
All-in-one scraper and pipeline for kino-teatr.ru Soviet film data.

This single file contains:
- Selenium-based scraper (`KinoTeatrScraper`)
- Fast requests+BeautifulSoup scraper (`FastKinoTeatrScraper`)
- Ticket price handling and merge logic (box office calculation)
- CLI to run the full 3-step pipeline.
"""

import argparse
import csv
import re
import time
from collections import defaultdict
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin


# ---------------------------------------------------------------------------
# Ticket prices (stylized year-by-year schedule in rubles)
# ---------------------------------------------------------------------------

TICKET_PRICES_BY_YEAR: Dict[int, float] = {
    # 1950s: Stable low prices (0.25-0.30 rubles)
    1950: 0.25, 1951: 0.26, 1952: 0.27, 1953: 0.27, 1954: 0.28,
    1955: 0.28, 1956: 0.29, 1957: 0.29, 1958: 0.30, 1959: 0.30, 1960: 0.30,

    # 1960s: Gradual increase (0.30-0.40 rubles)
    1961: 0.31, 1962: 0.32, 1963: 0.33, 1964: 0.34, 1965: 0.35,
    1966: 0.36, 1967: 0.37, 1968: 0.38, 1969: 0.39, 1970: 0.40,

    # 1970s: Continued increase (0.40-0.50 rubles)
    1971: 0.41, 1972: 0.42, 1973: 0.43, 1974: 0.44, 1975: 0.45,
    1976: 0.46, 1977: 0.47, 1978: 0.48, 1979: 0.49, 1980: 0.50,

    # 1980s-1991: Higher prices (0.50-0.60 rubles)
    1981: 0.51, 1982: 0.52, 1983: 0.53, 1984: 0.54, 1985: 0.55,
    1986: 0.56, 1987: 0.57, 1988: 0.58, 1989: 0.59, 1990: 0.60, 1991: 0.60,
}


def get_ticket_price(year: int) -> float:
    """Get average ticket price for a given year (in rubles)."""
    if year in TICKET_PRICES_BY_YEAR:
        return TICKET_PRICES_BY_YEAR[year]
    if year < 1950:
        return TICKET_PRICES_BY_YEAR[1950]
    if year > 1991:
        return TICKET_PRICES_BY_YEAR[1991]
    # Default fallback inside range (should not normally happen)
    return 0.50


# ---------------------------------------------------------------------------
# Selenium-based scraper
# ---------------------------------------------------------------------------

class KinoTeatrScraper:
    """Selenium-based scraper for kino-teatr.ru."""

    def __init__(self, headless: bool = True, delay: float = 2.0, timeout: int = 180, max_retries: int = 3):
        self.headless = headless
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://www.kino-teatr.ru"
        self.driver: Optional[webdriver.Chrome] = None

    # --- Selenium driver management -------------------------------------------------

    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        # Hide automation indicators to avoid CAPTCHA
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.page_load_strategy = "eager"
        # Additional stealth options
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to hide webdriver property and remove automation banner
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                // Remove automation banner
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            '''
        })
        
        self.driver.set_page_load_timeout(self.timeout)
        self.driver.implicitly_wait(10)
        return self.driver

    def cleanup_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    # --- Parsing helpers ------------------------------------------------------------

    @staticmethod
    def parse_viewers(viewers_text: str) -> Optional[int]:
        if not viewers_text:
            return None
        viewers_clean = viewers_text.replace(" ", "").replace(",", "")
        try:
            return int(viewers_clean)
        except ValueError:
            return None

    @staticmethod
    def parse_country_and_year(country_year_text: str):
        if not country_year_text:
            return (None, None)
        parts = country_year_text.split(",")
        if len(parts) >= 2:
            country = parts[0].strip()
            year_match = re.search(r"(\d{4})", parts[-1])
            if year_match:
                try:
                    production_year = int(year_match.group(1))
                except ValueError:
                    production_year = None
            else:
                production_year = None
            return country, production_year
        if len(parts) == 1:
            year_match = re.search(r"(\d{4})", parts[0])
            if year_match:
                try:
                    production_year = int(year_match.group(1))
                    return (None, production_year)
                except ValueError:
                    pass
            return (parts[0].strip(), None)
        return (None, None)

    # --- Year-page scraping ---------------------------------------------------------

    def scrape_year_page(self, year: int):
        """Scrape a year page (e.g., y1975) and return list of film dicts."""
        url = f"{self.base_url}/box/history/sov/y{year}/"
        print(f"Scraping year {year}: {url}")

        if not self.driver:
            self.setup_driver()

        films = []
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    print(f"  Retry attempt {attempt}/{self.max_retries}...")
                    time.sleep(self.delay * attempt)

                self.driver.get(url)
                # Wait longer for DDoS Guard redirect/challenge to complete
                time.sleep(self.delay * 3)
                
                # Wait for redirect to complete and page to load
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                
                # Additional wait for any DDoS Guard challenge
                time.sleep(2)
                
                # Now wait for table to appear
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                rows = self.driver.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) != 3:
                        continue

                    rank_cell, info_cell, viewers_cell = cells
                    rank_text = rank_cell.text.strip()
                    if not (rank_text and rank_text.endswith(".") and rank_text[:-1].isdigit()):
                        continue

                    rank = int(rank_text[:-1])

                    # Title + URL
                    try:
                        title_link = info_cell.find_element(By.CSS_SELECTOR, "h4 a")
                        name_russian = title_link.find_element(By.TAG_NAME, "strong").text.strip()
                        film_url = title_link.get_attribute("href")
                        if film_url and not film_url.startswith("http"):
                            film_url = urljoin(self.base_url, film_url)
                    except Exception as e:
                        print(f"  Warning: Could not extract title/link for rank {rank}: {e}")
                        name_russian = None
                        film_url = None

                    # Country + production year
                    country = None
                    production_year = None
                    try:
                        sm_spans = info_cell.find_elements(By.CSS_SELECTOR, "p span.sm")
                        for span in sm_spans:
                            text = span.text.strip()
                            if span.find_elements(By.TAG_NAME, "a"):
                                continue
                            if text and ("," in text or re.search(r"\d{4}", text)):
                                country, production_year = self.parse_country_and_year(text)
                                break
                    except Exception as e:
                        print(f"  Warning: Could not extract country/year for rank {rank}: {e}")

                    viewers_text = viewers_cell.text.strip()
                    viewers_total = self.parse_viewers(viewers_text)

                    films.append(
                        {
                            "rank": rank,
                            "name_russian": name_russian,
                            "film_url": film_url,
                            "country": country,
                            "production_year": production_year,
                            "soviet_release_year": year,
                            "viewers_total": viewers_total,
                        }
                    )
                    print(f"  ✓ Rank {rank}: {name_russian} ({viewers_total:,} viewers)")

                print(f"  Found {len(films)} films for year {year}")
                return films

            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                if "Timeout" in error_type or "timeout" in str(e).lower():
                    if attempt < self.max_retries:
                        print(f"  ⚠ Timeout on attempt {attempt}, will retry...")
                        continue
                    print(f"  ✗ Timeout after {self.max_retries} attempts")
                else:
                    print(f"  ✗ Error scraping year {year}: {e}")
                    import traceback

                    traceback.print_exc()
                    return []

        print(f"  ✗ Failed to scrape year {year} after {self.max_retries} attempts")
        if last_error:
            print(f"  Last error: {last_error}")
        return []

    def scrape_years(self, start_year: int = 1950, end_year: int = 1991, output_csv: str = "soviet_releases.csv"):
        """Scrape multiple years (sequential, Selenium only)."""
        all_films = []
        try:
            self.setup_driver()
            for year in range(start_year, end_year + 1):
                films = self.scrape_year_page(year)
                all_films.extend(films)
                time.sleep(self.delay)
        finally:
            self.cleanup_driver()

        if not all_films:
            print("\n✗ No films found")
            return None

        all_films.sort(
            key=lambda x: (int(x.get("soviet_release_year", 0)), int(x.get("rank", 0)))
        )
        fieldnames = [
            "rank",
            "name_russian",
            "film_url",
            "country",
            "production_year",
            "soviet_release_year",
            "viewers_total",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_films)
        print(f"\n✓ Saved {len(all_films)} films to {output_csv}")
        return output_csv

    # --- Film-page scraping ---------------------------------------------------------

    def scrape_film_page(self, film_url: str):
        """Scrape individual film page with Selenium for metadata."""
        if not film_url:
            return None

        print(f"  Scraping film page: {film_url}")
        if not self.driver:
            self.setup_driver()

        metadata = {
            "film_url": film_url,
            "name_original": None,
            "country_of_origin": None,
            "short_description": None,
            "production_year": None,
            "kinopoisk_id": None,
        }

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    print(f"    Retry attempt {attempt}/{self.max_retries}...")
                    time.sleep(self.delay * attempt)

                self.driver.get(film_url)
                time.sleep(self.delay)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                break
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                if "Timeout" in error_type or "timeout" in str(e).lower():
                    if attempt < self.max_retries:
                        continue
                    print(f"    ✗ Timeout after {self.max_retries} attempts")
                    return metadata
                print(f"    ✗ Error loading page: {e}")
                return metadata

        try:
            # info_table structure
            try:
                param_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.info_table_param")
                for param_div in param_divs:
                    label = param_div.text.strip()
                    try:
                        data_div = param_div.find_element(
                            By.XPATH, "following-sibling::div[@class='info_table_data']"
                        )
                        value = data_div.text.strip()
                        try:
                            strong = data_div.find_element(By.TAG_NAME, "strong")
                            value = strong.text.strip()
                        except Exception:
                            pass

                        if label == "Оригинальное название" and not metadata["name_original"]:
                            metadata["name_original"] = value
                        elif label == "Страна" and not metadata["country_of_origin"]:
                            metadata["country_of_origin"] = value
                        elif label == "Год" and not metadata["production_year"]:
                            year_match = re.search(r"(\d{4})", value)
                            if year_match:
                                try:
                                    metadata["production_year"] = int(year_match.group(1))
                                except ValueError:
                                    pass
                    except Exception:
                        continue
            except Exception as e:
                print(f"    Warning: Could not extract from info_table: {e}")

            # Description
            try:
                desc_selectors = [
                    "div[itemprop='description']",
                    "div.description",
                    "p.description",
                    "div.about_film",
                ]
                for selector in desc_selectors:
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        desc = desc_elem.text.strip()
                        if len(desc) > 50:
                            metadata["short_description"] = desc[:500]
                            break
                    except Exception:
                        continue

                if not metadata["short_description"]:
                    page_text = self.driver.page_source
                    desc_patterns = [
                        r'<div[^>]*itemprop=["\']description["\'][^>]*>([^<]{50,500})',
                        r"Сюжет[:\s]+([^<\n]{50,500})",
                    ]
                    for pattern in desc_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                        if match:
                            desc = match.group(1).strip()
                            desc = re.sub(r"<[^>]+>", "", desc)
                            desc = re.sub(r"\s+", " ", desc)
                            if len(desc) > 50:
                                metadata["short_description"] = desc[:500]
                                break
            except Exception as e:
                print(f"    Warning: Could not extract description: {e}")

            # Kinopoisk ID
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "kinopoisk.ru" in href:
                        match = re.search(r"/(\d+)/", href)
                        if match:
                            metadata["kinopoisk_id"] = match.group(1)
                            break
            except Exception as e:
                print(f"    Warning: Could not extract Kinopoisk ID: {e}")

            # Success - metadata extracted (don't print every one to reduce noise)
            return metadata
        except Exception as e:
            # Silently skip errors - we'll collect what we can
            return metadata

    # --- Film metadata scraping over CSV -------------------------------------------

    def scrape_film_metadata(self, input_csv: str = "soviet_releases.csv", output_csv: str = "films_metadata.csv"):
        """Scrape metadata for all unique films referenced in a CSV."""
        film_urls = set()
        try:
            with open(input_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("film_url")
                    if url:
                        film_urls.add(url)
            print(f"Found {len(film_urls)} unique film URLs")
        except FileNotFoundError:
            print(f"✗ Input CSV {input_csv} not found. Run scrape_years() first.")
            return None

        all_metadata = []
        try:
            self.setup_driver()
            for i, film_url in enumerate(film_urls, 1):
                print(f"[{i}/{len(film_urls)}] ", end="")
                metadata = self.scrape_film_page(film_url)
                if metadata:
                    all_metadata.append(metadata)
                time.sleep(self.delay)
        finally:
            self.cleanup_driver()

        if not all_metadata:
            print("\n✗ No metadata found")
            return None

        fieldnames = [
            "film_url",
            "name_original",
            "country_of_origin",
            "short_description",
            "production_year",
            "kinopoisk_id",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_metadata)

        print(f"\n✓ Saved metadata for {len(all_metadata)} films to {output_csv}")
        return output_csv

    # --- Merge + box office --------------------------------------------------------

    def merge_data(
        self,
        releases_csv: str = "soviet_releases.csv",
        metadata_csv: str = "films_metadata.csv",
        output_csv: str = "soviet_films_complete.csv",
    ):
        """Merge year-page data with film metadata and calculate box office."""
        try:
            releases: Dict[str, list] = {}
            with open(releases_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("film_url")
                    if url:
                        releases.setdefault(url, []).append(row)

            metadata_by_url: Dict[str, dict] = {}
            try:
                with open(metadata_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        url = row.get("film_url")
                        if url:
                            metadata_by_url[url] = row
            except FileNotFoundError:
                print(f"Warning: {metadata_csv} not found. Proceeding without metadata.")

            merged_rows = []
            for url, release_list in releases.items():
                meta = metadata_by_url.get(url, {})
                for release in release_list:
                    name_original = release.get("name_original") or meta.get("name_original") or ""
                    merged = {
                        "rank": release.get("rank"),
                        "name_russian": release.get("name_russian"),
                        "name_original": name_original,
                        "film_url": url,
                        "country": release.get("country") or meta.get("country_of_origin") or "",
                        "country_of_origin": meta.get("country_of_origin") or release.get("country") or "",
                        "production_year": meta.get("production_year") or release.get("production_year") or "",
                        "soviet_release_year": release.get("soviet_release_year"),
                        "viewers_total": release.get("viewers_total"),
                        "short_description": meta.get("short_description") or "",
                        "kinopoisk_id": meta.get("kinopoisk_id") or "",
                    }

                    viewers = release.get("viewers_total")
                    release_year = release.get("soviet_release_year")
                    if viewers and release_year:
                        try:
                            viewers_int = int(viewers)
                            year_int = int(release_year)
                            ticket_price = get_ticket_price(year_int)
                            box_office = viewers_int * ticket_price
                            merged["avg_ticket_price_rub"] = ticket_price
                            merged["box_office_rubles"] = box_office
                        except (ValueError, TypeError):
                            merged["avg_ticket_price_rub"] = ""
                            merged["box_office_rubles"] = ""
                    else:
                        merged["avg_ticket_price_rub"] = ""
                        merged["box_office_rubles"] = ""

                    merged_rows.append(merged)

            if not merged_rows:
                print("\n✗ No data to merge")
                return None

            fieldnames = [
                "rank",
                "name_russian",
                "name_original",
                "film_url",
                "country",
                "country_of_origin",
                "production_year",
                "soviet_release_year",
                "viewers_total",
                "avg_ticket_price_rub",
                "box_office_rubles",
                "short_description",
                "kinopoisk_id",
            ]
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(merged_rows)
            print(f"\n✓ Merged {len(merged_rows)} records to {output_csv}")
            return output_csv
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            return None


# ---------------------------------------------------------------------------
# Fast scraper (requests + BeautifulSoup + optional Selenium for films)
# ---------------------------------------------------------------------------

class FastKinoTeatrScraper:
    """Fast scraper using requests + BeautifulSoup for year pages, optional Selenium for films."""

    def __init__(self, delay: float = 0.5, max_workers: int = 5, use_selenium_for_films: bool = False):
        self.delay = delay
        self.max_workers = max_workers
        self.use_selenium_for_films = use_selenium_for_films
        self.base_url = "https://www.kino-teatr.ru"
        self.session = requests.Session()
        # Use more realistic headers to avoid bot detection
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.kino-teatr.ru/",
                "DNT": "1",
            }
        )
        self.selenium_scraper: Optional[KinoTeatrScraper] = None
        if self.use_selenium_for_films:
            self.selenium_scraper = KinoTeatrScraper(headless=True, delay=1)

    @staticmethod
    def parse_viewers(viewers_text: str) -> Optional[int]:
        if not viewers_text:
            return None
        viewers_clean = viewers_text.replace(" ", "").replace(",", "")
        try:
            return int(viewers_clean)
        except ValueError:
            return None

    @staticmethod
    def parse_country_and_year(country_year_text: str):
        if not country_year_text:
            return (None, None)
        parts = country_year_text.split(",")
        if len(parts) >= 2:
            country = parts[0].strip()
            year_match = re.search(r"(\d{4})", parts[-1])
            if year_match:
                try:
                    production_year = int(year_match.group(1))
                except ValueError:
                    production_year = None
            else:
                production_year = None
            return country, production_year
        if len(parts) == 1:
            year_match = re.search(r"(\d{4})", parts[0])
            if year_match:
                try:
                    production_year = int(year_match.group(1))
                    return (None, production_year)
                except ValueError:
                    pass
            return (parts[0].strip(), None)
        return (None, None)

    def scrape_year_page(self, year: int):
        """Scrape a year page using requests + BeautifulSoup (fast)."""
        url = f"{self.base_url}/box/history/sov/y{year}/"
        print(f"Scraping year {year}: {url}")
        films = []
        try:
            response = self.session.get(url, timeout=(10, 30))
            response.encoding = "windows-1251"
            response.raise_for_status()

            if "Роботам запрещено" in response.text or "captcha" in response.text.lower():
                print(f"  ⚠ Bot detection page received for year {year}, skipping...")
                return []

            soup = BeautifulSoup(response.text, "lxml")
            rows = soup.find_all("tr")
            if not rows:
                print(f"  ⚠ No table rows found for year {year}, page might be blocked")
                return []

            for row in rows:
                cells = row.find_all("td")
                if len(cells) != 3:
                    continue

                rank_cell, info_cell, viewers_cell = cells
                rank_text = rank_cell.get_text(strip=True)
                if not (rank_text and rank_text.endswith(".") and rank_text[:-1].isdigit()):
                    continue
                rank = int(rank_text[:-1])

                name_russian = None
                name_original = None
                film_url = None
                try:
                    h4 = info_cell.find("h4")
                    title_link = h4.find("a") if h4 else None
                    if title_link:
                        strong = title_link.find("strong")
                        name_russian = strong.get_text(strip=True) if strong else title_link.get_text(strip=True)
                        href = title_link.get("href", "")
                        if href:
                            film_url = urljoin(self.base_url, href)
                except Exception as e:
                    print(f"  Warning: Could not extract title/link for rank {rank}: {e}")

                # Original name from year page
                try:
                    sm_links = info_cell.find_all("span", class_="sm")
                    for span in sm_links:
                        link = span.find("a")
                        if not link:
                            continue
                        name_original = link.get("title", "").strip() or link.get_text(strip=True)
                        if name_original and name_original != name_russian:
                            break
                except Exception:
                    pass

                country = None
                production_year = None
                try:
                    sm_spans = info_cell.find_all("span", class_="sm")
                    for span in sm_spans:
                        if span.find("a"):
                            continue
                        text = span.get_text(strip=True)
                        if text and ("," in text or re.search(r"\d{4}", text)):
                            country, production_year = self.parse_country_and_year(text)
                            break
                except Exception as e:
                    print(f"  Warning: Could not extract country/year for rank {rank}: {e}")

                viewers_text = viewers_cell.get_text(strip=True)
                viewers_total = self.parse_viewers(viewers_text)

                films.append(
                    {
                        "rank": rank,
                        "name_russian": name_russian,
                        "name_original": name_original,
                        "film_url": film_url,
                        "country": country,
                        "production_year": production_year,
                        "soviet_release_year": year,
                        "viewers_total": viewers_total,
                    }
                )
                print(f"  ✓ Rank {rank}: {name_russian} ({viewers_total:,} viewers)")

            print(f"  Found {len(films)} films for year {year}")
            return films
        except Exception as e:
            print(f"  ✗ Error scraping year {year}: {e}")
            return []

    def scrape_years(
        self,
        start_year: int = 1950,
        end_year: int = 1991,
        output_csv: str = "soviet_releases.csv",
        parallel: bool = True,
    ):
        """Scrape multiple years (optionally in parallel)."""
        all_films = []
        years = list(range(start_year, end_year + 1))

        if parallel and len(years) > 1:
            print(f"Scraping {len(years)} years in parallel ({self.max_workers} workers)...")
            completed = 0
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_year = {executor.submit(self.scrape_year_page, y): y for y in years}
                pending = set(future_to_year.keys())
                try:
                    # Use a more reasonable timeout per year (60 seconds per year max)
                    timeout_per_year = 60
                    total_timeout = timeout_per_year * len(years)
                    start_time = time.time()
                    
                    while pending:
                        if time.time() - start_time > total_timeout:
                            print(f"  ⚠ Overall timeout reached ({total_timeout}s), cancelling pending tasks...")
                            break
                        
                        done, not_done = [], []
                        for future in pending:
                            if future.done():
                                done.append(future)
                            else:
                                not_done.append(future)
                        
                        for future in done:
                            pending.remove(future)
                            year = future_to_year[future]
                            completed += 1
                            try:
                                films = future.result(timeout=5)  # Quick result retrieval
                                all_films.extend(films)
                                print(
                                    f"  ✓ Completed {completed}/{len(years)} years "
                                    f"(year {year}: {len(films)} films)"
                                )
                            except Exception as e:
                                print(f"  ✗ Year {year} generated an exception: {e}")
                        
                        # Exit if all done
                        if not pending:
                            break
                        
                        # Brief pause before checking again (only if still pending)
                        time.sleep(1)
                except Exception as e:
                    print(f"  ⚠ Error in parallel processing: {e}")
                finally:
                    # Cancel any remaining pending futures
                    for future in pending:
                        future.cancel()
                    # Collect any remaining completed results
                    for future, year in future_to_year.items():
                        if future.done() and future not in pending:
                            try:
                                films = future.result()
                                if films:
                                    all_films.extend(films)
                            except Exception:
                                pass
        else:
            for year in years:
                films = self.scrape_year_page(year)
                all_films.extend(films)
                time.sleep(self.delay)

        if not all_films:
            print("\n✗ No films found")
            return None

        all_films.sort(
            key=lambda x: (int(x.get("soviet_release_year", 0)), int(x.get("rank", 0)))
        )
        fieldnames = [
            "rank",
            "name_russian",
            "name_original",
            "film_url",
            "country",
            "production_year",
            "soviet_release_year",
            "viewers_total",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_films)
        print(f"\n✓ Saved {len(all_films)} films to {output_csv}")
        return output_csv

    def scrape_film_page(self, film_url: str):
        """Scrape individual film page (requests only, no Selenium fallback to avoid issues)."""
        if not film_url:
            return None

        # Don't print every URL to reduce noise - only print every 10th
        # (We'll track progress separately)
        metadata = {
            "film_url": film_url,
            "name_original": None,
            "country_of_origin": None,
            "short_description": None,
            "production_year": None,
            "kinopoisk_id": None,
        }

        try:
            # Add a small delay to avoid rate limiting
            time.sleep(self.delay)
            response = self.session.get(film_url, timeout=(10, 30))
            response.encoding = "windows-1251"
            response.raise_for_status()

            if "Роботам запрещено" in response.text or "captcha" in response.text.lower():
                raise Exception("Bot detection page received")

            soup = BeautifulSoup(response.text, "lxml")

            param_divs = soup.find_all("div", class_="info_table_param")
            if not param_divs:
                raise Exception("No metadata found, likely bot detection")

            for param_div in param_divs:
                label = param_div.get_text(strip=True)
                data_div = param_div.find_next_sibling("div", class_="info_table_data")
                if not data_div:
                    continue

                value = data_div.get_text(strip=True)
                strong = data_div.find("strong")
                if strong:
                    value = strong.get_text(strip=True)

                if label == "Оригинальное название" and not metadata["name_original"]:
                    metadata["name_original"] = value
                elif label == "Страна" and not metadata["country_of_origin"]:
                    metadata["country_of_origin"] = value
                elif label == "Год" and not metadata["production_year"]:
                    year_match = re.search(r"(\d{4})", value)
                    if year_match:
                        try:
                            metadata["production_year"] = int(year_match.group(1))
                        except ValueError:
                            pass

            desc_elem = soup.find("div", itemprop="description")
            if desc_elem:
                desc = desc_elem.get_text(strip=True)
                if len(desc) > 50:
                    metadata["short_description"] = desc[:500]

            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                if "kinopoisk.ru" in href:
                    match = re.search(r"/(\d+)/", href)
                    if match:
                        metadata["kinopoisk_id"] = match.group(1)
                        break

            # Success - metadata extracted (don't print every one to reduce noise)
            return metadata
        except Exception as e:
            # Don't use Selenium fallback - it causes too many issues with parallel processing
            # Just return what we have (empty metadata is fine)
            if "Bot detection" in str(e) or "captcha" in str(e).lower():
                pass  # Silently skip bot-detected pages
            return metadata

    def scrape_film_metadata(
        self,
        input_csv: str = "soviet_releases.csv",
        output_csv: str = "films_metadata.csv",
        parallel: bool = True,
    ):
        """Scrape metadata for all unique films - can run in parallel."""
        film_urls = set()
        try:
            with open(input_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("film_url")
                    if url:
                        film_urls.add(url)
            print(f"Found {len(film_urls)} unique film URLs")
        except FileNotFoundError:
            print(f"✗ Input CSV {input_csv} not found. Run scrape_years() first.")
            return None

        all_metadata = []
        film_urls_list = list(film_urls)

        if parallel and len(film_urls_list) > 1:
            # Use fewer workers for film pages to avoid bot detection
            film_workers = min(self.max_workers, 2)  # Max 2 workers for film pages
            print(f"Scraping {len(film_urls_list)} films in parallel ({film_workers} workers)...")
            with ThreadPoolExecutor(max_workers=film_workers) as executor:
                future_to_url = {
                    executor.submit(self.scrape_film_page, url): url for url in film_urls_list
                }
                completed = 0
                pending = set(future_to_url.keys())
                start_time = time.time()
                # Max 30 seconds per film, with overall cap
                timeout_per_film = 30
                total_timeout = min(timeout_per_film * len(film_urls_list), 3600)  # Cap at 1 hour
                
                try:
                    while pending:
                        if time.time() - start_time > total_timeout:
                            print(f"  ⚠ Overall timeout reached ({total_timeout}s), cancelling pending tasks...")
                            break
                        
                        done, not_done = [], []
                        for future in pending:
                            if future.done():
                                done.append(future)
                            else:
                                not_done.append(future)
                        
                        for future in done:
                            pending.remove(future)
                            url = future_to_url[future]
                            completed += 1
                            try:
                                metadata = future.result(timeout=5)  # Quick result retrieval
                                if metadata:
                                    all_metadata.append(metadata)
                                # Print progress more frequently
                                if completed % 5 == 0 or completed == len(film_urls_list):
                                    print(
                                        f"  Progress: {completed}/{len(film_urls_list)} films processed "
                                        f"({len(all_metadata)} with metadata)"
                                    )
                            except Exception as e:
                                # Don't print every error - too noisy
                                if completed % 20 == 0:
                                    print(f"  ⚠ Some errors encountered (processed {completed}/{len(film_urls_list)})")
                        
                        # Exit if all done
                        if not pending:
                            break
                        
                        # Brief pause before checking again (only if still pending)
                        time.sleep(1)
                except Exception as e:
                    print(f"  ⚠ Error in parallel processing: {e}")
                finally:
                    # Cancel any remaining pending futures
                    for future in pending:
                        future.cancel()
                    # Collect any remaining completed results
                    for future, url in future_to_url.items():
                        if future.done() and future not in pending:
                            try:
                                metadata = future.result()
                                if metadata:
                                    all_metadata.append(metadata)
                            except Exception:
                                pass
        else:
            for i, film_url in enumerate(film_urls_list, 1):
                print(f"[{i}/{len(film_urls_list)}] ", end="")
                metadata = self.scrape_film_page(film_url)
                if metadata:
                    all_metadata.append(metadata)
                time.sleep(self.delay)

        if not all_metadata:
            print("\n✗ No metadata found")
            return None

        fieldnames = [
            "film_url",
            "name_original",
            "country_of_origin",
            "short_description",
            "production_year",
            "kinopoisk_id",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_metadata)

        print(f"\n✓ Saved metadata for {len(all_metadata)} films to {output_csv}")
        return output_csv

    def merge_data(
        self,
        releases_csv: str = "soviet_releases.csv",
        metadata_csv: str = "films_metadata.csv",
        output_csv: str = "soviet_films_complete.csv",
    ):
        """Reuse Selenium scraper's merge logic for consistency."""
        temp_scraper = KinoTeatrScraper()
        return temp_scraper.merge_data(releases_csv, metadata_csv, output_csv)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape kino-teatr.ru for Soviet film data")
    parser.add_argument("--start-year", type=int, default=1950, help="Start year (default: 1950)")
    parser.add_argument("--end-year", type=int, default=1991, help="End year (default: 1991)")
    parser.add_argument(
        "--step",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which step to run: 1=year pages, 2=film metadata, 3=merge, all=all steps",
    )
    parser.add_argument(
        "--delay", type=float, default=2.0, help="Delay between requests in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Page load timeout in seconds (Selenium, default: 180)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Max retries for failed Selenium requests (default: 3)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (Selenium)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Show browser window (Selenium)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        default=True,
        help="Use fast scraper (requests+BeautifulSoup) - 10-100x faster (default: True)",
    )
    parser.add_argument(
        "--no-fast",
        dest="fast",
        action="store_false",
        help="Use Selenium scraper (slower but more reliable)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Max parallel workers for fast scraper (default: 5)",
    )

    args = parser.parse_args()

    # Choose implementation
    if args.fast:
        scraper = FastKinoTeatrScraper(delay=args.delay, max_workers=args.max_workers)
    else:
        scraper = KinoTeatrScraper(
            headless=args.headless,
            delay=args.delay,
            timeout=args.timeout,
            max_retries=args.max_retries,
        )

    releases_csv = f"soviet_releases_{args.start_year}_{args.end_year}.csv"
    metadata_csv = f"films_metadata_{args.start_year}_{args.end_year}.csv"
    complete_csv = f"soviet_films_complete_{args.start_year}_{args.end_year}.csv"

    try:
        if args.step in ["1", "all"]:
            print("=" * 60)
            print("STEP 1: Scraping year pages")
            print("=" * 60)
            scraper.scrape_years(start_year=args.start_year, end_year=args.end_year, output_csv=releases_csv)

        if args.step in ["2", "all"]:
            print("\n" + "=" * 60)
            print("STEP 2: Scraping film metadata")
            print("=" * 60)
            scraper.scrape_film_metadata(input_csv=releases_csv, output_csv=metadata_csv)

        if args.step in ["3", "all"]:
            print("\n" + "=" * 60)
            print("STEP 3: Merging data and calculating box office")
            print("=" * 60)
            scraper.merge_data(releases_csv=releases_csv, metadata_csv=metadata_csv, output_csv=complete_csv)

        print("\n" + "=" * 60)
        print("✓ Scraping complete!")
        print("=" * 60)
        print("Output files:")
        print(f"  - Year data: {releases_csv}")
        if args.step in ["2", "all"]:
            print(f"  - Film metadata: {metadata_csv}")
        if args.step in ["3", "all"]:
            print(f"  - Complete data: {complete_csv}")

    except KeyboardInterrupt:
        print("\n\n✗ Scraping interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
