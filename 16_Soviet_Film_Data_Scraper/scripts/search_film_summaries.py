"""
Web search module to find film summaries from anywhere on the internet.
Uses general web search to find summaries from any website, not just hardcoded sources.
"""
import csv
import re
import time
import urllib.parse
from typing import Dict, Optional, List, Set

import requests
from bs4 import BeautifulSoup

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    _GoogleTranslator = GoogleTranslator  # Keep reference for use in methods
except ImportError:
    TRANSLATOR_AVAILABLE = False
    _GoogleTranslator = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class WebFilmSummarySearcher:
    """Search the entire web for film summaries from any source."""
    
    def __init__(self, delay: float = 1.0, max_results: int = 15):
        self.delay = delay
        self.max_results = max_results  # Get more results per search
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        # Only skip truly non-content domains (social media, shopping, etc.)
        # Keep it minimal - we want to search the ENTIRE web
        self.skip_domains = {
            'facebook.com', 'twitter.com', 'instagram.com', 
            'pinterest.com', 'linkedin.com', 'tumblr.com',
            'amazon.com', 'ebay.com', 'etsy.com',
            # Allow YouTube, Reddit - they might have film reviews/summaries
        }
        # Initialize translator if available
        self.translator_available = TRANSLATOR_AVAILABLE
        self.gemini_available = GEMINI_AVAILABLE
        self.gemini_model = None
        self.selenium_available = SELENIUM_AVAILABLE
        self.driver = None
        
        # Try to initialize Gemini if available and API key is set
        if self.gemini_available:
            try:
                import os
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                else:
                    self.gemini_available = False
            except:
                self.gemini_available = False
    
    def setup_selenium_driver(self):
        """Setup Selenium driver for fallback search."""
        if not self.selenium_available or self.driver:
            return
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            self.selenium_available = False
    
    def cleanup_selenium(self):
        """Clean up Selenium driver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def translate_to_english(self, text: str) -> str:
        """Translate text to English if it's in another language."""
        if not self.translator_available or not text:
            return text
        
        try:
            # Simple check: if text contains Cyrillic, it's likely Russian
            has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in text)
            
            if has_cyrillic:
                # Translate from Russian to English - MUST translate with retries
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        if attempt > 0:
                            time.sleep(2 * attempt)  # Progressive delay: 2s, 4s
                        
                        from deep_translator import GoogleTranslator
                        # Try explicit Russian->English first
                        translator = GoogleTranslator(source='ru', target='en')
                        chunk = text[:4000] if len(text) > 4000 else text
                        translated = translator.translate(chunk)
                        
                        if translated and translated.strip():
                            # Verify it's actually translated (doesn't contain Cyrillic)
                            translated_has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in translated)
                            if not translated_has_cyrillic:
                                return translated
                        
                        # If still has Cyrillic, try auto-detect
                        if attempt < max_attempts - 1:
                            time.sleep(1)
                            translator = GoogleTranslator(source='auto', target='en')
                            translated = translator.translate(chunk)
                            if translated and translated.strip():
                                translated_has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in translated)
                                if not translated_has_cyrillic:
                                    return translated
                    except Exception as e:
                        if attempt < max_attempts - 1:
                            time.sleep(2 * (attempt + 1))  # Wait before retry
                            continue
                        # Last attempt failed - try one more time with smaller chunk
                        if attempt == max_attempts - 1:
                            try:
                                time.sleep(3)
                                from deep_translator import GoogleTranslator
                                translator = GoogleTranslator(source='ru', target='en')
                                # Try even smaller chunk
                                small_chunk = text[:2000] if len(text) > 2000 else text
                                translated = translator.translate(small_chunk)
                                if translated and translated.strip():
                                    translated_has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in translated)
                                    if not translated_has_cyrillic:
                                        return translated
                            except:
                                pass
                
                # All attempts failed - print warning and return original
                print(f"        → Warning: Could not translate summary to English")
                return text
            else:
                # Already English or other language - try auto-detect if needed
                try:
                    from deep_translator import GoogleTranslator
                    translated = GoogleTranslator(source='auto', target='en').translate(text[:5000])
                    # Only use translation if it's different (was actually translated)
                    if translated and translated.lower() != text.lower():
                        return translated
                except:
                    pass
            
            return text  # Return original if translation fails or not needed
        except Exception as e:
            print(f"        → Translation error: {str(e)[:50]}")
            return text  # Return original if translation fails
    
    def condense_summary(self, text: str) -> str:
        """Condense summary to max 2 sentences if it exceeds that."""
        if not text:
            return text
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # If already 2 sentences or less, return as is
        if len(sentences) <= 2:
            return text
        
        # Take first 2 substantial sentences
        condensed = []
        for sentence in sentences:
            if len(sentence) > 30:  # Only substantial sentences
                condensed.append(sentence)
                if len(condensed) >= 2:
                    break
        
        if condensed:
            result = '. '.join(condensed)
            if result and not result.endswith(('.', '!', '?')):
                result += '.'
            return result
        
        # Fallback: return original if we can't condense properly
        return text

    def extract_text_from_page(self, html_content: str, url: str) -> Optional[str]:
        """Extract meaningful text/summary from any webpage, with special handling for Wikipedia."""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # SPECIAL HANDLING FOR WIKIPEDIA
            is_wikipedia = 'wikipedia.org' in url.lower()
            if is_wikipedia:
                # Find the main content div
                main_content = soup.find('div', {'id': 'mw-content-text'}) or soup.find('div', class_='mw-parser-output')
                if main_content:
                    # Look for Plot/Сюжет section specifically
                    plot_section = None
                    
                    # Find all headings (h2, h3, h4) and look for Plot section
                    headings = main_content.find_all(['h2', 'h3', 'h4'])
                    for heading in headings:
                        heading_text = heading.get_text().strip().lower()
                        # Check for plot keywords in multiple languages
                        plot_keywords = ['plot', 'сюжет', 'story', 'synopsis', 'summary', 
                                       'описание', 'содержание', 'storyline']
                        if any(keyword in heading_text for keyword in plot_keywords):
                            # Found plot section - extract all following paragraphs
                            # Use a different approach: find all elements after this heading until next h2
                            plot_section = []
                            heading_level = int(heading.name[1]) if heading.name.startswith('h') else 999
                            
                            # Find all elements in main_content, get those after plot heading
                            all_elems = main_content.find_all(['h2', 'h3', 'h4', 'p', 'div', 'ul'])
                            found_heading = False
                            
                            for elem in all_elems:
                                if elem == heading:
                                    found_heading = True
                                    continue
                                
                                if not found_heading:
                                    continue
                                
                                # Stop at next heading of same or higher level
                                if elem.name and elem.name.startswith('h'):
                                    elem_level = int(elem.name[1])
                                    if elem_level <= heading_level:
                                        break
                                
                                # Extract text from paragraphs and divs
                                if elem.name == 'p':
                                    text = elem.get_text().strip()
                                    # Skip warning messages
                                    if any(warn in text.lower() for warn in [
                                        'нет полного описания', 'полное описание сюжета',
                                        'в этой статье нет', 'you can help', 'пожалуйста, пишите текст',
                                        'please write the text yourself'
                                    ]):
                                        continue
                                    
                                    text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
                                    text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
                                    text = re.sub(r'\[.*?\]', '', text)
                                    text = re.sub(r'\s+', ' ', text).strip()
                                    
                                    if len(text) > 50:
                                        plot_section.append(text)
                                
                                # Also check divs for paragraphs (nested structure)
                                elif elem.name == 'div':
                                    # Skip template/warning boxes
                                    div_class = str(elem.get('class', [])).lower()
                                    if any(skip in div_class for skip in ['ambox', 'hatnote', 'thumb', 'infobox', 'navbox']):
                                        continue
                                    
                                    # Get paragraphs inside div
                                    div_paragraphs = elem.find_all('p')
                                    for p in div_paragraphs:
                                        text = p.get_text().strip()
                                        if any(warn in text.lower() for warn in [
                                            'нет полного описания', 'полное описание сюжета'
                                        ]):
                                            continue
                                        
                                        text = re.sub(r'\[.*?\]', '', text)
                                        text = re.sub(r'\s+', ' ', text).strip()
                                        
                                        if len(text) > 50:
                                            plot_section.append(text)
                                
                                # Limit
                                if len(plot_section) >= 10:
                                    break
                            
                            if plot_section:
                                combined = ' '.join(plot_section)
                                # Get full plot, translate if needed
                                if len(combined) > 150:
                                    # Translate to English if needed
                                    combined = self.translate_to_english(combined)
                                    return combined
                                elif len(combined) > 50:
                                    # Even if short, translate and return it
                                    combined = self.translate_to_english(combined)
                                    return combined
                    
                    # If no plot section found, get first few substantial paragraphs
                    paragraphs = main_content.find_all('p')
                    text_parts = []
                    for p in paragraphs[:8]:  # First 8 paragraphs
                        text = p.get_text().strip()
                        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
                        text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
                        text = re.sub(r'\[.*?\]', '', text)  # Remove citations
                        text = re.sub(r'\s+', ' ', text).strip()
                        if len(text) > 150:  # Substantial paragraphs
                            text_parts.append(text)
                    
                    if text_parts:
                        combined = ' '.join(text_parts[:3])
                        if len(combined) > 150:
                            # Translate to English if needed
                            combined = self.translate_to_english(combined)
                            return combined
            
            # SPECIAL HANDLING FOR IMDb
            is_imdb = 'imdb.com' in url.lower()
            if is_imdb:
                # IMDb has specific structure for plot summaries
                # Look for plot section
                plot_section = soup.find('section', {'data-testid': 'Storyline'}) or \
                              soup.find('div', {'class': re.compile('plot', re.I)}) or \
                              soup.find('div', {'class': re.compile('summary_text', re.I)})
                
                if plot_section:
                    # Find plot text
                    plot_text = plot_section.find('span', {'class': re.compile('plot|summary', re.I)}) or \
                               plot_section.find('div', {'class': re.compile('plot|summary', re.I)})
                    
                    if plot_text:
                        text = plot_text.get_text().strip()
                        text = re.sub(r'\s+', ' ', text).strip()
                        if len(text) > 100:
                            text = self.translate_to_english(text)
                            condensed = self.condense_summary(text)
                            return condensed if condensed else text[:2000]
                
                # Try alternative: look for description in page
                desc = soup.find('span', {'data-testid': 'plot-xl'}) or \
                       soup.find('span', {'data-testid': 'plot-l'}) or \
                       soup.find('div', {'data-testid': 'plot'})
                if desc:
                    text = desc.get_text().strip()
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 100:
                        text = self.translate_to_english(text)
                        condensed = self.condense_summary(text)
                        return condensed if condensed else text[:2000]
            
            # SPECIAL HANDLING FOR KINOPOISK
            is_kinopoisk = 'kinopoisk.ru' in url.lower() or 'kinopoisk.com' in url.lower()
            if is_kinopoisk:
                # Kinopoisk has specific structure for synopsis
                # Try multiple approaches to find the synopsis text
                
                # Method 1: Try data attributes and common class patterns
                synopsis_selectors = [
                    '[data-test-id="synopsis"]',
                    '[data-testid="synopsis"]',
                    '[class*="synopsis"]',
                    '[class*="Synopsis"]',
                    '[class*="описание"]',
                    '[class*="сюжет"]',
                    '.film-synopsis',
                    '.movie-synopsis',
                    '[itemprop="description"]',
                ]
                
                for selector in synopsis_selectors:
                    try:
                        synopsis = soup.select_one(selector)
                        if synopsis:
                            text = synopsis.get_text().strip()
                            text = re.sub(r'\s+', ' ', text).strip()
                            if len(text) > 100:
                                text = self.translate_to_english(text)
                                condensed = self.condense_summary(text)
                                return condensed if condensed else text[:2000]
                    except:
                        continue
                
                # Method 2: Search for text blocks that start with years (common in synopses)
                # Like "1893. Edith..." - look for patterns starting with 4-digit years
                all_text = soup.get_text()
                # Find text blocks that start with years and are substantial
                year_pattern = r'(\d{4})[\.\s].{200,}'
                matches = re.finditer(year_pattern, all_text)
                for match in matches:
                    text = match.group(0).strip()
                    # Check if it looks like a plot (contains names, actions, etc.)
                    if len(text) > 200 and any(kw in text.lower() for kw in 
                        ['saved', 'rescued', 'prisoner', 'embassy', 'fate', 'escape',
                         'спасает', 'узник', 'посольство', 'судьба', 'побег']):
                        # Extract first few sentences
                        sentences = re.split(r'[.!?]+', text)
                        plot_text = '. '.join([s.strip() for s in sentences[:3] if len(s.strip()) > 30])
                        if len(plot_text) > 100:
                            text = self.translate_to_english(plot_text)
                            condensed = self.condense_summary(text)
                            return condensed if condensed else text[:2000]
                
                # Method 3: Find all text blocks and look for plot-like content
                desc_divs = soup.find_all(['div', 'p', 'span'])
                for div in desc_divs:
                    text = div.get_text().strip()
                    # Look for substantial text that contains plot indicators
                    if len(text) > 200:
                        # Skip metadata
                        if any(meta in text.lower() for meta in ['год:', 'year:', 'режиссёр:', 'director:', 
                                                                 'жанр:', 'genre:', 'рейтинг', 'rating']):
                            continue
                        # Check for plot indicators
                        plot_indicators = ['prisoner', 'saved', 'rescue', 'escape', 'mission', 'daughter',
                                          'узник', 'спасает', 'побег', 'миссия', 'дочь', 'происходит']
                        if any(ind in text.lower() for ind in plot_indicators):
                            # Also check it starts with context (year, name, etc.)
                            first_words = text[:50].lower()
                            if any(start in first_words for start in ['18', '19', '20', 'edith', 'kalin']):
                                text = re.sub(r'\s+', ' ', text).strip()
                                text = self.translate_to_english(text)
                                condensed = self.condense_summary(text)
                                return condensed if condensed else text[:2000]
            
            # GENERAL WEB PAGE EXTRACTION
            # Try to find main content area
            main_selectors = [
                '.mw-parser-output',  # Wikipedia fallback
                'main', 'article', '[role="main"]',
                '.content', '.main-content', '.post-content',
                '.entry-content', '.article-content', '.story-body',
                '#content', '#main', '#article',
                '.film-details', '.movie-details',  # Common movie site patterns
                '[class*="film"]', '[class*="movie"]',
            ]
            
            main_content = None
            for selector in main_selectors:
                try:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                except:
                    continue
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract all paragraphs and text blocks
            paragraphs = main_content.find_all(['p', 'div'])
            text_parts = []
            
            for elem in paragraphs:
                text = elem.get_text().strip()
                # Look for substantial text blocks (likely summaries/descriptions)
                if len(text) > 150:
                    # Skip metadata/navigation text
                    if any(skip in text.lower() for skip in ['login', 'register', 'subscribe', 'cookie', 
                                                             'privacy policy', 'terms of service',
                                                             'вход', 'регистрация', 'подписка']):
                        continue
                    
                    # Clean up text - be more careful with citations
                    text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    # Check if it looks like a plot summary (multi-language)
                    plot_keywords = ['plot', 'story', 'summary', 'synopsis', 'about', 
                                   'follows', 'tells', 'chronicles', 'revolves',
                                   'сюжет', 'описание', 'фильм', 'movie', 'film',
                                   'происходит', 'рассказывает', 'действие']
                    text_lower = text.lower()[:300]
                    if any(keyword in text_lower for keyword in plot_keywords):
                        text_parts.append(text)
                    elif len(text) > 250:  # Long paragraphs are often summaries
                        text_parts.append(text)
            
            # Combine and return best summary
            if text_parts:
                # Sort by length (longer is usually better for summaries)
                text_parts.sort(key=len, reverse=True)
                combined = ' '.join(text_parts[:3])  # Take top 3 paragraphs
                # Limit to reasonable length
                if len(combined) > 150:
                    # Translate to English if needed
                    combined = self.translate_to_english(combined)
                    # Condense only if more than 2 sentences
                    combined = self.condense_summary(combined)
                    return combined
                return combined
                
        except Exception as e:
            pass
        return None

    def get_search_results(self, query: str) -> List[Dict[str, str]]:
        """Get search results from DuckDuckGo - try requests first, fallback to Selenium."""
        results = []
        
        # Try requests-based search first
        try:
            search_url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            
            time.sleep(self.delay)
            response = self.session.post(search_url, data=params, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                'Referer': 'https://www.google.com/',
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Try multiple selectors - DuckDuckGo HTML format may vary
                result_divs = (soup.find_all('div', class_='result') or 
                             soup.find_all('div', class_='web-result') or 
                             soup.find_all('div', {'class': re.compile('result', re.I)}))
                
                if not result_divs:
                    # Try alternative structure
                    result_divs = soup.find_all('div', {'class': re.compile('web-result|result', re.I)})
                
                for result_div in result_divs[:self.max_results]:
                    try:
                        # Try multiple link selectors
                        link_elem = (result_div.find('a', class_='result__a') or 
                                   result_div.find('a', class_='result-link') or
                                   result_div.find('a', href=re.compile('http')) or
                                   result_div.find('a'))
                        
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href', '')
                            title = link_elem.get_text().strip()
                            
                            # Try to find snippet
                            snippet_elem = (result_div.find('a', class_='result__snippet') or
                                          result_div.find('div', class_='result__snippet') or
                                          result_div.find('span', class_='result__snippet') or
                                          result_div.find('div', {'class': re.compile('snippet', re.I)}))
                            snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                            
                            # Extract actual URL (DuckDuckGo wraps URLs)
                            if href.startswith('/l/?kh=-1&uddg=') or '/l/?uddg=' in href or '/l/?' in href:
                                try:
                                    if 'uddg=' in href:
                                        href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                                except:
                                    pass
                            
                            if not href.startswith('http'):
                                continue
                            
                            # Skip unwanted domains
                            domain = urllib.parse.urlparse(href).netloc.lower()
                            if any(skip in domain for skip in self.skip_domains):
                                continue
                            
                            results.append({
                                'title': title,
                                'url': href,
                                'snippet': snippet,
                                'domain': domain
                            })
                    except Exception as e:
                        continue
                
                if results:
                    return results
        except Exception as e:
            pass
        
        # If requests failed, try Selenium fallback
        if not results and self.selenium_available:
            try:
                print(f"        → Requests failed, trying Selenium fallback...")
                self.setup_selenium_driver()
                
                if self.driver:
                    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                    self.driver.get(search_url)
                    time.sleep(2)  # Wait for page to load
                    
                    # Get page source and parse
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'lxml')
                    
                    # Parse results the same way
                    result_divs = (soup.find_all('div', class_='result') or 
                                 soup.find_all('div', class_='web-result') or 
                                 soup.find_all('div', {'class': re.compile('result', re.I)}))
                    
                    for result_div in result_divs[:self.max_results]:
                        try:
                            link_elem = (result_div.find('a', class_='result__a') or 
                                       result_div.find('a', class_='result-link') or
                                       result_div.find('a', href=re.compile('http')) or
                                       result_div.find('a'))
                            
                            if link_elem and link_elem.get('href'):
                                href = link_elem.get('href', '')
                                title = link_elem.get_text().strip()
                                
                                snippet_elem = (result_div.find('a', class_='result__snippet') or
                                              result_div.find('div', class_='result__snippet') or
                                              result_div.find('span', class_='result__snippet') or
                                              result_div.find('div', {'class': re.compile('snippet', re.I)}))
                                snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                                
                                # Extract actual URL (DuckDuckGo wraps URLs)
                                if href.startswith('/l/?kh=-1&uddg=') or '/l/?uddg=' in href or '/l/?' in href:
                                    try:
                                        if 'uddg=' in href:
                                            href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                                    except:
                                        pass
                                
                                if not href.startswith('http'):
                                    continue
                                
                                domain = urllib.parse.urlparse(href).netloc.lower()
                                if any(skip in domain for skip in self.skip_domains):
                                    continue
                                
                                results.append({
                                    'title': title,
                                    'url': href,
                                    'snippet': snippet,
                                    'domain': domain
                                })
                        except:
                            continue
            except Exception as e:
                pass
        
        return results

    def try_direct_wikipedia(self, film_name: str, name_original: Optional[str] = None, year: Optional[int] = None) -> Optional[str]:
        """Try to access Wikipedia directly by constructing URL with multiple variations."""
        urls_to_try = []
        
        # Construct Wikipedia URLs with various formats
        # Russian Wikipedia variations (most likely for Soviet films)
        base_name = film_name.replace(' ', '_')
        
        # Prioritize URLs with "_(фильм)" suffix first - these are more likely to be film pages
        # Try: "Film Name (фильм)" first, then other variations
        urls_to_try.append(f'https://ru.wikipedia.org/wiki/{urllib.parse.quote(base_name + "_(фильм)")}')
        urls_to_try.append(f'https://ru.wikipedia.org/wiki/{urllib.parse.quote(base_name + "_(film)")}')
        # Try base name last (might redirect to disambiguation or wrong page)
        urls_to_try.append(f'https://ru.wikipedia.org/wiki/{urllib.parse.quote(base_name)}')
        
        # If year is available, try with year variations
        if year:
            urls_to_try.append(f'https://ru.wikipedia.org/wiki/{urllib.parse.quote(base_name + f"_(фильм,_{year})")}')
            urls_to_try.append(f'https://ru.wikipedia.org/wiki/{urllib.parse.quote(base_name + f"_(film,_{year})")}')
        
        # If we have original name, try English Wikipedia too
        if name_original:
            orig_base = name_original.replace(' ', '_')
            urls_to_try.append(f'https://en.wikipedia.org/wiki/{urllib.parse.quote(orig_base)}')
            urls_to_try.append(f'https://en.wikipedia.org/wiki/{urllib.parse.quote(orig_base + "_(film)")}')
            if year:
                urls_to_try.append(f'https://en.wikipedia.org/wiki/{urllib.parse.quote(orig_base + f"_(film,_{year})")}')
        
        for url in urls_to_try:
            try:
                time.sleep(self.delay * 0.5)  # Faster since we're trying multiple URLs
                response = self.session.get(url, timeout=15, allow_redirects=True, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                    'Referer': 'https://www.google.com/',
                })
                
                if response.status_code == 200:
                    summary = self.extract_text_from_page(response.text, url)
                    if summary and len(summary) > 100:
                        return summary
            except:
                continue
        
        return None
    
    def try_gemini_summary(self, film_name: str, year: Optional[int] = None, 
                          name_original: Optional[str] = None) -> Optional[str]:
        """Try to get summary from Gemini AI if available."""
        if not self.gemini_model:
            return None
        
        try:
            # Construct prompt
            name_part = name_original if name_original else film_name
            year_part = f" from {year}" if year else ""
            prompt = f"Provide a brief 1-2 sentence plot summary of the film '{name_part}'{year_part}. " \
                    f"If the film is '{film_name}' in Russian, provide the summary in English. " \
                    f"Only provide factual plot information, no commentary."
            
            response = self.gemini_model.generate_content(prompt)
            summary = response.text.strip()
            
            if summary and len(summary) > 50:
                # Condense if needed
                condensed = self.condense_summary(summary)
                return condensed if condensed else summary[:500]
        except Exception as e:
            pass
        
        return None
    
    def search_web_general(self, film_name: str, year: Optional[int] = None, 
                          name_original: Optional[str] = None) -> Optional[str]:
        """
        Process: Search by title → Wikipedia if available → Visit search results in order.
        Extract summaries and condense to 1-3 sentences if needed.
        """
        # Step 1: Try direct Wikipedia access first
        print(f"    Searching for Wikipedia page...")
        summary = self.try_direct_wikipedia(film_name, name_original, year)
        if summary:
            # Condense to 1-3 sentences if longer
            sentences = re.split(r'[.!?]+', summary)
            if len(sentences) > 3:
                print(f"    → Summary is {len(sentences)} sentences, condensing to 1-3...")
                condensed = self.condense_summary(summary)
                if condensed:
                    summary = condensed
            print(f"    ✓ Found summary from Wikipedia (direct)")
            return summary
        
        # Step 2: Wikipedia not found - search web by title
        # Build search queries using just the film title (no extra words)
        queries = []
        if name_original:
            queries.append(f'"{name_original}"')
        queries.append(f'"{film_name}"')
        
        # Remove duplicates
        seen = set()
        queries = [q for q in queries if q and not (q in seen or seen.add(q))]
        
        visited_urls: Set[str] = set()
        found_summary = None
        
        # Try each query (usually just 1-2 queries)
        requests_failed = False
        for query in queries:
            print(f"    Searching: {query}")
            results = self.get_search_results(query)
            
            print(f"      → Found {len(results)} search results")
            
            if not results:
                requests_failed = True
                print(f"      → No search results returned")
                # Will try Selenium fallback after all queries
                continue
            
            # Show search results
            print(f"      → Found {len(results)} search results")
            print(f"      → Will visit links in order to extract summaries...")
            
            # Visit all results in order (up to 10 sites)
            for idx, result in enumerate(results[:10], 1):
                url = result['url']
                
                if url in visited_urls:
                    continue
                visited_urls.add(url)
                
                # Skip obvious non-content pages
                if any(skip in url.lower() for skip in ['/search', '/login', '/register', 
                                                         '/cart', '/checkout', '.pdf', 
                                                         '.zip', '.exe', '/tag/', '/category/',
                                                         'youtube.com/watch']):
                    continue
                
                print(f"      [{idx}/10] Checking: {result['domain']}")
                
                try:
                    time.sleep(self.delay)
                    response = self.session.get(url, timeout=15, allow_redirects=True, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Referer': 'https://www.google.com/',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                    })
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'text/html' not in content_type:
                            continue
                        
                        summary = self.extract_text_from_page(response.text, url)
                        
                        if summary:
                            # Condense to 1-3 sentences if longer
                            sentences = re.split(r'[.!?]+', summary.strip())
                            sentence_count = len([s for s in sentences if s.strip()])
                            if sentence_count > 3:
                                condensed = self.condense_summary(summary)
                                if condensed:
                                    summary = condensed
                            
                            if len(summary) > 100:
                                print(f"    ✓ Found summary from {result['domain']}")
                                found_summary = summary
                                break  # Found summary, exit query loop
                            
                except Exception as e:
                    continue
            
            # If found summary from this query, return it
            if found_summary:
                return found_summary
        
        # If all searches failed, try Selenium fallback, then direct database access
        if requests_failed and self.selenium_available and queries:
            print(f"    Trying Selenium fallback for search...")
            try:
                self.setup_selenium_driver()
                if self.driver:
                    query = queries[0]
                    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                    self.driver.get(search_url)
                    time.sleep(3)
                    
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'lxml')
                    result_divs = (soup.find_all('div', class_='result') or 
                                 soup.find_all('div', {'class': re.compile('result', re.I)}))
                    
                    selenium_results = []
                    for result_div in result_divs[:self.max_results]:
                        try:
                            link_elem = result_div.find('a', class_='result__a') or result_div.find('a', href=re.compile('http'))
                            if link_elem and link_elem.get('href'):
                                href = link_elem.get('href', '')
                                if '/l/?uddg=' in href:
                                    href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                                if href.startswith('http'):
                                    domain = urllib.parse.urlparse(href).netloc.lower()
                                    if not any(skip in domain for skip in self.skip_domains):
                                        selenium_results.append({
                                            'title': link_elem.get_text().strip(),
                                            'url': href,
                                            'snippet': '',
                                            'domain': domain
                                        })
                        except:
                            continue
                    
                    if selenium_results:
                        print(f"      → Selenium found {len(selenium_results)} results")
                        # Use these results - continue with normal visiting logic
                        for idx, result in enumerate(selenium_results[:10], 1):
                            url = result['url']
                            if url in visited_urls:
                                continue
                            visited_urls.add(url)
                            
                            print(f"      [{idx}/10] Checking: {result['domain']}")
                            try:
                                time.sleep(self.delay)
                                response = self.session.get(url, timeout=15, headers={
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                                    'Referer': 'https://www.google.com/',
                                })
                                if response.status_code == 200:
                                    summary = self.extract_text_from_page(response.text, url)
                                    if summary:
                                        # Check for bot messages FIRST
                                        summary_lower = summary.lower()
                                        bot_indicators = [
                                            'please confirm', 'you are not a robot', 'captcha',
                                            'verify you are human', 'automated requests',
                                            'we\'re sorry, but it looks like requests',
                                            'after checkbox', 'bot detected', 'access denied'
                                        ]
                                        if any(bot in summary_lower[:500] for bot in bot_indicators):
                                            continue  # Skip bot messages
                                        
                                        # Condense to 1-3 sentences if longer
                                        sentences = re.split(r'[.!?]+', summary.strip())
                                        sentence_count = len([s for s in sentences if s.strip()])
                                        if sentence_count > 3:
                                            condensed = self.condense_summary(summary)
                                            if condensed:
                                                summary = condensed
                                        if len(summary) > 100:
                                            print(f"    ✓ Found summary from {result['domain']} (via Selenium)")
                                            return summary
                            except:
                                continue
            except Exception as e:
                print(f"      → Selenium error: {str(e)[:50]}")
        
        # Final fallback: Direct database access
        print(f"    Trying direct film database access...")
        
        # Construct and try direct URLs to film databases
        urls_to_try = []
        
        # Try IMDb - use search URL with year to get more accurate results
        if name_original:
            if year:
                imdb_search = f"https://www.imdb.com/find/?q={urllib.parse.quote(name_original + ' ' + str(year))}&s=tt&ttype=ft"
            else:
                imdb_search = f"https://www.imdb.com/find/?q={urllib.parse.quote(name_original)}&s=tt&ttype=ft"
            urls_to_try.append(('IMDb', imdb_search, True))
        
        # Try Kinopoisk search (Russian film database)
        kinopoisk_search = f"https://www.kinopoisk.ru/index.php?kp_query={urllib.parse.quote(film_name)}"
        urls_to_try.append(('Kinopoisk', kinopoisk_search, True))
        
        for site_name, url, is_search_page in urls_to_try:
            try:
                print(f"      Trying {site_name}...")
                time.sleep(self.delay)
                response = self.session.get(url, timeout=10, allow_redirects=True, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                    'Referer': 'https://www.google.com/',
                })
                
                if response.status_code == 200:
                    if is_search_page:
                        # Extract film links from search results page
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        # Find film page links - patterns vary by site
                        film_link_patterns = [
                            r'/film/\d+/',  # Kinopoisk: /film/123456/
                            r'/title/tt\d+/',  # IMDb: /title/tt123456/
                            r'/movie/\d+/',  # Other sites
                        ]
                        
                        for pattern in film_link_patterns:
                            links = soup.find_all('a', href=re.compile(pattern))
                            for link in links[:3]:  # Try first 3 results
                                href = link.get('href', '')
                                if not href.startswith('http'):
                                    from urllib.parse import urljoin
                                    href = urljoin(url, href)
                                
                                if href in visited_urls:
                                    continue
                                visited_urls.add(href)
                                
                                try:
                                    print(f"        Checking: {href[:80]}")
                                    time.sleep(self.delay * 0.5)
                                    film_response = self.session.get(href, timeout=10)
                                    if film_response.status_code == 200:
                                        film_summary = self.extract_text_from_page(film_response.text, href)
                                        if film_summary and len(film_summary) > 100:
                                            # Check for bot messages - reject them immediately
                                            summary_lower = film_summary.lower()
                                            bot_indicators = [
                                                'please confirm', 'you are not a robot', 'captcha',
                                                'verify you are human', 'automated requests',
                                                'we\'re sorry, but it looks like requests',
                                                'after checkbox', 'bot detected', 'access denied'
                                            ]
                                            if any(bot in summary_lower[:500] for bot in bot_indicators):
                                                continue  # Skip bot messages
                                            print(f"    ✓ Found summary from {site_name}")
                                            return film_summary
                                except:
                                    continue
                    else:
                        # Direct film page
                        summary = self.extract_text_from_page(response.text, url)
                        if summary and len(summary) > 100:
                            # Check for bot messages - reject them immediately
                            summary_lower = summary.lower()
                            bot_indicators = [
                                'please confirm', 'you are not a robot', 'captcha',
                                'verify you are human', 'automated requests',
                                'we\'re sorry, but it looks like requests',
                                'after checkbox', 'bot detected', 'access denied'
                            ]
                            if any(bot in summary_lower[:500] for bot in bot_indicators):
                                continue  # Skip bot messages
                            print(f"    ✓ Found summary from {site_name}")
                            return summary
            except Exception as e:
                continue
        
        # Final fallback: Gemini
        print(f"    Trying Gemini AI as final fallback...")
        gemini_summary = self.try_gemini_summary(film_name, year, name_original)
        if gemini_summary:
            print(f"    ✓ Found summary from Gemini")
            return gemini_summary
        
        return None

    def find_summary(self, film_name: str, year: Optional[int] = None, 
                     name_original: Optional[str] = None) -> Optional[str]:
        """
        Search the entire web for film summary from any source.
        Uses general web search to find summaries from anywhere on the internet.
        """
        # Use general web search that searches the entire internet
        summary = self.search_web_general(film_name, year, name_original)
        return summary

    def add_summaries_to_csv(self, input_csv: str, output_csv: Optional[str] = None,
                             start_idx: int = 0, max_films: Optional[int] = None):
        """
        Add summaries from web search to CSV file.
        PRESERVES existing summaries - reads from output_csv if it exists to maintain progress.
        """
        if output_csv is None:
            output_csv = input_csv.replace('.csv', '_with_summaries.csv')
        
        # IMPORTANT: Read from output_csv if it exists to preserve existing summaries
        # Otherwise, read from input_csv to create new file
        import os
        if os.path.exists(output_csv):
            print(f"Reading existing {output_csv} to preserve existing summaries...")
            source_file = output_csv
        else:
            print(f"Reading {input_csv} (creating new output file)...")
            source_file = input_csv
        
        rows = []
        with open(source_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            
            # Add summary column if not exists
            if 'web_summary' not in fieldnames:
                fieldnames.append('web_summary')
            
            for row in reader:
                # Ensure web_summary column exists
                if 'web_summary' not in row:
                    row['web_summary'] = ''
                rows.append(row)
        
        print(f"Found {len(rows)} films")
        
        # Count existing summaries
        existing_summaries = sum(1 for r in rows if r.get('web_summary', '').strip())
        print(f"Found {existing_summaries} films with existing summaries (will be preserved)")
        
        # Determine actual starting point
        if start_idx > 0:
            print(f"Starting from index {start_idx} (film #{start_idx + 1})")
            rows_to_process = rows[start_idx:]
        else:
            # Find first film without summary
            first_empty = None
            for idx, row in enumerate(rows):
                if not row.get('web_summary', '').strip():
                    first_empty = idx
                    break
            if first_empty is not None:
                print(f"Auto-detected: Starting from first film without summary (index {first_empty}, film #{first_empty + 1})")
                rows_to_process = rows[first_empty:]
            else:
                print("All films already have summaries!")
                rows_to_process = []
        
        if max_films:
            rows_to_process = rows_to_process[:max_films]
            print(f"Processing first {max_films} films")
        
        found = 0
        not_found = 0
        skipped = 0
        
        for i, row in enumerate(rows_to_process):
            # Calculate actual index in full list
            if start_idx > 0:
                actual_idx = start_idx + i
            else:
                # Find actual index
                actual_idx = None
                for idx, r in enumerate(rows):
                    if r == row:
                        actual_idx = idx
                        break
                if actual_idx is None:
                    actual_idx = i
            
            film_name = row.get('name_russian', '').strip()
            name_original = row.get('name_original', '').strip()
            year = row.get('production_year', '').strip() or row.get('soviet_release_year', '').strip()
            year_int = int(year) if year and year.isdigit() else None
            
            # Skip if already has summary (double-check for safety)
            if row.get('web_summary', '').strip():
                print(f"[{actual_idx + 1}/{len(rows)}] ✓ Already has summary: {film_name}")
                skipped += 1
                continue
            
            print(f"[{actual_idx + 1}/{len(rows)}] Searching for: {film_name} ({year_int or 'no year'})")
            film_name = row.get('name_russian', '').strip()
            name_original = row.get('name_original', '').strip()
            year = row.get('production_year', '').strip() or row.get('soviet_release_year', '').strip()
            year_int = int(year) if year and year.isdigit() else None
            
            # Skip if already has summary
            if row.get('web_summary', '').strip():
                print(f"[{i+1}/{len(rows)}] ✓ Already has summary: {film_name}")
                found += 1
                continue
            
            print(f"[{i+1}/{len(rows)}] Searching for: {film_name} ({year_int or 'no year'})")
            
            summary = self.find_summary(film_name, year_int, name_original)
            
            if summary:
                # Ensure summary is translated to English before saving
                original_summary = summary
                summary = self.translate_to_english(summary)
                
                # VERIFY translation worked - must not contain Cyrillic
                has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in summary)
                if has_cyrillic:
                    # Translation failed - retry with more aggressive approach
                    print(f"        → Translation verification failed, retrying translation...")
                    # Use module-level translator if available, or try to import
                    translator_class = None
                    if TRANSLATOR_AVAILABLE and _GoogleTranslator is not None:
                        translator_class = _GoogleTranslator
                    else:
                        # Try to import again
                        try:
                            from deep_translator import GoogleTranslator
                            translator_class = GoogleTranslator
                        except:
                            pass
                    
                    if translator_class:
                        try:
                            # Try multiple translation attempts
                            translation_successful = False
                            for attempt in range(3):
                                try:
                                    translated_text = translator_class(source='ru', target='en').translate(original_summary[:5000])
                                    if translated_text and translated_text.strip():
                                        has_cyrillic_check = any('\u0400' <= char <= '\u04FF' for char in translated_text)
                                        if not has_cyrillic_check:
                                            summary = translated_text
                                            translation_successful = True
                                            print(f"        → Translation successful on attempt {attempt + 1}")
                                            break
                                        elif attempt < 2:
                                            print(f"        → Translation attempt {attempt + 1} still contains Cyrillic, retrying...")
                                    elif attempt < 2:
                                        print(f"        → Translation attempt {attempt + 1} returned empty, retrying...")
                                except Exception as e:
                                    if attempt < 2:
                                        print(f"        → Translation attempt {attempt + 1} error: {str(e)[:50]}, retrying...")
                                    else:
                                        print(f"        → Translation attempt {attempt + 1} error: {str(e)[:50]}")
                                if attempt < 2:
                                    time.sleep(1)  # Brief delay between attempts
                            
                            # Final check - if still has Cyrillic, reject summary
                            if not translation_successful:
                                if summary:
                                    has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in summary)
                                    if has_cyrillic:
                                        print(f"        → ERROR: Summary still contains Cyrillic after translation attempts - REJECTING")
                                        summary = None  # Reject untranslated summary
                                else:
                                    print(f"        → ERROR: All translation attempts failed - REJECTING")
                                    summary = None
                        except Exception as e:
                            print(f"        → ERROR: Translation retry error: {str(e)[:50]}")
                            summary = None
                    else:
                        # Try importing directly as fallback
                        try:
                            from deep_translator import GoogleTranslator
                            translated_text = GoogleTranslator(source='ru', target='en').translate(original_summary[:5000])
                            if translated_text and translated_text.strip():
                                has_cyrillic_check = any('\u0400' <= char <= '\u04FF' for char in translated_text)
                                if not has_cyrillic_check:
                                    summary = translated_text
                                    print(f"        → Translation successful (fallback import)")
                                else:
                                    print(f"        → ERROR: Translation still contains Cyrillic - REJECTING")
                                    summary = None
                            else:
                                print(f"        → ERROR: Translation returned empty - REJECTING")
                                summary = None
                        except ImportError as e:
                            print(f"        → ERROR: Cannot import GoogleTranslator: {e}")
                            summary = None
                        except Exception as e:
                            print(f"        → ERROR: Translation error: {str(e)[:50]}")
                            summary = None
                
                if summary:
                    row['web_summary'] = summary
                    found += 1
                    print(f"  ✓ Found summary ({len(summary)} chars, translated to English)")
                else:
                    not_found += 1
                    print(f"  ✗ Summary found but translation failed - skipping")
            else:
                not_found += 1
                print(f"  ✗ No summary found")
            
            # Save progress every 10 films - UPDATE THE FULL ROWS LIST
            if (i + 1) % 10 == 0:
                print(f"\n  Progress: {found} found, {not_found} not found, {skipped} skipped (existing)\n")
                # Update the full rows list with processed row
                if actual_idx < len(rows):
                    rows[actual_idx].update(row)
                
                # Save entire rows list to preserve all existing summaries
                with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                print(f"  ✓ Progress saved to {output_csv}")
        
        # Final save - write all rows (preserves existing summaries)
        print(f"\nSaving final results...")
        # Update all processed rows in the full list
        for i, row in enumerate(rows_to_process):
            if start_idx > 0:
                actual_idx = start_idx + i
            else:
                # Find actual index
                for idx, r in enumerate(rows):
                    if r.get('name_russian') == row.get('name_russian') and r.get('rank') == row.get('rank'):
                        actual_idx = idx
                        break
                else:
                    continue
            
            if actual_idx < len(rows):
                rows[actual_idx].update(row)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        final_count = sum(1 for r in rows if r.get('web_summary', '').strip())
        print(f"\n✓ Complete!")
        print(f"  New summaries found: {found}")
        print(f"  Not found: {not_found}")
        print(f"  Skipped (existing): {skipped}")
        print(f"  Total summaries in file: {final_count}/{len(rows)}")
        print(f"  Saved to: {output_csv}")
        
        # Cleanup Selenium if used
        self.cleanup_selenium()


if __name__ == "__main__":
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    start_idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    max_films = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    searcher = WebFilmSummarySearcher(delay=1.5)  # More conservative delay to avoid missing films
    searcher.add_summaries_to_csv(input_file, output_file, start_idx, max_films)

