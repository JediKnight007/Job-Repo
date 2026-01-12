# ECON1520 Scraper - Kino-Teatr.ru Soviet Film Data

A comprehensive web scraper for extracting Soviet film box office data from kino-teatr.ru.

## Project Structure

```
├── scripts/          # All Python code files
├── data/            # CSV files and data outputs
├── docs/            # Documentation files
└── outputs/         # Temporary output files
```

## Features

- **Main Scraper**: Scrapes year pages (1950-1991) to extract film data
- **Web Summary Search**: Finds and translates film summaries from multiple sources
- **Quality Checking**: Identifies and fixes problematic summaries
- **Box Office Calculation**: Calculates box office in rubles based on ticket prices

## Setup

1. Install dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

2. Make sure you have Chrome browser installed (required for Selenium).

## Usage

### Main Scraper

Scrape all years from 1950-1991:
```bash
cd scripts
python main.py --start-year 1950 --end-year 1991
```

### Adding Summaries

Fix remaining anomalous summaries:
```bash
cd scripts
python fix_all_remaining_anomalies.py ../data/soviet_releases_1950_1991_with_summaries.csv ../data/soviet_releases_1950_1991_with_summaries_anomalies_list.csv
```

### Identifying Issues

Find bot-blocked films:
```bash
cd scripts
python identify_bot_blocked_films.py ../data/soviet_releases_1950_1991_with_summaries.csv
```

Check summary quality:
```bash
cd scripts
python comprehensive_summary_check.py ../data/soviet_releases_1950_1991_with_summaries.csv
```

## Scripts

### Core Scripts
- `main.py` - Main scraper for kino-teatr.ru
- `search_film_summaries.py` - Web search and summary extraction
- `fix_all_remaining_anomalies.py` - Fixes problematic summaries

### Utility Scripts
- `identify_bad_summaries.py` - Identifies problematic summaries
- `identify_bot_blocked_films.py` - Finds films blocked by bot detection
- `comprehensive_summary_check.py` - Comprehensive quality checking
- `retry_problematic_summaries_improved.py` - Improved retry logic
- `retry_missing_summaries.py` - Translation utilities
- `add_english_names.py` - Adds English names to CSV
- `add_box_office.py` - Calculates box office
- `add_box_office_from_table.py` - Box office from table data
- `compare_box_office_versions.py` - Compares box office versions

## Data Files

Main CSV files are in the `data/` directory:
- `soviet_releases_1950_1991_with_summaries.csv` - Main dataset with summaries
- `soviet_releases_1950_1991_with_summaries_anomalies_list.csv` - Films with anomalies
- `soviet_releases_1950_1991_with_summaries_BOT_BLOCKED.csv` - Films blocked by bot detection


