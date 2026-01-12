# Comprehensive Dataset Assembly and Codebase Documentation

## Table of Contents
1. [Overview](#overview)
2. [Dataset Assembly Process](#dataset-assembly-process)
3. [Codebase Architecture](#codebase-architecture)
4. [Detailed Process Documentation](#detailed-process-documentation)
5. [Data Quality and Validation](#data-quality-and-validation)
6. [Translation and Summary Creation](#translation-and-summary-creation)
7. [Box Office Calculations](#box-office-calculations)
8. [Spreadsheet Integration](#spreadsheet-integration)

---

## Overview

This project assembles a comprehensive dataset of Soviet film releases from 1950-1991, including box office data, film metadata, and English plot summaries. The dataset is compiled from **kino-teatr.ru**, a Russian cinema database, with supplementary data from multiple web sources.

### Final Dataset Structure

The main dataset (`soviet_releases_1950_1991_with_summaries.csv`) contains:
- **4,652 films** from 1950-1991
- Russian film titles, English translations, production years
- Total viewers (box office attendance)
- Box office calculations in rubles
- English plot summaries (web-sourced and translated)
- Country of origin, Soviet release years
- Kinopoisk IDs (where available)

---

## Dataset Assembly Process

The dataset assembly follows a **three-step pipeline** executed sequentially:

### Step 1: Scraping Year Pages (Box Office Rankings)

**Script:** `main.py` → `FastKinoTeatrScraper.scrape_year_page()` or `KinoTeatrScraper.scrape_year_page()`

**Process:**
1. For each year from 1950-1991, visit: `https://www.kino-teatr.ru/box/history/sov/y{year}/`
2. Parse HTML table containing film rankings
3. Extract for each film:
   - **Rank** (position in box office ranking)
   - **Russian film name** (`name_russian`)
   - **Film URL** (relative path to individual film page)
   - **Country and production year** (parsed from "Country, Year" format)
   - **Soviet release year** (the year being scraped)
   - **Total viewers** (converted from formatted text like "1 234 567" to integer)

**Technical Details:**
- Uses **BeautifulSoup** for fast HTML parsing (preferred method)
- Falls back to **Selenium** for JavaScript-heavy pages
- Handles Windows-1251 encoding (legacy Russian encoding)
- Implements bot detection bypass strategies (realistic headers, delays)
- Parallel processing with ThreadPoolExecutor (5 workers by default) for speed

**Output:** `soviet_releases_1950_1991.csv` (or year-specific CSVs)

**Example Data Extracted:**
```csv
rank,name_russian,film_url,country,production_year,soviet_release_year,viewers_total
1,Иван Грозный,./kino/movie/sov/1234/,СССР,1944,1950,32500000
```

**Challenges Handled:**
- Bot detection pages ("Роботам запрещено" - "Robots forbidden")
- Inconsistent HTML structure across years
- Missing or malformed data
- Network timeouts and rate limiting

---

### Step 2: Scraping Film Metadata

**Script:** `main.py` → `scrape_film_metadata()`

**Process:**
1. Reads CSV from Step 1
2. For each film URL, visits the individual film page: `https://www.kino-teatr.ru/{film_url}`
3. Extracts additional metadata:
   - **Original name** (`name_original`) - English/Latin name if available
   - **Country** (more precise than Step 1)
   - **Short description** (`description`) - Russian plot summary from kino-teatr.ru
   - **Production year** (refined, may differ from Step 1)
   - **Kinopoisk ID** (if linked)

**Technical Details:**
- Uses Selenium for reliable JavaScript rendering (many pages are dynamic)
- Implements retry logic (up to 3 attempts per film)
- Handles missing data gracefully (not all films have all fields)
- Preserves existing data from Step 1

**Output:** `films_metadata.csv` (merged with Step 1 data)

**Key Selectors Used:**
- Original name: Various patterns (`.original_name`, `[itemprop="name"]`, etc.)
- Description: `.description`, `.synopsis`, etc.
- Kinopoisk ID: Extracted from links or metadata

---

### Step 3: Merging Data and Calculating Box Office

**Script:** `main.py` → `merge_data()` + `add_box_office.py`

**Process:**
1. **Merging:** Combines Step 1 (box office rankings) and Step 2 (film metadata) by film URL
2. **Box Office Calculation:**
   - Formula: `box_office_rubles = viewers_total × avg_ticket_price_rub`
   - Uses historical average ticket prices by year (see Box Office Calculations section)

**Ticket Price Schedule:**
- **1950s:** 0.25-0.30 rubles (stable low prices)
- **1960s:** 0.30-0.40 rubles (gradual increase)
- **1970s:** 0.40-0.50 rubles (continued increase)
- **1980s-1991:** 0.50-0.60 rubles (higher prices)

**Technical Details:**
- Handles missing viewers or years (sets box office to empty)
- Rounds box office to 2 decimal places
- Creates separate columns: `avg_ticket_price_rub` and `box_office_rubles`

**Output:** Final merged CSV with box office calculations

---

## Codebase Architecture

### File Organization

```
scripts/
├── main.py                                    # Core scraper (Steps 1-3)
├── search_film_summaries.py                   # Web summary search & translation
├── fix_all_remaining_anomalies.py             # Quality improvement script
├── retry_problematic_summaries_improved.py    # Summary quality checks
├── retry_missing_summaries.py                 # Translation utilities
├── identify_bad_summaries.py                  # Anomaly detection
├── identify_bot_blocked_films.py              # Bot detection analysis
├── comprehensive_summary_check.py             # Full quality audit
├── add_box_office.py                          # Box office calculator
├── add_box_office_from_table.py               # Alternative box office source
├── add_english_names.py                       # English name lookup
└── compare_box_office_versions.py             # Data comparison utility

data/
└── *.csv                                      # All CSV data files

docs/
└── DATASET_ASSEMBLY_AND_CODEBASE_DOCUMENTATION.md
```

### Core Classes

#### 1. `KinoTeatrScraper` (Selenium-based)
- **Purpose:** Reliable scraping with JavaScript rendering
- **Use case:** Film metadata extraction (Step 2)
- **Features:**
  - Headless Chrome with stealth settings
  - Anti-bot detection (hides webdriver properties)
  - Retry logic with exponential backoff
  - Automatic driver management

#### 2. `FastKinoTeatrScraper` (Requests + BeautifulSoup)
- **Purpose:** Fast parallel scraping for static pages
- **Use case:** Year page scraping (Step 1)
- **Features:**
  - ThreadPoolExecutor for parallel requests
  - BeautifulSoup for fast HTML parsing
  - Realistic HTTP headers
  - Bot detection handling

#### 3. `WebFilmSummarySearcher`
- **Purpose:** Find and extract film summaries from the entire web
- **Use case:** Adding English plot summaries
- **Features:**
  - Multi-source search (Wikipedia, Kinopoisk, IMDb, general web)
  - Intelligent content extraction (plot sections, not just first paragraph)
  - Translation pipeline (Russian → English)
  - Quality filtering

---

## Detailed Process Documentation

### Web Summary Search Process

**Script:** `search_film_summaries.py`

The web summary search is the most complex process, involving multiple stages:

#### 1. Search Strategy

The searcher uses a **multi-tier search strategy**:

**Tier 1: Wikipedia Direct Access**
- Constructs Wikipedia URLs with film name variations:
  - `https://ru.wikipedia.org/wiki/{film_name}_(фильм,_{year})`
  - `https://ru.wikipedia.org/wiki/{film_name}_(фильм)`
  - `https://ru.wikipedia.org/wiki/{film_name}`
- Prioritizes URLs with `_(фильм)` suffix to avoid disambiguation pages
- Extracts content specifically from **Plot/Сюжет section** (not intro paragraph)

**Tier 2: General Web Search**
- Uses DuckDuckGo HTML search (via requests, fallback to Selenium)
- Searches for: `"{film_name}" {year} film plot summary`
- Visits top 10-15 results sequentially
- Skips social media and shopping sites

**Tier 3: Direct Database Access**
- Tries direct URLs to:
  - **Kinopoisk** (Russian film database): `https://www.kinopoisk.ru/index.php?kp_query={film_name}`
  - **IMDb** (if English name available): `https://www.imdb.com/find/?q={name_original}+{year}`
- Extracts synopsis from structured pages

**Tier 4: AI Fallback (Optional)**
- Uses Google Gemini API if available
- Generates summary from film name and year

#### 2. Content Extraction

The `extract_text_from_page()` method is sophisticated:

**Wikipedia Handling:**
1. Finds main content div (`mw-content-text` or `mw-parser-output`)
2. Searches for Plot/Сюжет heading (h2, h3, h4)
3. Extracts all paragraphs following the plot heading until next section
4. Skips warning boxes, templates, and disambiguation messages
5. Removes citations `[1]`, `[citation needed]`, etc.
6. Combines paragraphs into full plot summary

**Kinopoisk Handling:**
1. Looks for synopsis selectors: `[data-test-id="synopsis"]`, `[class*="synopsis"]`
2. Extracts from structured divs
3. Handles bot detection pages

**IMDb Handling:**
1. Finds plot section: `[data-testid="Storyline"]` or `.plot` classes
2. Extracts plot text from structured elements
3. Filters out cast/crew lists

**General Web Pages:**
1. Removes scripts, styles, navigation, footer, header
2. Finds main content area (`.content`, `main`, `article`, etc.)
3. Extracts substantial paragraphs (>150 chars)
4. Filters for plot-related keywords
5. Combines top paragraphs

**Bot Detection Filtering:**
- Early detection of CAPTCHA pages
- Rejects text containing: "please confirm", "you are not a robot", "automated requests", "captcha", etc.
- Checks for suspiciously short texts with bot keywords

#### 3. Summary Condensation

The `condense_summary()` method:
- Splits text into sentences
- If >2 sentences, takes first 2 substantial sentences (>30 chars each)
- Preserves sentence structure and punctuation
- Returns original if condensation not needed

---

### Translation Process

**Scripts:** `search_film_summaries.py`, `retry_missing_summaries.py`, `fix_all_remaining_anomalies.py`

Translation uses a **multi-method fallback system**:

#### Method 1: Aggressive Translation (`aggressive_translate()`)
- Uses `deep_translator.GoogleTranslator`
- Explicit Russian-to-English translation
- Handles chunking for long texts (>4000 chars)
- Retries up to 3 times with progressive delays (2s, 4s)

#### Method 2: Auto-detect Translation
- Uses Google Translator with `source='auto'`
- Detects source language automatically
- Useful when language is uncertain

#### Method 3: Explicit Russian→English
- Forces Russian as source language
- Handles edge cases where auto-detect fails

#### Method 4: Sentence-by-Sentence Translation
- For very long texts (>500 chars)
- Splits into sentences
- Translates first 20 sentences individually
- Combines results
- Adds delays between sentences (0.3s) to avoid rate limiting

#### Translation Verification

After translation:
1. **Cyrillic Check:** Verifies no Cyrillic characters remain (except in film names)
2. **Length Check:** Ensures translation is substantial (>40-50 chars)
3. **Bot Message Check:** Rejects translated bot detection pages
4. **Fallback:** If translation fails but Russian text has plot content, accepts Russian summary (to avoid losing valid data)

**Translation Challenges Addressed:**
- **Rate Limiting:** Progressive delays, chunking, sentence-by-sentence
- **API Failures:** Multiple retry attempts with different methods
- **Long Texts:** Automatic chunking to stay under API limits
- **Quality:** Verification checks prevent garbage translations

---

## Data Quality and Validation

### Quality Checking Process

Multiple scripts work together to ensure data quality:

#### 1. `identify_bad_summaries.py`
**Purpose:** Initial detection of problematic summaries

**Checks for:**
- **Bot messages:** "please confirm", "you are not a robot", etc.
- **Dictionary definitions:** Text starting with "X is a..." without film context
- **Navigation text:** "Films", "About the film", "Creators and actors"
- **Search result snippets:** "Results for", "Sort by:", "Price:"
- **Too short:** <100 characters
- **Too long:** >2000 characters (likely includes extra content)
- **No plot keywords:** Missing words like "plot", "story", "tells", "follows"

#### 2. `comprehensive_summary_check.py`
**Purpose:** Full quality audit of all summaries

**Enhanced checks:**
- **Weirdly written:** Unusual formatting, excessive punctuation
- **Non-plot driven:** Lists of actors, technical details, reviews
- **Wrong timeline:** References to modern years (2000+), modern technology
- **Cast/crew lists:** IMDb-style technical information
- **Blog posts/quotes:** Personal opinions, not objective summaries

#### 3. `is_good_summary()` (from `retry_problematic_summaries_improved.py`)
**Purpose:** Final validation before accepting summaries

**Validates:**
- **Plot keywords present:** "plot", "story", "tells", "follows", "about", "narrative", "synopsis"
- **Action words:** "meets", "discovers", "finds", "goes", "becomes", etc.
- **Event indicators:** "character", "hero", "protagonist", "village", "journey", etc.
- **Substantial length:** >150 characters for narrative summaries
- **No bad patterns:** Rejects blog posts, quotes, marketing text

#### 4. `fix_all_remaining_anomalies.py`
**Purpose:** Systematic fixing of all problematic summaries

**Process:**
1. Reads list of anomalous films from CSV
2. For each film:
   - Attempts to find better summary using improved search
   - Applies all quality checks
   - Verifies Soviet era correctness
   - Translates if needed
   - Saves progress every 25 films (checkpoint system)

**Quality Improvements:**
- Early bot message detection (before translation)
- Enhanced Wikipedia plot extraction
- Better filtering of cast/crew lists
- Timeline verification (rejects modern films)
- Accepts valid Russian summaries if translation fails

### Bot Detection Analysis

**Script:** `identify_bot_blocked_films.py`

**Purpose:** Identifies films where summaries are bot detection pages instead of actual content

**Detection Patterns:**
- "Please confirm that you and not a robot are sending requests"
- "We're sorry, but it looks like requests sent from your device are automated"
- "After checkbox you will have additional check"
- Multiple bot keywords in short text (<500 chars)

**Result:** 102 films (2.2% of dataset) identified as bot-blocked

**Impact:** These films need manual fixes or alternative sources

---

## Translation and Summary Creation

### Summary Creation Pipeline

The complete pipeline for adding summaries:

```
1. Read film name, year, original name
   ↓
2. Try Wikipedia direct access
   ├─ Success? → Extract plot section → Translate → Quality check → Done
   └─ Fail? → Continue
   ↓
3. General web search (DuckDuckGo)
   ├─ Visit top results
   ├─ Extract content
   ├─ Filter bot messages
   └─ Success? → Translate → Quality check → Done
   ↓
4. Direct database access (Kinopoisk, IMDb)
   ├─ Extract synopsis
   └─ Success? → Translate → Quality check → Done
   ↓
5. AI fallback (Gemini)
   └─ Generate summary → Quality check → Done
```

### Translation Quality Assurance

**Verification Steps:**
1. **Cyrillic Detection:** Checks for remaining Russian characters
2. **Length Validation:** Minimum 40-50 characters
3. **Content Check:** Verifies plot keywords present
4. **Bot Message Filter:** Rejects CAPTCHA pages
5. **Timeline Check:** Verifies Soviet era (1950-1991)
6. **Quality Scoring:** Uses `is_good_summary()` function

**Fallback Strategy:**
- If English translation fails but Russian summary has plot content:
  - Accepts Russian summary (better than nothing)
  - Marks for later translation
  - Preserves valuable data

---

## Box Office Calculations

### Historical Ticket Prices

**Source:** Based on Soviet cinema statistics and historical trends

**Methodology:**
- Prices gradually increased over time due to inflation and policy changes
- Average prices compiled from historical sources
- Applied uniformly to all films released in a given year

**Price Schedule (in rubles):**

| Period | Years | Price Range | Trend |
|--------|-------|-------------|-------|
| 1950s | 1950-1960 | 0.25-0.30 | Stable low prices |
| 1960s | 1961-1970 | 0.31-0.40 | Gradual increase |
| 1970s | 1971-1980 | 0.41-0.50 | Continued increase |
| 1980s-1991 | 1981-1991 | 0.51-0.60 | Higher prices |

**Example:**
- Film released in 1975: 0.45 rubles per ticket
- Film with 10,000,000 viewers: 10,000,000 × 0.45 = **4,500,000 rubles**

### Calculation Script

**Script:** `add_box_office.py`

**Process:**
1. Reads CSV with `viewers_total` and `soviet_release_year` columns
2. Looks up ticket price for the year from `TICKET_PRICES_BY_YEAR` dictionary
3. Calculates: `box_office_rubles = viewers_total × avg_ticket_price_rub`
4. Adds columns:
   - `avg_ticket_price_rub` (ticket price used)
   - `box_office_rubles` (calculated box office)

**Handling Edge Cases:**
- Missing viewers: Sets box office to empty
- Missing year: Sets box office to empty
- Years outside range (1950-1991): Uses boundary value (1950 or 1991 price)

**Output Format:**
- Box office rounded to 2 decimal places
- Ticket price as float

---

## Spreadsheet Integration

### CSV Structure

The final dataset CSV has the following columns:

**Core Fields:**
- `rank` - Box office ranking position
- `name_russian` - Russian film title
- `name_english` - English translation (added via `add_english_names.py`)
- `name_original` - Original/Latin name from film page
- `film_url` - Relative URL to film page on kino-teatr.ru

**Box Office Fields:**
- `viewers_total` - Total attendance (integer)
- `soviet_release_year` - Year of Soviet release (1950-1991)
- `avg_ticket_price_rub` - Average ticket price for that year
- `box_office_rubles` - Calculated box office (viewers × price)

**Metadata Fields:**
- `country` - Country of origin
- `production_year` - Year film was produced
- `kinopoisk_id` - Kinopoisk database ID (if available)
- `description` - Original Russian description from kino-teatr.ru
- `web_summary` - English plot summary (web-sourced and translated)

### Data Preservation

**Key Feature:** All scripts preserve existing data when updating CSVs

**Implementation:**
- Scripts read existing CSV first
- Only update missing or problematic fields
- Maintain all existing columns
- Checkpoint system for long-running processes (saves progress every N films)

**Example:** When adding summaries:
```python
# Read existing CSV
rows = []
with open('film.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # If summary exists and is good, keep it
        if row.get('web_summary') and is_good_summary(row['web_summary']):
            continue
        # Otherwise, try to find better summary
        new_summary = search_for_summary(...)
        if new_summary:
            row['web_summary'] = new_summary
        rows.append(row)
```

### Additional CSV Files

**Analysis CSVs:**
- `soviet_releases_1950_1991_with_summaries_anomalies_list.csv` - Films with problematic summaries
- `soviet_releases_1950_1991_with_summaries_BOT_BLOCKED.csv` - Films blocked by bot detection
- `soviet_releases_1950_1991_with_summaries_WRONG_TIMELINE.csv` - Films with wrong timeline references

**Backup Files:**
- `soviet_releases_1950_1991_with_summaries_backup.csv` - Full backup before major changes

---

## Technical Implementation Details

### Bot Detection Bypass Strategies

The scraper implements multiple strategies to avoid bot detection:

1. **Realistic Headers:**
   - Uses standard browser User-Agent
   - Includes Accept-Language, Referer, DNT headers
   - Matches real browser request patterns

2. **Selenium Stealth:**
   - Hides `navigator.webdriver` property
   - Removes automation banners
   - Simulates real browser environment
   - Uses headless mode with stealth options

3. **Request Delays:**
   - Configurable delays between requests (default 0.5-2.0s)
   - Random jitter to avoid predictable patterns
   - Respects rate limits

4. **Session Management:**
   - Reuses HTTP sessions for cookies
   - Maintains referrer chains
   - Handles redirects properly

### Error Handling

**Retry Logic:**
- Up to 3 retry attempts for failed requests
- Exponential backoff (2s, 4s delays)
- Different strategies on each retry (requests → Selenium → alternative URL)

**Graceful Degradation:**
- Missing data handled gracefully (empty strings)
- Partial data preserved (some fields missing is OK)
- Logging of failures for manual review

**Checkpoint System:**
- Long-running scripts save progress every N films (typically 25)
- Can resume from last checkpoint if interrupted
- Prevents data loss on crashes

### Performance Optimizations

1. **Parallel Processing:**
   - ThreadPoolExecutor for year page scraping (5 workers)
   - Concurrent requests for faster processing
   - Queue management to avoid overload

2. **Efficient Parsing:**
   - BeautifulSoup with 'lxml' parser (fast C library)
   - Specific selectors (not full DOM traversal)
   - Early termination when content found

3. **Caching:**
   - Session reuse for HTTP connections
   - Driver reuse for Selenium (don't restart for each film)

---

## Usage Examples

### Running the Full Pipeline

```bash
cd scripts
python main.py --start-year 1950 --end-year 1991
```

This runs all three steps automatically:
1. Scrapes year pages (1950-1991)
2. Scrapes film metadata
3. Merges and calculates box office

### Adding English Names

```bash
cd scripts
python add_english_names.py ../data/soviet_releases_1950_1991.csv
```

### Adding Box Office

```bash
cd scripts
python add_box_office.py ../data/soviet_releases_1950_1991.csv
```

### Finding and Fixing Summary Issues

```bash
cd scripts

# 1. Identify problematic summaries
python comprehensive_summary_check.py ../data/soviet_releases_1950_1991_with_summaries.csv

# 2. Find bot-blocked films
python identify_bot_blocked_films.py ../data/soviet_releases_1950_1991_with_summaries.csv

# 3. Fix remaining anomalies
python fix_all_remaining_anomalies.py ../data/soviet_releases_1950_1991_with_summaries.csv ../data/soviet_releases_1950_1991_with_summaries_anomalies_list.csv
```

---

## Future Improvements

### Potential Enhancements

1. **Improved Translation:**
   - Fine-tune translation quality checks
   - Better handling of film-specific terminology
   - Context-aware translation

2. **Alternative Sources:**
   - Additional film databases
   - Archive access for rare films
   - Manual review queue for bot-blocked films

3. **Data Validation:**
   - Cross-reference with other databases
   - Historical accuracy verification
   - Automated fact-checking

4. **Performance:**
   - Distributed scraping
   - Better caching strategies
   - Incremental updates

---

## Conclusion

This documentation provides a comprehensive overview of how the Soviet film dataset was assembled, from initial web scraping through data quality improvement and box office calculations. The codebase implements robust error handling, quality assurance, and data preservation to create a reliable and accurate dataset for research and analysis.

For questions or issues, refer to the individual script docstrings or the main README.md file.

