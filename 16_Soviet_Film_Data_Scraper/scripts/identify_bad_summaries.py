"""
Identify summaries that are definitions, navigation text, or non-summary content.
"""
import csv
import re

def is_bad_summary(summary, film_name, row):
    """Check if summary appears to be a definition, navigation, or non-summary."""
    if not summary or len(summary.strip()) < 50:
        return True, "Too short"
    
    summary_lower = summary.lower()
    film_name_lower = film_name.lower() if film_name else ""
    
    # Pattern 1: Dictionary definitions (but NOT film descriptions)
    # Only flag if it's clearly a dictionary entry, not a film description
    definition_patterns = [
        # "X means..." - always a definition
        r'^[^.]*\s+means\s+',
        # "X refers to..." - always a definition  
        r'^[^.]*\s+refers\s+to\s+',
        # "X denotes..." - always a definition
        r'^[^.]*\s+denotes\s+',
        # "X is a [non-film thing]" - check if it's NOT about a film
        r'^[^.]*\s+is\s+(a|an|the)\s+(?!.*(film|movie|opera|ballet|feature|soviet|russian|directed|director|filmed|shot))',
        # Scientific/technical definitions
        r'^[^.]*\s+is\s+(a|an|the)\s+(intense|process|set|movement|time|period|conventional word)',
        # "X — a [non-film thing]"
        r'^[^.]*\s+—\s+(a|an|the)\s+(?!.*(film|movie|opera|ballet|feature|soviet|russian|directed|director|filmed|shot))',
    ]
    
    for pattern in definition_patterns:
        if re.match(pattern, summary, re.IGNORECASE):
            # Double-check: if it mentions film/movie/director, it's probably OK
            if not any(kw in summary_lower[:200] for kw in ['film', 'movie', 'opera', 'ballet', 'directed', 'director', 'filmed', 'shot', 'soviet', 'russian']):
                return True, "Dictionary definition"
    
    # Pattern 2: Navigation/website text
    nav_keywords = [
        'новости', 'news', 'дозорные', 'watchmen', 'лайфстайл', 'lifestyle',
        'кастинг', 'casting', 'поиск', 'search', 'войти', 'login', 'вход',
        'регистрация', 'register', 'навигация', 'navigation',
        'главная', 'home', 'menu', 'меню'
    ]
    
    nav_count = sum(1 for kw in nav_keywords if kw in summary_lower)
    if nav_count >= 3:
        return True, "Navigation/website text"
    
    # Pattern 3: Technical info only (cast lists, crew, no plot)
    technical_only_patterns = [
        r'^(information about the film|информация о фильме)',
        r'director.*screenwriter.*operator.*composer',
        r'режиссёр.*сценарист.*оператор.*композитор',
        r'^actors?.*roles?',
        r'^актёры.*роли',
    ]
    
    for pattern in technical_only_patterns:
        if re.search(pattern, summary_lower):
            # Check if it's ONLY technical info (no plot keywords)
            plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                           'сюжет', 'рассказ', 'рассказывает', 'о', 'про']
            has_plot = any(kw in summary_lower for kw in plot_keywords)
            if not has_plot and len(summary) < 500:
                return True, "Technical info only (no plot)"
    
    # Pattern 4: Wrong subject (e.g., about the city instead of the film)
    # Check if summary mentions film name but seems to be about something else
    if film_name:
        # If film name is in summary but it's clearly about the wrong thing
        # (e.g., "Tbilisi is the capital..." for a film called "Tbilisi - Paris and back")
        wrong_subject_patterns = [
            r'is the capital',
            r'is a city',
            r'is a town',
            r'столица',  # capital
            r'город',  # city
        ]
        if any(p in summary_lower for p in wrong_subject_patterns):
            # But film name should be in it
            if film_name_lower.split()[0] in summary_lower:
                return True, "Wrong subject (about place/thing, not film)"
    
    # Pattern 5: Too generic or non-specific
    generic_patterns = [
        r'^[^.]*\s+is\s+(a|an)\s+(soviet|russian|film|movie)',
        r'^[^.]*\s+—\s+(a|an)\s+(soviet|russian|film|movie)',
    ]
    
    for pattern in generic_patterns:
        if re.match(pattern, summary_lower) and len(summary) < 200:
            # Check if it has any actual content beyond the generic start
            # Be more lenient - accept if it mentions film production details, director, actors, etc.
            has_content = any(kw in summary_lower for kw in [
                'plot', 'story', 'tells', 'about', 'follows', 'narrative',
                'сюжет', 'рассказ', 'о', 'про', 'рассказывает',
                'director', 'directed', 'actor', 'actress', 'starring', 'cast',
                'premiere', 'studio', 'filmed', 'shot', 'based on', 'adaptation',
                'режиссёр', 'актёр', 'актриса', 'фильм', 'кино', 'премьера',
                'снят', 'снят', 'экранизация'
            ])
            if not has_content:
                return True, "Too generic (no actual content)"
    
    # Pattern 6: Breadcrumb/navigation paths
    if '/' in summary and summary.count('/') >= 3:
        if any(kw in summary_lower for kw in ['главная', 'home', 'фильмы', 'films']):
            return True, "Breadcrumb/navigation path"
    
    # Pattern 7: Password/definition entries (for the "Password" film)
    if 'password' in summary_lower or 'пароль' in summary_lower:
        if 'conventional word' in summary_lower or 'условное слово' in summary_lower:
            if 'film' not in summary_lower and 'фильм' not in summary_lower:
                return True, "Dictionary definition (password)"
    
    return False, None

def analyze_summaries(csv_file):
    """Analyze all summaries and identify problematic ones."""
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)
    
    problematic = []
    
    print("Analyzing all summaries...")
    print()
    
    for i, row in enumerate(rows):
        summary = row.get('web_summary', '').strip()
        if not summary:
            continue
        
        film_name = row.get('name_russian', '').strip()
        is_bad, reason = is_bad_summary(summary, film_name, row)
        
        if is_bad:
            problematic.append({
                'index': i + 1,
                'rank': row.get('rank', ''),
                'name_russian': film_name,
                'name_original': row.get('name_original', ''),
                'year': row.get('production_year', '') or row.get('soviet_release_year', ''),
                'summary': summary,
                'reason': reason,
                'length': len(summary)
            })
    
    print(f"Found {len(problematic)} problematic summaries out of {len([r for r in rows if r.get('web_summary', '').strip()])} total")
    print()
    
    # Group by reason
    by_reason = {}
    for item in problematic:
        reason = item['reason']
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(item)
    
    print("Breakdown by issue type:")
    for reason, items in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {reason}: {len(items)} films")
    print()
    
    print("=" * 80)
    print("PROBLEMATIC SUMMARIES:")
    print("=" * 80)
    print()
    
    for item in problematic:
        print(f"Film #{item['index']} (Rank {item['rank']}): {item['name_russian']} ({item['year']})")
        if item['name_original']:
            print(f"  Original: {item['name_original']}")
        print(f"  Issue: {item['reason']}")
        print(f"  Length: {item['length']} chars")
        print(f"  Summary preview: {item['summary'][:200]}...")
        print()
    
    # Save to CSV for review
    output_file = csv_file.replace('.csv', '_problematic_summaries.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'rank', 'name_russian', 'name_original', 'year', 'reason', 'summary'])
        writer.writeheader()
        for item in problematic:
            writer.writerow({
                'index': item['index'],
                'rank': item['rank'],
                'name_russian': item['name_russian'],
                'name_original': item['name_original'],
                'year': item['year'],
                'reason': item['reason'],
                'summary': item['summary']
            })
    
    print(f"✓ Saved problematic summaries to: {output_file}")
    print()
    print(f"Total problematic: {len(problematic)}")
    print(f"Percentage: {len(problematic)*100/len([r for r in rows if r.get('web_summary', '').strip()]):.2f}%")

if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    analyze_summaries(csv_file)

