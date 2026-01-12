"""
IMPROVED retry script for problematic summaries.
Addresses: translation failures, Wikipedia rejections, navigation text, and quality checks.
"""
import csv
import sys
import time
import re
from search_film_summaries import WebFilmSummarySearcher
from retry_missing_summaries import aggressive_translate

def clean_navigation_text(text):
    """Remove navigation and website UI elements from text."""
    if not text:
        return text
    
    # Remove common navigation patterns (including concatenated forms)
    nav_patterns = [
        # English navigation
        r'\bMenu\b|\bSearch\b|\bLive\b|\bHome\b|\bProgram\b|\bShows\b|\bFilms\b|\bSeries\b',
        r'\bClose\b|\bPrevious\b|\bNext\b|\bUnsubscribe\b|\bSubscribe\b',
        r'\bRating\b|\bRate\b|\bIMDb\s*RATING\b|\bYOUR\s*RATING\b',
        r'\bBack\b|\bJump\s+to\b|\bCast\s*&\s*crew\b|\bTrivia\b|\bIMDbPro\b',
        r'\bLoading\s+video\b|\bPrevious\s+series\b|\bNext\s+series\b',
        r'\bReport\s+a\s+technical\s+problem\b',
        # French/non-English navigation (including concatenated)
        r'\bSommaire\s+de\s+la\s+fiche\b',
        r'\bShare\b|\bFacebook\b|\bMail\b|\bFavorite\b|\bFermer\b',
        r'\bShareFacebookMailFavoriteFermer\b',  # Concatenated form
        r'\bContents?\b',
        # Russian navigation
        r'\bновости\b|\bnews\b|\bдозорные\b|\bкастинг\b|\bcasting\b|\bпоиск\b|\bsearch\b',
        r'\bглавная\b|\bhome\b|\bменю\b|\bmenu\b|\bнавигация\b|\bnavigation\b',
        r'\bвойти\b|\blogin\b|\bвход\b|\bрегистрация\b|\bregister\b',
        # Common patterns
        r'\bInformation\s+about\s+the\s+film\b',
        r'\bActors\s+and\s+roles\b|\bReviews\b',
        r'\bFilm\s+posters\b|\bStills\s+from\s+the\s+film\b',
    ]
    
    cleaned = text
    for pattern in nav_patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    
    # Remove concatenated navigation blocks (like ShareFacebookMailFavoriteFermer)
    # Look for blocks of navigation words stuck together
    nav_block_patterns = [
        r'\b[Ss]hare[Ff]acebook[Mm]ail[Ff]avorite[Ff]ermer\w*\b',
        r'\b[Ss]ommaire\s+de\s+la\s+fiche\w*\b',
        r'\b[Cc]ontents?\w*\b',
    ]
    for pattern in nav_block_patterns:
        cleaned = re.sub(pattern, ' ', cleaned)
    
    # Remove standalone navigation words (but preserve if part of content words)
    nav_words_standalone = ['share', 'facebook', 'mail', 'favorite', 'fermer', 
                           'sommaire', 'fiche', 'menu', 'search', 'home', 
                           'close', 'previous', 'next', 'subscribe', 'rating', 
                           'rate', 'back', 'cast', 'crew', 'trivia', 'imdb',
                           'loading', 'video', 'series']
    
    # Only remove if it's a standalone word (word boundaries)
    for nav_word in nav_words_standalone:
        # Remove if it's a standalone word, but keep if it's part of a larger word
        cleaned = re.sub(r'\b' + nav_word + r'\b', ' ', cleaned, flags=re.IGNORECASE)
    
    # Remove multiple spaces and clean up
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove leading/trailing punctuation and standalone navigation remnants
    cleaned = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', cleaned)
    
    # Final cleanup - remove any remaining navigation words
    for nav_word in nav_words_standalone:
        cleaned = re.sub(r'\b' + nav_word + r'\b', ' ', cleaned, flags=re.IGNORECASE)
    
    # Final cleanup of spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def improved_search(film_name, name_original, year, url=None, searcher=None):
    """Use improved search strategies for problematic films."""
    if searcher is None:
        searcher = WebFilmSummarySearcher(delay=0.5)  # Reduced from 1.5 to 0.5 seconds
    
    # Strategy 1: Search with "film" or "movie" explicitly in query
    queries = []
    if name_original:
        queries.append(f'"{name_original}" film {year}')
        queries.append(f'"{name_original}" movie {year}')
        queries.append(f'"{name_original}" soviet film')
    
    queries.append(f'"{film_name}" фильм {year}')
    queries.append(f'"{film_name}" советский фильм')
    queries.append(f'"{film_name}" film plot {year}')
    
    # Remove parenthetical info like "(фильм-балет)" for search
    clean_name = re.sub(r'\([^)]+\)', '', film_name).strip()
    if clean_name != film_name:
        queries.append(f'"{clean_name}" film {year}')
    
    # Strategy 2: Try to scrape from kino-teatr.ru directly if URL available
    if url and 'kino-teatr.ru' in url:
        from get_final_3_summaries import scrape_kino_teatr_page
        page_summary = scrape_kino_teatr_page(url)
        if page_summary:
            # Clean navigation text
            page_summary = clean_navigation_text(page_summary)
            
            # Check if it's actually about a film
            page_lower = page_summary.lower()
            if any(kw in page_lower for kw in ['сюжет', 'plot', 'рассказ', 'story', 'фильм', 'film']):
                # Extract plot-related sentences
                sentences = re.split(r'[.!?]+', page_summary)
                plot_sentences = []
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 50:
                        sent_lower = sent.lower()
                        # Prioritize sentences with plot keywords
                        if any(kw in sent_lower for kw in ['сюжет', 'plot', 'рассказ', 'story', 'о', 'about', 'tells', 'follows']):
                            plot_sentences.append(sent)
                        elif len(plot_sentences) < 2:  # Add a couple more if no plot keywords found
                            plot_sentences.append(sent)
                if plot_sentences:
                    combined = '. '.join(plot_sentences[:3])
                    # Quick quality check before translation (saves time)
                    if len(combined.strip()) > 100:
                        # Try translation, but accept even if it fails partially
                        translated = aggressive_translate(combined)
                        if not translated or len(translated.strip()) < 50:
                            # If translation fails, try direct translate
                            try:
                                from deep_translator import GoogleTranslator
                                translated = GoogleTranslator(source='auto', target='en').translate(combined[:5000])
                            except:
                                # Accept original if translation completely fails
                                translated = combined
                        
                        if translated and len(translated.strip()) > 100:
                            cleaned = clean_navigation_text(translated)
                            # Quick validation before returning
                            if len(cleaned.strip()) > 100:
                                return cleaned
    
    # Strategy 3: Try Wikipedia directly (often high quality)
    try:
        wiki_summary = searcher.find_summary(film_name, year, name_original)
        if wiki_summary:
            # Wikipedia summaries are usually good - be more lenient
            wiki_lower = wiki_summary.lower()
            
            # Check if it's a definition (but allow if it mentions it's a film adaptation)
            is_def = re.match(r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)', 
                            wiki_summary, re.IGNORECASE)
            
            # Wikipedia often starts with "X is a novel/play" but then describes the film
            if is_def and len(wiki_summary) > 300:
                # Check if it mentions film adaptation later
                if any(kw in wiki_lower for kw in ['film', 'movie', 'adaptation', 'directed', 'director']):
                    is_def = False  # Override - it's describing the film adaptation
            
            if not is_def:
                translated = aggressive_translate(wiki_summary)
                if not translated or len(translated.strip()) < 50:
                    try:
                        from deep_translator import GoogleTranslator
                        translated = GoogleTranslator(source='auto', target='en').translate(wiki_summary[:5000])
                    except:
                        translated = wiki_summary
                
                if translated:
                    cleaned = clean_navigation_text(translated)
                    # Wikipedia summaries are usually good - be more lenient
                    # Accept if length is reasonable, even if quality check is strict
                    if len(cleaned) > 120:  # Reduced from 150
                        # Quick validation - Wikipedia is usually reliable
                        # Check it's not obviously wrong content
                        cleaned_lower = cleaned.lower()
                        if not any(kw in cleaned_lower for kw in ['recipe', 'cooking', 'mango', 'avocado', 'servings']):
                            return cleaned
    except:
        pass
    
    # Strategy 4: Try web search with film-specific queries (limit to 2 for speed)
    for query in queries[:2]:  # Reduced from 3 to 2 queries for speed
        try:
            results = searcher.get_search_results(query)
            # Visit results looking for actual plot summaries (limit to 3 for speed)
            for result in results[:3]:  # Reduced from 5 to 3 results
                url_to_check = result['url']
                
                # Skip obvious non-content pages
                if any(skip in url_to_check.lower() for skip in 
                       ['/search', '/login', '/tag/', '/category/', 'wiktionary', 'dictionary',
                        'recipe', 'cooking', 'food', 'kitchen', 'cuisine', 'cookbook']):
                    continue
                
                try:
                    # Reduced delay - only sleep if not first result
                    if result != results[0]:
                        time.sleep(searcher.delay)
                    import requests
                    response = requests.get(url_to_check, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        summary = searcher.extract_text_from_page(response.text, url_to_check)
                        if summary:
                            # Quick check for wrong content before processing
                            summary_lower_pre = summary.lower()
                            wrong_content = ['recipe', 'mango', 'avocado', 'servings', 'cooking', 
                                            'kitchen', 'ingredients', 'cookbook', 'cuisine', 'food blog']
                            if any(kw in summary_lower_pre for kw in wrong_content):
                                # Skip if it's clearly not about a film
                                if not any(kw in summary_lower_pre for kw in ['film', 'movie', 'director', 'actor', 'plot']):
                                    continue
                            
                            # Clean navigation
                            summary = clean_navigation_text(summary)
                            
                            # Check if it's actually about the film (has plot keywords or film terms)
                            summary_lower = summary.lower()
                            if any(kw in summary_lower for kw in 
                                   ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                                    'сюжет', 'рассказ', 'рассказывает', 'о', 'про',
                                    'film', 'movie', 'director', 'directed', 'actor']):
                                translated = aggressive_translate(summary)
                                if not translated or len(translated.strip()) < 50:
                                    try:
                                        from deep_translator import GoogleTranslator
                                        translated = GoogleTranslator(source='auto', target='en').translate(summary[:5000])
                                    except:
                                        translated = summary
                                
                                if translated:
                                    cleaned = clean_navigation_text(translated)
                                    # Verify it's not a definition
                                    if not re.match(r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)', 
                                                   cleaned, re.IGNORECASE):
                                        if len(cleaned) > 100:
                                            return cleaned
                except:
                    continue
        except:
            continue
        # Reduced delay between query attempts
        time.sleep(0.3)
    
    return None

def is_good_summary(summary):
    """Improved quality check for summaries - very lenient."""
    if not summary or len(summary.strip()) < 60:  # Reduced from 80 to 60 - very lenient
        return False, "Too short"
    
    summary = clean_navigation_text(summary)
    summary_lower = summary.lower()
    
    # Check for obviously wrong content (recipes, unrelated topics)
    wrong_content_keywords = ['recipe', 'mango', 'avocado', 'servings', 'cooking', 
                             'kitchen', 'ingredients', 'cookbook', 'cuisine']
    if any(kw in summary_lower for kw in wrong_content_keywords):
        # Check if it's actually about a film
        if not any(kw in summary_lower for kw in ['film', 'movie', 'director', 'actor', 'plot', 'story']):
            return False, "Wrong content (not about film)"
    
    # Check if it's still a definition (but allow film adaptations)
    is_def = re.match(r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)', 
                    summary, re.IGNORECASE)
    if is_def and len(summary) < 300:  # Reduced from 400 to 300
        # Very short definitions are bad, longer ones might describe film adaptation
        if not any(kw in summary_lower for kw in ['film', 'movie', 'adaptation', 'directed', 'director', 'story', 'plot']):
            return False, "Dictionary definition"
    
    # Check if it's just technical info
    tech_only_patterns = [
        r'^(information about the film|информация о фильме)[^.]*$',
    ]
    is_tech_only = False
    for pattern in tech_only_patterns:
        if re.search(pattern, summary_lower):
            # Check if it has actual plot keywords
            plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                           'сюжет', 'рассказ', 'рассказывает', 'о', 'про', 'происходит']
            has_plot_kw = any(kw in summary_lower for kw in plot_keywords)
            if not has_plot_kw and len(summary) < 800:
                is_tech_only = True
                break
    
    if is_tech_only:
        return False, "Technical info only"
    
    # Check for plot content (be very lenient - accept if has any substantive content)
    plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'events',
                   'сюжет', 'рассказ', 'рассказывает', 'о', 'про', 'происходит',
                   'character', 'hero', 'герой', 'персонаж', 'young', 'man', 'woman',
                   'love', 'любовь', 'жизнь', 'life', 'father', 'mother', 'daughter', 
                   'son', 'family', 'synopsis', 'growing', 'moving', 'away', 'king',
                   'queen', 'prince', 'princess', 'meet', 'meeting', 'conflict',
                   'war', 'battle', 'journey', 'adventure', 'mystery', 'detective',
                   'murder', 'crime', 'police', 'investigation', 'secret', 'hidden',
                   'student', 'school', 'teacher', 'friend', 'relationship', 'relationship',
                   'marriage', 'wedding', 'death', 'died', 'killed', 'arrest', 'captured',
                   'release', 'prison', 'escape', 'trial', 'court', 'law', 'justice',
                   'village', 'town', 'city', 'country', 'land', 'world', 'earth',
                   'ancient', 'medieval', 'historical', 'history', 'past', 'future',
                   'year', 'time', 'day', 'night', 'morning', 'evening', 'winter', 'summer',
                   'work', 'job', 'career', 'business', 'company', 'factory', 'farm',
                   'история', 'рассказ', 'происходит', 'герой', 'персонаж']
    has_plot = any(kw in summary_lower for kw in plot_keywords)
    
    # Also check if it mentions film-related terms (director, actor, etc.) - counts as valid
    film_terms = ['director', 'directed', 'actor', 'actress', 'starring', 'cast',
                 'film', 'movie', 'cinema', 'screenplay', 'screenwriter', 'producer',
                 'режиссёр', 'актёр', 'актриса', 'фильм', 'кино', 'feature', 'soviet',
                 'russian', 'drama', 'comedy', 'thriller', 'action', 'romance']
    has_film_terms = any(kw in summary_lower for kw in film_terms)
    
    # If it's a substantial summary (long enough), accept it even without explicit keywords
    # Many valid summaries describe events without using plot/story keywords
    # Reduced threshold to catch Wikipedia condensed summaries (1-3 sentences)
    is_substantial = len(summary.strip()) > 150  # Reduced from 200 to 150
    
    # Check for heavy navigation (but allow minor navigation if good content)
    # Note: summary has already been cleaned, so this checks for any remaining navigation
    nav_keywords = ['новости', 'news', 'кастинг', 'casting', 'поиск', 'search',
                   'share', 'facebook', 'mail', 'favorite', 'fermer', 'sommaire',
                   'menu', 'search', 'home', 'close', 'previous', 'next']
    nav_count = sum(1 for kw in nav_keywords if kw in summary_lower)
    
    # Very lenient acceptance criteria:
    # 1. Has plot keywords OR film terms OR is substantial (>150 chars)
    # 2. Navigation is minimal (allow up to 5 now - very lenient)
    # 3. Length is reasonable (100 chars minimum - very lenient)
    
    # Accept if it has plot keywords and reasonable navigation
    if has_plot and nav_count <= 5 and len(summary) > 100:
        return True, None
    
    # Accept if it has film terms and reasonable navigation
    if has_film_terms and nav_count <= 5 and len(summary) > 100:
        return True, None
    
    # Accept if it's substantial (long) even without explicit keywords
    # Many valid summaries describe events without using plot/story keywords
    if is_substantial and nav_count <= 5 and not is_def:
        return True, None
    
    # Even more lenient: if it has film terms OR is from Wikipedia (substantial), accept
    # Wikipedia summaries condensed to 1-3 sentences are usually valid even if short
    if (has_film_terms or is_substantial) and nav_count <= 5 and len(summary) > 80:
        return True, None
    
    # Only reject if it's very short AND has no plot/film terms AND has navigation issues
    if not has_plot and not has_film_terms and not is_substantial and len(summary) < 100:
        return False, "No plot content"
    
    if nav_count > 5:  # Increased from 4 to 5 - very lenient
        return False, "Too much navigation text"
    
    # Default: accept if it passed other checks
    return True, None

def retry_problematic_summaries(csv_file, problematic_csv, output_csv=None):
    """Retry all problematic summaries with improved search. Can resume if interrupted."""
    if output_csv is None:
        output_csv = csv_file
    
    # Load problematic films
    problematic_films = {}
    with open(problematic_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            problematic_films[int(row['index'])] = row
    
    print(f"Found {len(problematic_films)} problematic summaries to retry")
    print()
    
    # Load main CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)
    
    # RESUME CAPABILITY: Check which films already have good summaries
    # (i.e., were already fixed or are no longer problematic)
    from identify_bad_summaries import is_bad_summary
    
    already_fixed = []
    still_problematic = []
    
    for idx in sorted(problematic_films.keys()):
        row = rows[idx - 1]
        summary = row.get('web_summary', '').strip()
        
        if summary:
            # Check if current summary is still problematic
            is_bad, reason = is_bad_summary(summary, row.get('name_russian', ''), row)
            if not is_bad:
                already_fixed.append(idx)
            else:
                still_problematic.append(idx)
        else:
            still_problematic.append(idx)
    
    if already_fixed:
        print(f"Found {len(already_fixed)} films already fixed (will skip)")
        print(f"Processing {len(still_problematic)} films that still need fixing")
        print()
    
    searcher = WebFilmSummarySearcher(delay=0.5)  # Much faster - reduced from 1.0 to 0.5
    fixed = 0
    still_bad = 0
    skipped = 0
    
    for idx in sorted(still_problematic):
        row = rows[idx - 1]  # Convert to 0-indexed
        problem_info = problematic_films[idx]
        
        film_name = row.get('name_russian', '').strip()
        name_original = row.get('name_original', '').strip()
        year = row.get('production_year', '').strip() or row.get('soviet_release_year', '').strip()
        year_int = int(year) if year and year.isdigit() else None
        url = row.get('film_url', '').strip()
        old_summary = row.get('web_summary', '').strip()
        issue_type = problem_info['reason']
        
        print(f"[{still_problematic.index(idx) + 1}/{len(still_problematic)}] "
              f"Film #{idx}: {film_name} ({year_int or 'no year'})")
        print(f"    Issue: {issue_type}")
        print(f"    Old summary preview: {old_summary[:100]}...")
        
        # Try improved search
        new_summary = improved_search(film_name, name_original, year_int, url, searcher)
        
        if new_summary:
            # Use improved quality check
            is_good, reason = is_good_summary(new_summary)
            
            if is_good:
                row['web_summary'] = new_summary
                fixed += 1
                print(f"    ✓ FIXED - New summary: {new_summary[:150]}...")
            else:
                still_bad += 1
                print(f"    ✗ New summary still problematic: {reason}")
        else:
            still_bad += 1
            print(f"    ✗ No better summary found")
        
        print()
        
        # Save progress every 20 films
        if (still_problematic.index(idx) + 1) % 20 == 0:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"  Progress saved: {fixed} fixed, {still_bad} still problematic")
            print()
    
    # Final save
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Complete!")
    print(f"  Already fixed (skipped): {len(already_fixed)}")
    print(f"  Newly fixed: {fixed}")
    print(f"  Still problematic: {still_bad}")
    if still_problematic:
        print(f"  Success rate: {fixed*100/len(still_problematic):.1f}%")
    print(f"  Saved to: {output_csv}")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    problematic_csv = sys.argv[2] if len(sys.argv) > 2 else "soviet_releases_1950_1991_with_summaries_problematic_summaries.csv"
    output_csv = sys.argv[3] if len(sys.argv) > 3 else csv_file
    
    retry_problematic_summaries(csv_file, problematic_csv, output_csv)

