"""
Comprehensive check for summary anomalies:
1. Weirdly written entries
2. Non-plot driven entries
3. Modern films outside Soviet timeline (1950-1991)
"""
import csv
import re
from datetime import datetime

def is_weirdly_written(summary):
    """Check for weirdly written, garbled, or nonsensical text."""
    if not summary or len(summary.strip()) < 30:
        return False, None
    
    summary_lower = summary.lower()
    
    # Check for excessive encoding issues
    if '&#x' in summary or '&#' in summary or '%20' in summary or '%C3' in summary:
        return True, "Encoding artifacts (HTML/URL encoding)"
    
    # Check for garbled text (mixed scripts, excessive special chars)
    if re.search(r'[^\w\s.,!?;:\-()\'"]{5,}', summary):
        return True, "Excessive special characters/garbled text"
    
    # Check for repetitive nonsense
    words = summary.split()
    if len(words) > 10:
        # Check if too many words are repeated
        from collections import Counter
        word_counts = Counter([w.lower() for w in words])
        repeated = sum(1 for count in word_counts.values() if count > len(words) * 0.1)
        if repeated > 5:
            return True, "Highly repetitive text"
    
    # Check for non-English/Russian mixed with nonsense
    if re.search(r'[а-яА-ЯёЁ]{10,}', summary) and not any(kw in summary_lower for kw in 
        ['фильм', 'film', 'movie', 'director', 'directed', 'режиссёр']):
        # Lots of Cyrillic but no film-related terms - might be garbled
        return True, "Non-film Russian text (possibly garbled)"
    
    # Check for search result pages or bot messages
    bot_patterns = [
        r'please confirm.*robot',
        r'we are sorry.*automated',
        r'verify.*human',
        r'results for.*sort by',
        r'1-16 of.*results',
        r'sponsored.*shop on',
        r'00or best offer',
        r'opens in a new window',
        r'checking.*browser',
        r'access denied',
        r'blocked.*captcha',
    ]
    for pattern in bot_patterns:
        if re.search(pattern, summary_lower):
            return True, "Bot message/search result page"
    
    # Check for dictionary definitions
    definition_patterns = [
        r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)',
        r'^[^.]*\s+—\s+(a|an|the)\s+(?!.*(film|movie|directed))',
    ]
    for pattern in definition_patterns:
        if re.match(pattern, summary, re.IGNORECASE):
            # But allow if it mentions film adaptation
            if not any(kw in summary_lower[:200] for kw in ['film', 'movie', 'adaptation', 'directed', 'director']):
                return True, "Dictionary definition (not about film)"
    
    # Check for navigation/breadcrumbs
    if '/' in summary and summary.count('/') >= 3:
        if any(kw in summary_lower for kw in ['главная', 'home', 'films', 'фильмы', 'menu']):
            return True, "Navigation/breadcrumb path"
    
    # Check for technical info only (no plot)
    if re.match(r'^(information about the film|информация о фильме)', summary_lower):
        if not any(kw in summary_lower for kw in ['plot', 'story', 'tells', 'about', 'сюжет', 'рассказ']):
            return True, "Technical info only (no plot)"
    
    return False, None

def is_non_plot_driven(summary):
    """Check if summary is not plot-driven."""
    if not summary or len(summary.strip()) < 50:
        return False, None
    
    summary_lower = summary.lower()
    
    # Must have plot keywords or film production details
    plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'events',
                     'сюжет', 'рассказ', 'рассказывает', 'о', 'про', 'происходит',
                     'character', 'hero', 'герой', 'персонаж', 'young', 'man', 'woman',
                     'love', 'любовь', 'life', 'жизнь', 'father', 'mother', 'daughter', 
                     'son', 'family', 'synopsis', 'growing', 'moving', 'journey',
                     'adventure', 'mystery', 'detective', 'murder', 'crime', 'war',
                     'battle', 'conflict', 'meeting', 'meet', 'returns', 'leaves']
    
    has_plot = any(kw in summary_lower for kw in plot_keywords)
    
    # Or film production details
    film_terms = ['director', 'directed', 'actor', 'actress', 'starring', 'cast',
                  'film', 'movie', 'cinema', 'screenplay', 'screenwriter', 'producer',
                  'premiere', 'studio', 'filmed', 'shot', 'based on', 'adaptation',
                  'режиссёр', 'актёр', 'актриса', 'фильм', 'кино', 'премьера', 'снят']
    
    has_film_terms = any(kw in summary_lower for kw in film_terms)
    
    if not has_plot and not has_film_terms:
        # Check if it's very short (might be acceptable if it's just a brief description)
        if len(summary) < 150:
            return True, "Non-plot driven (too short and no plot/film terms)"
    
    # Check if it's just a definition
    if re.match(r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)', 
                summary, re.IGNORECASE):
        if not any(kw in summary_lower[:200] for kw in ['film', 'movie', 'adaptation', 'directed']):
            return True, "Non-plot driven (definition only)"
    
    # Check if it's just technical crew info
    if re.search(r'director.*screenwriter.*operator.*composer', summary_lower):
        if not any(kw in summary_lower for kw in ['plot', 'story', 'tells', 'about', 'сюжет']):
            if len(summary) < 300:
                return True, "Non-plot driven (crew info only)"
    
    return False, None

def is_wrong_timeline(row):
    """Check if film is outside Soviet timeline (1950-1991) or clearly modern."""
    summary = row.get('web_summary', '').strip()
    if not summary:
        return False, None
    
    summary_lower = summary.lower()
    
    # Check for modern references (2000s, 2010s, 2020s)
    modern_years = []
    for year in range(2000, 2030):
        if str(year) in summary:
            modern_years.append(str(year))
    
    if modern_years:
        # Check if it's actually about a modern film
        modern_indicators = ['film', 'movie', 'released', 'premiere', 'directed', 
                           'фильм', 'кино', 'вышел', 'премьера']
        if any(kw in summary_lower for kw in modern_indicators):
            # Get the year from the row
            year = row.get('production_year', '') or row.get('soviet_release_year', '')
            if year and year.isdigit():
                year_int = int(year)
                if year_int >= 1950 and year_int <= 1991:
                    # Film is in our timeline but summary mentions modern years - suspicious
                    return True, f"Summary mentions modern years ({', '.join(modern_years)}) but film is {year_int}"
    
    # Check for modern technology/terms
    modern_terms = ['internet', 'website', 'online', 'streaming', 'netflix', 'amazon prime',
                   'smartphone', 'iphone', 'android', 'social media', 'facebook', 'twitter',
                   'instagram', 'youtube channel', 'podcast', 'blog', 'app', 'software',
                   'internet', 'веб-сайт', 'онлайн', 'стриминг', 'смартфон', 'социальные сети']
    
    if any(term in summary_lower for term in modern_terms):
        # Check if it's actually about a modern film/product
        if any(kw in summary_lower for kw in ['film', 'movie', 'directed', 'released', 'фильм']):
            year = row.get('production_year', '') or row.get('soviet_release_year', '')
            if year and year.isdigit():
                year_int = int(year)
                if year_int >= 1950 and year_int <= 1991:
                    return True, f"Summary mentions modern technology but film is {year_int}"
    
    # Check for obviously wrong film (summary about completely different film)
    # This is harder to detect automatically, but we can look for extreme mismatches
    film_name = row.get('name_russian', '').strip().lower()
    name_original = row.get('name_original', '').strip().lower()
    
    # If summary mentions a year that's way off
    year_in_summary = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', summary)
    if year_in_summary:
        year = row.get('production_year', '') or row.get('soviet_release_year', '')
        if year and year.isdigit():
            year_int = int(year)
            summary_years = [int(y) for y in year_in_summary if int(y) >= 1950]
            if summary_years:
                # If summary mentions a year > 10 years different from film year
                min_diff = min(abs(y - year_int) for y in summary_years)
                if min_diff > 15:  # More than 15 years difference
                    return True, f"Summary mentions year(s) {year_in_summary} but film is {year_int} (large discrepancy)"
    
    return False, None

def comprehensive_check(csv_file):
    """Run comprehensive check on all summaries."""
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)
    
    anomalies = {
        'weirdly_written': [],
        'non_plot_driven': [],
        'wrong_timeline': [],
    }
    
    print(f"Scanning {len(rows)} films...")
    print()
    
    for i, row in enumerate(rows):
        summary = row.get('web_summary', '').strip()
        if not summary:
            continue
        
        film_name = row.get('name_russian', '')
        year = row.get('production_year', '') or row.get('soviet_release_year', '')
        
        # Check for weirdly written
        is_weird, weird_reason = is_weirdly_written(summary)
        if is_weird:
            anomalies['weirdly_written'].append({
                'index': i + 1,
                'name': film_name,
                'year': year,
                'reason': weird_reason,
                'summary_preview': summary[:200]
            })
        
        # Check for non-plot driven
        is_non_plot, non_plot_reason = is_non_plot_driven(summary)
        if is_non_plot:
            anomalies['non_plot_driven'].append({
                'index': i + 1,
                'name': film_name,
                'year': year,
                'reason': non_plot_reason,
                'summary_preview': summary[:200]
            })
        
        # Check for wrong timeline
        is_wrong, wrong_reason = is_wrong_timeline(row)
        if is_wrong:
            anomalies['wrong_timeline'].append({
                'index': i + 1,
                'name': film_name,
                'year': year,
                'reason': wrong_reason,
                'summary_preview': summary[:200]
            })
    
    return anomalies, rows

if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    
    anomalies, rows = comprehensive_check(csv_file)
    
    print("=" * 80)
    print("COMPREHENSIVE SUMMARY ANOMALY REPORT")
    print("=" * 80)
    print()
    
    total_anomalies = sum(len(v) for v in anomalies.values())
    
    print(f"Total films with summaries: {sum(1 for r in rows if r.get('web_summary', '').strip())}")
    print(f"Total anomalies found: {total_anomalies}")
    print()
    
    # Weirdly written
    print(f"WEIRDLY WRITTEN ENTRIES: {len(anomalies['weirdly_written'])}")
    print("-" * 80)
    for item in anomalies['weirdly_written'][:20]:  # Show first 20
        print(f"Film #{item['index']}: {item['name']} ({item['year']})")
        print(f"  Issue: {item['reason']}")
        print(f"  Preview: {item['summary_preview']}...")
        print()
    if len(anomalies['weirdly_written']) > 20:
        print(f"  ... and {len(anomalies['weirdly_written']) - 20} more")
    print()
    
    # Non-plot driven
    print(f"NON-PLOT DRIVEN ENTRIES: {len(anomalies['non_plot_driven'])}")
    print("-" * 80)
    for item in anomalies['non_plot_driven'][:20]:  # Show first 20
        print(f"Film #{item['index']}: {item['name']} ({item['year']})")
        print(f"  Issue: {item['reason']}")
        print(f"  Preview: {item['summary_preview']}...")
        print()
    if len(anomalies['non_plot_driven']) > 20:
        print(f"  ... and {len(anomalies['non_plot_driven']) - 20} more")
    print()
    
    # Wrong timeline
    print(f"WRONG TIMELINE ENTRIES: {len(anomalies['wrong_timeline'])}")
    print("-" * 80)
    for item in anomalies['wrong_timeline']:
        print(f"Film #{item['index']}: {item['name']} ({item['year']})")
        print(f"  Issue: {item['reason']}")
        print(f"  Preview: {item['summary_preview']}...")
        print()
    print()
    
    # Summary list for user
    print("=" * 80)
    print("COMPLETE LIST OF ALL ANOMALIES (for deletion)")
    print("=" * 80)
    print()
    
    all_anomaly_indices = set()
    for category in anomalies.values():
        for item in category:
            all_anomaly_indices.add(item['index'])
    
    all_anomaly_indices = sorted(all_anomaly_indices)
    
    print(f"Total unique films with anomalies: {len(all_anomaly_indices)}")
    print()
    print("FILM INDICES TO REVIEW/DELETE:")
    print("-" * 80)
    
    for idx in all_anomaly_indices:
        # Get film info
        row = rows[idx - 1]
        issues = []
        for category, items in anomalies.items():
            for item in items:
                if item['index'] == idx:
                    issues.append(f"{category}: {item['reason']}")
        
        print(f"Film #{idx}: {row.get('name_russian', '')} ({row.get('production_year', '') or row.get('soviet_release_year', '')})")
        print(f"  Issues: {'; '.join(issues)}")
        print()
    
    # Save to CSV for easy review
    output_csv = csv_file.replace('.csv', '_anomalies_list.csv')
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'name_russian', 'year', 'issues', 'summary_preview'])
        writer.writeheader()
        for idx in all_anomaly_indices:
            row = rows[idx - 1]
            issues = []
            for category, items in anomalies.items():
                for item in items:
                    if item['index'] == idx:
                        issues.append(f"{category}: {item['reason']}")
            
            writer.writerow({
                'index': idx,
                'name_russian': row.get('name_russian', ''),
                'year': row.get('production_year', '') or row.get('soviet_release_year', ''),
                'issues': '; '.join(issues),
                'summary_preview': row.get('web_summary', '')[:300]
            })
    
    print(f"✓ Full list saved to: {output_csv}")


