"""
Fix all remaining anomalous summaries (494 films).
Prioritizes bot messages, dictionary definitions, and other problematic content.
Uses improved search strategies and quality checks.
"""
import csv
import sys
import time
import re
from search_film_summaries import WebFilmSummarySearcher
from retry_missing_summaries import aggressive_translate
from retry_problematic_summaries_improved import clean_navigation_text, is_good_summary

def verify_soviet_era_final(summary, film_year, film_name):
    """Final verification - rejects only obviously wrong content."""
    if not summary:
        return False, "No summary"
    
    summary_lower = summary.lower()
    
    # Reject IMDb cast/crew lists (technical info without plot)
    imdb_patterns = [
        r'cast\s*&\s*crew',
        r'user\s*reviews',
        r'imdbpro',
        r'(in credits order)',
        r'(complete, awaiting verification)',
        r'(jump to)',
        r'director\s*\(\d+\)',
        r'writer\s*\(\d+\)',
        r'producer\s*\(\d+\)',
        r'cinematographer\s*\(\d+\)',
        r'editor\s*\(\d+\)',
        r'production\s*designer\s*\(\d+\)',
        r'art\s*director\s*\(\d+\)',
        r'makeup\s*department',
        r'production\s*management',
        r'second\s*unit',
        r'assistant\s*director',
        r'sound\s*department',
        r'camera\s*and\s*electrical',
        r'music\s*department',
        r'see agents for this',
        r'contribute to this page',
        r'suggest an edit',
        r'more from this title'
    ]
    
    # Check if summary is primarily IMDb technical info
    imdb_count = sum(1 for pattern in imdb_patterns if re.search(pattern, summary_lower))
    
    # If it has many IMDb patterns and no plot keywords in first 500 chars, reject
    if imdb_count >= 3:
        first_500 = summary_lower[:500]
        plot_keywords_in_start = any(kw in first_500 for kw in ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'сюжет', 'рассказ'])
        if not plot_keywords_in_start:
            return False, "IMDb cast/crew list (no plot)"
    
    # Reject bot messages
    bot_messages = [
        'please confirm that you', 'you are not a robot', 'automated requests',
        'captcha', 'verify you are human', 'bot detected', 'we are sorry',
        'sort by:', 'price:', 'sponsored', 'shop on ebay', 'best offer',
        '1-16 of', 'results for', 'newest arrivals', 'best sellers'
    ]
    if any(msg in summary_lower[:500] for msg in bot_messages):
        return False, "Bot message/search result"
    
    # Reject modern years (2000+) as primary content
    modern_years = re.findall(r'\b(20[0-2]\d)\b', summary)
    if modern_years:
        years_found = [int(y) for y in modern_years if int(y) >= 2000]
        if years_found and summary_lower.count('202') + summary_lower.count('201') + summary_lower.count('200') > 2:
            return False, f"Too many modern year references: {years_found[:3]}"
    
    # Reject clearly wrong films
    wrong_films = ['lord of the rings', 'gandalf', 'frodo', 'aragorn', 'sauron', 'hobbit']
    if any(kw in summary_lower for kw in wrong_films):
        return False, "Wrong film (Lord of the Rings)"
    
    # Reject if it's clearly a dictionary definition with no film context
    definition_start = re.match(r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)', summary_lower)
    if definition_start:
        if 'film' not in summary_lower[:300] and 'movie' not in summary_lower[:300] and 'фильм' not in summary_lower[:300]:
            return False, "Dictionary definition without film context"
    
    return True, "OK"

def translate_with_fallbacks(text):
    """Try multiple translation methods with retries."""
    if not text:
        return None, False
    
    has_cyrillic = bool(re.search(r'[А-Яа-яЁё]', text))
    if not has_cyrillic:
        return text, True
    
    # Method 1: Aggressive translate (with retry and longer delays)
    for attempt in range(3):  # Increased retries
        try:
            if attempt > 0:
                time.sleep(2 * attempt)  # Progressive delay: 2s, 4s
            translated = aggressive_translate(text)
            if translated and len(translated.strip()) > 40:
                if not re.search(r'[А-Яа-яЁё]', translated):
                    return translated, True
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))  # Wait longer before retry
                continue
            pass
    
    # Method 2: Google Translator with auto-detect (with retry and longer delays)
    for attempt in range(3):  # Increased retries
        try:
            if attempt > 0:
                time.sleep(2 * attempt)  # Progressive delay: 2s, 4s
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='auto', target='en')
            # Try smaller chunks if text is very long
            chunk = text[:4000] if len(text) > 4000 else text
            translated = translator.translate(chunk)
            if translated and len(translated.strip()) > 40:
                # Check if it actually translated (not just returned original)
                if not re.search(r'[А-Яа-яЁё]', translated):
                    return translated, True
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))  # Wait longer before retry
                continue
            pass
    
    # Method 3: Explicit Russian->English (with retry and longer delays)
    for attempt in range(3):  # Increased retries
        try:
            if attempt > 0:
                time.sleep(2 * attempt)  # Progressive delay: 2s, 4s
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='ru', target='en')
            # Try smaller chunks if text is very long
            chunk = text[:4000] if len(text) > 4000 else text
            translated = translator.translate(chunk)
            if translated and len(translated.strip()) > 40:
                if not re.search(r'[А-Яа-яЁё]', translated):
                    return translated, True
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))  # Wait longer before retry
                continue
            pass
    
    # Method 4: Try sentence-by-sentence if long text (with longer delays)
    if len(text) > 500:
        try:
            from deep_translator import GoogleTranslator
            sentences = re.split(r'[.!?]+', text)
            translated_parts = []
            translator = GoogleTranslator(source='ru', target='en')  # Use explicit ru->en
            
            for i, sentence in enumerate(sentences[:15]):  # Increased to 15 sentences
                sentence = sentence.strip()
                if len(sentence) > 20:
                    try:
                        # Longer delay between sentences, especially after first few
                        if i > 0:
                            time.sleep(0.8 if i < 5 else 1.2)  # Progressive delay
                        
                        part = translator.translate(sentence[:1000])
                        if part and not re.search(r'[А-Яа-яЁё]', part):
                            translated_parts.append(part)
                    except Exception as e:
                        # If translation fails for a sentence, skip it but continue
                        time.sleep(1)  # Wait before next attempt
                        continue
            
            if translated_parts:
                translated = ' '.join(translated_parts)
                if len(translated.strip()) > 40:
                    return translated, True
        except:
            pass
    
    # Return original if translation fails (will be checked if valid Russian)
    return text, False

def find_better_summary_final(film_name, name_original, year, url=None):
    """Find better summary using multiple strategies."""
    searcher = WebFilmSummarySearcher(delay=0.5)
    
    # Strategy 1: Direct kino-teatr.ru if URL available (bypass with web search)
    # Skip this since kino-teatr.ru is blocked
    
    # Strategy 2: Wikipedia with explicit plot/synopsis keywords
    queries_wiki = []
    if name_original and name_original.strip():
        queries_wiki.extend([
            f'"{name_original}" {year} Soviet film plot synopsis',
            f'"{name_original}" {year} USSR film story',
        ])
    queries_wiki.extend([
        f'"{film_name}" {year} советский фильм сюжет',
        f'"{film_name}" {year} Soviet film plot',
    ])
    
    for query in queries_wiki[:4]:
        try:
            if name_original and name_original in query:
                search_name = name_original
            else:
                search_name = film_name
            
            summary = searcher.find_summary(search_name, year, name_original if name_original in query else None)
            
            if summary:
                # Check if this is from Wikipedia - Wikipedia plot sections are generally reliable
                # even if they don't have explicit plot keywords after condensing
                is_from_wikipedia = 'wikipedia' in str(query).lower() or 'wikipedia' in str(summary).lower()
                
                cleaned = clean_navigation_text(summary)
                
                # Check if it's still in Russian and try to translate
                has_cyrillic = bool(re.search(r'[А-Яа-яЁё]', cleaned))
                
                translated, is_english = translate_with_fallbacks(cleaned)
                
                # If translation failed but we have Russian text, check if it has plot content in Russian
                if not is_english and has_cyrillic and translated:
                    # Check for Russian plot keywords - if it has plot content, try harder
                    russian_plot_keywords = ['сюжет', 'рассказ', 'рассказывает', 'про', 'происходит', 
                                            'о фильме', 'фильм рассказывает', 'фильм о', 'рассказывает о',
                                            'история', 'события', 'происходит', 'главный', 'герой',
                                            'фильм повествует', 'рассказ о', 'история о']
                    russian_action_keywords = ['идет', 'приходит', 'уходит', 'возвращается', 'встречает',
                                              'находит', 'обнаруживает', 'пытается', 'становится', 'становятся']
                    has_russian_plot = any(kw in cleaned.lower() for kw in russian_plot_keywords)
                    has_russian_action = any(kw in cleaned.lower() for kw in russian_action_keywords)
                    
                    if has_russian_plot or has_russian_action or len(cleaned) > 200:
                        # It has plot content in Russian - try harder to translate
                        # Maybe chunk it or use a different approach
                        if len(cleaned) > 2000:
                            # Try translating first 2000 chars
                            translated, is_english = translate_with_fallbacks(cleaned[:2000])
                        else:
                            translated, is_english = translate_with_fallbacks(cleaned)
                        
                        # If translation still failed but we have substantial Russian text with plot,
                        # we could accept it, but let's try one more time with explicit ru->en
                        if not is_english and has_cyrillic:
                            try:
                                from deep_translator import GoogleTranslator
                                import time as time_module
                                time_module.sleep(0.5)  # Brief delay
                                translator = GoogleTranslator(source='ru', target='en')
                                # Try smaller chunks
                                chunk = cleaned[:1500] if len(cleaned) > 1500 else cleaned
                                final_trans = translator.translate(chunk)
                                if final_trans and len(final_trans.strip()) > 40:
                                    if not re.search(r'[А-Яа-яЁё]', final_trans):
                                        translated = final_trans
                                        is_english = True
                            except:
                                pass
                        
                        # If translation still failed but we have substantial Russian text with plot content,
                        # accept it anyway - it's better than nothing, and we can translate later
                        if not is_english and has_cyrillic and translated:
                            # Check if it has substantial plot content
                            if (has_russian_plot or has_russian_action) and len(translated.strip()) > 100:
                                # Accept the Russian summary - it has plot content
                                # The quality checks will still run, but won't reject it for being Russian
                                # We'll mark it as needing translation later
                                pass  # Continue to quality checks with Russian text
                            else:
                                # Not enough plot content, skip
                                continue
                
                # Check for bot messages in the original cleaned text BEFORE translation
                # Bot messages are often returned when sites block us
                cleaned_lower = cleaned.lower()
                if any(bad in cleaned_lower[:500] for bad in [
                    'please confirm', 'you are not a robot', 'automated requests',
                    'we\'re sorry, but it looks like requests', 'after checkbox',
                    'captcha', 'verify you are human', 'bot detected'
                ]):
                    continue  # Skip bot detection messages
                
                if translated and len(translated.strip()) > 50:
                    # Early bot check in translated text too
                    translated_lower = translated.lower()
                    if any(bad in translated_lower[:300] for bad in [
                        'please confirm', 'you are not a robot', 'sort by:', 
                        'price:', 'sponsored', 'results for', 'shop on',
                        'automated requests', 'after checkbox', 'captcha'
                    ]):
                        continue
                    
                    # Early rejection: Must NOT start with navigation/metadata or be a film list
                    first_300 = translated_lower[:300]
                    navigation_starts = [
                        'films ', 'film ', 'about the film', 'creators and actors',
                        'video review', 'stills', 'publications', 'film in collection',
                        'please confirm', 'you are not a robot', 'automated',
                        'director (', 'writer (', 'cast & crew', 'imdbpro',
                        'of eduard', 'you are not alone', 'trains go past'
                    ]
                    if any(nav in first_300 for nav in navigation_starts):
                        continue  # Skip summaries that start with navigation/metadata
                    
                    # Reject if it looks like a list of films (has multiple year references)
                    year_pattern = r'\(\d{4}\)'
                    year_matches = len(re.findall(year_pattern, translated[:500]))
                    if year_matches >= 3:
                        # If it has 3+ year references, it's likely a filmography list
                        if not any(kw in translated_lower for kw in ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'synopsis']):
                            continue  # Skip filmography lists
                    
                    is_valid, reason = verify_soviet_era_final(translated, year, film_name)
                    if is_valid:
                        # Check for plot content - be lenient
                        plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                                        'сюжет', 'рассказ', 'рассказывает', 'про', 'происходит',
                                        'synopsis', 'tells the story', 'follows the', 'is about']
                        has_plot = any(kw in translated_lower for kw in plot_keywords)
                        
                        action_words = ['meets', 'meeting', 'falls', 'leaves', 'returns', 'discovers',
                                       'finds', 'tries', 'goes', 'comes', 'becomes', 'wins', 'saves',
                                       'works', 'lives', 'dies', 'struggles', 'travels']
                        has_action = any(kw in translated_lower for kw in action_words)
                        
                        event_indicators = ['character', 'hero', 'protagonist', 'main character',
                                           'young', 'man', 'woman', 'boy', 'girl', 'father', 'mother',
                                           'village', 'town', 'city', 'country', 'war', 'battle',
                                           'journey', 'adventure', 'mystery', 'conflict', 'struggle',
                                           'family', 'son', 'daughter']
                        has_events = any(kw in translated_lower for kw in event_indicators)
                        
                        # Reject blog posts, quotes, marketing text
                        bad_patterns = [
                            'jan ', 'feb ', 'mar ', 'pm et', 'linkedin', 'flipboard',
                            'i\'m lookin\'', 'i\'m thinkin\'', 'i\'m ', 'i was', 'i got',
                            'beautiful, interesting, incredible', 'see what\'s playing',
                            'by: ', 'published', 'blog'
                        ]
                        is_bad_content = any(pattern in translated_lower[:200] for pattern in bad_patterns)
                        
                        if is_bad_content:
                            continue
                        
                        # Accept if narrative OR substantial with film content
                        # OR if it's from Wikipedia (Wikipedia plot sections are reliable)
                        has_narrative = has_plot or has_action or has_events
                        is_substantial = len(translated) > 200 and (
                            'film' in translated_lower or 'movie' in translated_lower or
                            'character' in translated_lower
                        )
                        
                        # Trust Wikipedia summaries more - they're usually good even if condensed
                        # Also accept Russian summaries from Wikipedia if they have plot content
                        if is_from_wikipedia and len(translated.strip()) > 100:
                            # Wikipedia summaries are generally reliable plot summaries
                            # Check quality (will work even if still in Russian)
                            is_good, check_reason = is_good_summary(translated)
                            if is_good or (not has_bad_content and len(translated.strip()) > 150):
                                # Even if still in Russian, accept it if it has plot content
                                # Check if it has Russian plot keywords (if translation failed)
                                if has_cyrillic:
                                    # Still has Cyrillic - check for Russian plot keywords
                                    if has_russian_plot or has_russian_action or len(translated.strip()) > 200:
                                        return translated  # Accept Russian summary with plot content
                                else:
                                    # No Cyrillic - it's translated, accept it
                                    return translated
                        
                        if not has_narrative and not is_substantial:
                            continue
                        
                        is_good, check_reason = is_good_summary(translated)
                        if is_good:
                            return translated
                        elif is_english and len(translated) > 150 and (has_plot or has_action or has_events):
                            # Accept if substantial and has any narrative content
                            return translated
                        elif not is_english and has_cyrillic and (has_russian_plot or has_russian_action) and len(translated.strip()) > 150:
                            # Accept Russian summary if it has plot content - better than nothing
                            # We can translate it later
                            is_good_ru, _ = is_good_summary(translated)
                            if is_good_ru:
                                return translated
                        elif not is_english and has_cyrillic:
                            # If still in Russian, try one more time to translate
                            final_trans, final_english = translate_with_fallbacks(translated)
                            if final_english and len(final_trans.strip()) > 100:
                                final_lower = final_trans.lower()
                                has_plot_final = any(kw in final_lower for kw in plot_keywords)
                                has_action_final = any(kw in final_lower for kw in action_words)
                                has_events_final = any(kw in final_lower for kw in event_indicators)
                                if has_plot_final or has_action_final or has_events_final:
                                    is_good_final, _ = is_good_summary(final_trans)
                                    if is_good_final:
                                        return final_trans
        except:
            continue
        time.sleep(0.3)
    
    # Strategy 3: Web search with explicit plot/synopsis queries
    search_queries = []
    if name_original:
        search_queries.append(f'"{name_original}" {year} Soviet film plot synopsis story')
        search_queries.append(f'"{name_original}" {year} film what happens story')
    
    search_queries.extend([
        f'"{film_name}" {year} советский фильм сюжет описание что происходит',
        f'"{film_name}" {year} Soviet film plot what happens',
        f'"{film_name}" {year} film synopsis story',
    ])
    
    for query in search_queries[:3]:
        try:
            results = searcher.get_search_results(query)
            for result in results[:4]:
                url_to_check = result['url']
                
                # Skip bad sources
                if any(skip in url_to_check.lower() for skip in 
                       ['/search', '/login', 'wiktionary', 'dictionary',
                        'youtube.com/watch', 'rutube.ru/watch', 'vk.com/video',
                        'thebatt.com', 'ebay.com', 'amazon.com']):
                    continue
                
                try:
                    if result != results[0]:
                        time.sleep(searcher.delay)
                    
                    import requests
                    response = requests.get(url_to_check, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        summary = searcher.extract_text_from_page(response.text, url_to_check)
                        if summary:
                            summary_lower = summary.lower()
                            
                            # Skip bot messages and e-commerce
                            if any(bad in summary_lower[:300] for bad in [
                                'please confirm', 'captcha', 'bot detected',
                                'results for', 'sort by:', 'sponsored', 'price:',
                                'shop on', 'buy now', 'click here'
                            ]):
                                continue
                            
                            # Check for bot messages BEFORE cleaning
                            summary_lower_check_raw = summary.lower()
                            if any(bad in summary_lower_check_raw[:500] for bad in [
                                'please confirm', 'you are not a robot', 'automated requests',
                                'we\'re sorry, but it looks like requests', 'after checkbox',
                                'captcha', 'verify you are human', 'bot detected'
                            ]):
                                continue  # Skip bot detection messages
                            
                            summary = clean_navigation_text(summary)
                            
                            # Early rejection of IMDb cast/crew lists
                            summary_lower_check = summary.lower()
                            imdb_patterns_check = [
                                'cast & crew', 'in credits order', 'complete, awaiting verification',
                                'director (', 'writer (', 'producer (', 'cinematographer (',
                                'see agents for this', 'contribute to this page'
                            ]
                            if sum(1 for p in imdb_patterns_check if p in summary_lower_check) >= 2:
                                # Check if it has plot in first part
                                if not any(kw in summary_lower_check[:300] for kw in ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'сюжет']):
                                    continue  # Skip IMDb cast/crew lists
            
                            translated, is_english = translate_with_fallbacks(summary)
                            
                            # If translation failed, try one more explicit attempt
                            if not is_english and translated and re.search(r'[А-Яа-яЁё]', summary):
                                try:
                                    from deep_translator import GoogleTranslator
                                    time.sleep(0.3)  # Use module-level time
                                    translator = GoogleTranslator(source='ru', target='en')
                                    chunk = summary[:2000] if len(summary) > 2000 else summary
                                    translated = translator.translate(chunk)
                                    if translated and len(translated.strip()) > 40:
                                        if not re.search(r'[А-Яа-яЁё]', translated):
                                            is_english = True
                                except:
                                    pass
                            
                            if translated and len(translated.strip()) > 50:
                                translated_lower = translated.lower()
                                
                                # Skip if still has bot messages
                                if any(bad in translated_lower[:300] for bad in [
                                    'please confirm', 'sort by:', 'results for', 'shop on'
                                ]):
                                    continue
                                
                                # Early rejection: Must NOT start with navigation/metadata or be a film list
                                first_300 = translated_lower[:300]
                                navigation_starts = [
                                    'films ', 'film ', 'about the film', 'creators and actors',
                                    'video review', 'stills', 'publications', 'film in collection',
                                    'please confirm', 'you are not a robot', 'automated',
                                    'director (', 'writer (', 'cast & crew', 'imdbpro',
                                    'information about the film', 'информация о фильме',
                                    'of eduard', 'you are not alone', 'trains go past'
                                ]
                                if any(nav in first_300 for nav in navigation_starts):
                                    continue  # Skip summaries that start with navigation/metadata
                                
                                # Reject if it looks like a list of films (has multiple year references)
                                year_pattern = r'\(\d{4}\)'
                                year_matches = len(re.findall(year_pattern, translated[:500]))
                                has_bad_content = False
                                if year_matches >= 3:
                                    # If it has 3+ year references, it's likely a filmography list
                                    if not any(kw in translated_lower for kw in ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'synopsis']):
                                        has_bad_content = True  # Skip filmography lists
                                
                                if has_bad_content:
                                    continue
                                
                                is_valid, reason = verify_soviet_era_final(translated, year, film_name)
                                if is_valid:
                                    # Must have plot keywords for acceptance (not just film terms)
                                    plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 
                                                    'сюжет', 'рассказ', 'рассказывает', 'про', 'происходит',
                                                    'synopsis', 'tells the story', 'follows the', 'is about',
                                                    'tells about', 'tells of', 'depicts', 'describes',
                                                    'narrates', 'chronicles', 'recounts', 'revolves around',
                                                    'centers on', 'focuses on', 'deals with', 'concerns',
                                                    'what happens', 'happens when', 'takes place', 'set in',
                                                    'tells of', 'revolves', 'centers', 'focuses']
                                    has_plot = any(kw in translated_lower for kw in plot_keywords)
                                    
                                    # Also check for action/event words that indicate plot (must be in context)
                                    action_words = ['meets', 'meeting', 'falls', 'falling', 'leaves', 'leaving',
                                                   'returns', 'returning', 'discovers', 'discovers', 'finds',
                                                   'finding', 'tries', 'trying', 'attempts', 'attempting',
                                                   'goes', 'going', 'comes', 'coming', 'becomes', 'becoming',
                                                   'wins', 'winning', 'loses', 'losing', 'saves', 'saving',
                                                   'escapes', 'escaping', 'hides', 'hiding', 'fights', 'fighting',
                                                   'falls in love', 'meets a', 'discovers that', 'finds out',
                                                   'tries to', 'attempts to', 'goes to', 'comes to', 'returns to']
                                    has_action = any(kw in translated_lower for kw in action_words)
                                    
                                    # Must have substantial plot content - reject if it's just metadata
                                    # Check if it's describing events/characters vs just listing info
                                    event_indicators = ['character', 'hero', 'protagonist', 'main character',
                                                       'young', 'man', 'woman', 'boy', 'girl', 'father', 'mother',
                                                       'village', 'town', 'city', 'country', 'war', 'battle',
                                                       'journey', 'adventure', 'mystery', 'conflict', 'struggle']
                                    has_events = any(kw in translated_lower for kw in event_indicators)
                                    
                                    # Require either plot keywords OR action words OR event indicators
                                    # (Any of these indicates narrative content)
                                    if not has_plot and not has_action and not has_events:
                                        continue  # Skip summaries without actual plot content
                                    
                                    is_good, check_reason = is_good_summary(translated)
                                    if is_good:
                                        return translated
                                    elif is_english and len(translated) > 150 and (has_plot or has_action):
                                        # Accept if substantial and has plot/action keywords
                                        return translated
                except:
                    continue
        except:
            continue
        time.sleep(0.3)
    
    return None

def is_still_problematic(summary, issues, verify_func):
    """Check if a summary is still problematic based on the original issues."""
    if not summary or len(summary.strip()) < 50:
        return True, "Empty or too short"
    
    summary_lower = summary.lower()
    
    # Check for bot messages (if originally flagged)
    if 'bot message' in issues.lower() or 'search result' in issues.lower():
        bot_messages = [
            'please confirm', 'you are not a robot', 'automated requests',
            'captcha', 'sort by:', 'price:', 'sponsored', 'shop on ebay',
            '1-16 of', 'results for', 'backcast & crew', 'jump to'
        ]
        if any(msg in summary_lower[:500] for msg in bot_messages):
            return True, "Still has bot message/search result"
        
        # Check for IMDb cast/crew lists
        imdb_patterns = [
            'cast & crew', 'in credits order', 'complete, awaiting verification',
            'director (', 'writer (', 'producer (', 'cinematographer (',
            'see agents for this', 'contribute to this page'
        ]
        if sum(1 for p in imdb_patterns if p in summary_lower) >= 3:
            if not any(kw in summary_lower[:300] for kw in ['plot', 'story', 'tells', 'follows', 'about', 'narrative', 'сюжет']):
                return True, "Still has IMDb cast/crew list"
    
    # Check for dictionary definitions (if originally flagged)
    if 'dictionary' in issues.lower():
        definition_patterns = [
            r'^[^.]*\s+(is|means|refers to|denotes)\s+(a|an|the)\s+(?!.*film)',
        ]
        for pattern in definition_patterns:
            if re.match(pattern, summary, re.IGNORECASE):
                if 'film' not in summary_lower[:300] and 'movie' not in summary_lower[:300] and 'фильм' not in summary_lower[:300]:
                    return True, "Still a dictionary definition"
    
    # Check for wrong timeline (if originally flagged)
    if 'wrong timeline' in issues.lower():
        modern_years = re.findall(r'\b(20[0-2]\d)\b', summary)
        if modern_years:
            years_found = [int(y) for y in modern_years if int(y) >= 2000]
            if years_found and summary_lower.count('202') + summary_lower.count('201') + summary_lower.count('200') > 2:
                return True, "Still has modern years"
        
        modern_tech = ['internet', 'website', 'online', 'streaming', 'youtube', 'rutube', 'facebook']
        if any(tech in summary_lower for tech in modern_tech):
            return True, "Still has modern technology"
    
    # Final verification check
    is_valid, reason = verify_func(summary, None, "")
    if not is_valid:
        return True, f"Verification failed: {reason}"
    
    # Check quality
    is_good, check_reason = is_good_summary(summary)
    if not is_good:
        return True, f"Quality check failed: {check_reason}"
    
    return False, None

def fix_all_anomalies(csv_file, anomalies_csv, output_csv=None):
    """Fix all anomalous summaries with checkpoint/resume capability."""
    if output_csv is None:
        output_csv = csv_file
    
    # Load main CSV first to check current state
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            rows.append(row)
    
    # Load anomalies
    anomaly_indices = []
    anomaly_info = {}
    with open(anomalies_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row['index'])
            anomaly_indices.append(idx)
            anomaly_info[idx] = row
    
    print(f"Found {len(anomaly_indices)} films originally identified with anomalies")
    print()
    
    # CHECKPOINT: Check which films still need fixing
    already_fixed = []
    still_problematic_indices = []
    
    print("Checking which films still need fixing...")
    for idx in sorted(anomaly_indices):
        if idx > len(rows):
            continue
        
        row = rows[idx - 1]
        summary = row.get('web_summary', '').strip()
        issues = anomaly_info[idx]['issues']
        
        # Check if still problematic
        is_still_bad, reason = is_still_problematic(summary, issues, verify_soviet_era_final)
        if is_still_bad:
            still_problematic_indices.append(idx)
        else:
            already_fixed.append(idx)
    
    if already_fixed:
        print(f"✓ Found {len(already_fixed)} films already fixed (will skip)")
    print(f"  Processing {len(still_problematic_indices)} films that still need fixing")
    print()
    
    if not still_problematic_indices:
        print("✓ All anomalies have been fixed!")
        return
    
    searcher = WebFilmSummarySearcher(delay=0.5)
    fixed = 0
    failed = 0
    skipped = 0
    
    for idx in still_problematic_indices:
        if idx > len(rows):
            skipped += 1
            continue
        
        row = rows[idx - 1]
        film_name = row.get('name_russian', '').strip()
        name_original = row.get('name_original', '').strip()
        year_str = row.get('production_year', '').strip() or row.get('soviet_release_year', '').strip()
        year = int(year_str) if year_str and year_str.isdigit() else None
        url = row.get('film_url', '').strip()
        old_summary = row.get('web_summary', '').strip()
        issues = anomaly_info[idx]['issues'] if idx in anomaly_info else 'Unknown'
        
        print(f"[{still_problematic_indices.index(idx) + 1}/{len(still_problematic_indices)}] "
              f"Film #{idx}: {film_name} ({year or 'no year'})")
        
        # Show main issue
        if 'bot message' in issues.lower() or 'search result' in issues.lower():
            print(f"    Issue: Bot message/search result")
        elif 'dictionary' in issues.lower():
            print(f"    Issue: Dictionary definition")
        elif 'too short' in issues.lower():
            print(f"    Issue: Too short/non-plot")
        elif 'wrong timeline' in issues.lower():
            print(f"    Issue: Wrong timeline")
        else:
            print(f"    Issue: {issues.split(';')[0][:50]}")
        
        print(f"    Old preview: {old_summary[:100]}...")
        
        # Try to find better summary
        new_summary = find_better_summary_final(film_name, name_original, year, url)
        
        if new_summary:
            # Final verification
            is_valid, reason = verify_soviet_era_final(new_summary, year, film_name)
            if is_valid:
                is_good, check_reason = is_good_summary(new_summary)
                if is_good:
                    # Final check: ensure it's actually a plot summary, not navigation/metadata
                    summary_lower = new_summary.lower()
                    first_200 = summary_lower[:200]
                    
                    # Reject if it starts with navigation
                    navigation_starts = [
                        'films ', 'film ', 'about the film', 'creators and actors',
                        'video review', 'stills', 'publications', 'film in collection',
                        'please confirm', 'you are not a robot', 'automated',
                        'director (', 'writer (', 'cast & crew', 'imdbpro',
                        'information about the film', 'информация о фильме'
                    ]
                    if any(nav in first_200 for nav in navigation_starts):
                        failed += 1
                        print(f"    ✗ Rejected: Starts with navigation/metadata")
                    else:
                        # Must have plot or action keywords
                        plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                                        'synopsis', 'tells the story', 'follows the', 'is about']
                        action_words = ['meets', 'meeting', 'falls', 'leaves', 'returns', 'discovers',
                                       'finds', 'tries', 'goes', 'comes', 'becomes', 'wins', 'saves',
                                       'works', 'lives', 'dies', 'struggles', 'travels']
                        event_indicators = ['character', 'hero', 'protagonist', 'man', 'woman',
                                           'village', 'town', 'city', 'war', 'battle', 'journey',
                                           'family', 'father', 'mother', 'son', 'daughter']
                        
                        has_narrative = any(kw in summary_lower for kw in plot_keywords + action_words + event_indicators)
                        is_substantial = len(new_summary) > 200 and (
                            'film' in summary_lower or 'movie' in summary_lower or 'character' in summary_lower
                        )
                        
                        # Reject obvious non-plot content
                        bad_patterns = ['jan ', 'feb ', 'pm et', 'linkedin', 'i\'m lookin\'', 
                                       'i\'m thinkin\'', 'beautiful, interesting, incredible',
                                       'by: ', 'published', 'blog']
                        is_bad = any(pattern in summary_lower[:200] for pattern in bad_patterns)
                        
                        if is_bad:
                            failed += 1
                            print(f"    ✗ Rejected: Non-plot content (blog/quote/marketing)")
                        elif has_narrative or is_substantial:
                            row['web_summary'] = new_summary
                            fixed += 1
                            print(f"    ✓ FIXED - New summary: {new_summary[:150]}...")
                        else:
                            failed += 1
                            print(f"    ✗ Rejected: No plot/action keywords")
                elif len(new_summary) > 150:
                    # Check for narrative content before accepting borderline
                    summary_lower = new_summary.lower()
                    plot_keywords = ['plot', 'story', 'tells', 'follows', 'about', 'narrative',
                                    'synopsis', 'tells the story', 'follows the', 'is about']
                    action_words = ['meets', 'meeting', 'falls', 'leaves', 'returns', 'discovers',
                                   'finds', 'tries', 'goes', 'comes', 'becomes', 'works', 'lives',
                                   'dies', 'struggles', 'travels', 'saves', 'wins']
                    event_indicators = ['character', 'hero', 'protagonist', 'man', 'woman',
                                       'village', 'town', 'city', 'war', 'battle', 'journey',
                                       'family', 'father', 'mother', 'son', 'daughter']
                    
                    has_narrative = any(kw in summary_lower for kw in plot_keywords + action_words + event_indicators)
                    is_substantial = len(new_summary) > 200 and (
                        'film' in summary_lower or 'movie' in summary_lower or 'character' in summary_lower
                    )
                    
                    # Reject obvious non-plot content
                    bad_patterns = ['jan ', 'feb ', 'pm et', 'linkedin', 'i\'m lookin\'', 
                                   'i\'m thinkin\'', 'beautiful, interesting, incredible',
                                   'by: ', 'published', 'blog']
                    is_bad = any(pattern in summary_lower[:200] for pattern in bad_patterns)
                    
                    if is_bad:
                        failed += 1
                        print(f"    ✗ Rejected: Non-plot content (blog/quote/marketing)")
                    elif has_narrative or is_substantial:
                        row['web_summary'] = new_summary
                        fixed += 1
                        print(f"    ✓ FIXED (borderline) - New summary: {new_summary[:150]}...")
                    else:
                        failed += 1
                        print(f"    ✗ Quality check failed: No plot content")
                else:
                    failed += 1
                    print(f"    ✗ Quality check failed: {check_reason}")
            else:
                failed += 1
                print(f"    ✗ Verification failed: {reason}")
        else:
            failed += 1
            print(f"    ✗ No better summary found")
        
        print()
        
        # Save progress every 25 films
        if (still_problematic_indices.index(idx) + 1) % 25 == 0:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"  Progress saved: {fixed} fixed, {failed} failed, {skipped} skipped")
            print()
    
    # Final save
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Complete!")
    print(f"  Already fixed (skipped): {len(already_fixed)}")
    print(f"  Newly fixed: {fixed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    if len(still_problematic_indices) > 0:
        print(f"  Success rate: {fixed*100/(len(still_problematic_indices) - skipped):.1f}%")
    print(f"  Saved to: {output_csv}")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    anomalies_csv = sys.argv[2] if len(sys.argv) > 2 else "soviet_releases_1950_1991_with_summaries_anomalies_list.csv"
    output_csv = sys.argv[3] if len(sys.argv) > 3 else csv_file
    
    fix_all_anomalies(csv_file, anomalies_csv, output_csv)

