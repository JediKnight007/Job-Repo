"""
Script to retry finding and translating summaries for films that failed previously.
Uses more aggressive translation strategies including chunking and multiple attempts.
"""
import csv
import sys
from search_film_summaries import WebFilmSummarySearcher
from deep_translator import GoogleTranslator
import time
import re

def clean_cyrillic_text(text):
    """Remove any remaining Cyrillic characters from text."""
    if not text:
        return text
    # Remove Cyrillic characters (Unicode range U+0400 to U+04FF)
    cleaned = ''.join(char if not ('\u0400' <= char <= '\u04FF') else '' for char in text)
    # Clean up multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def aggressive_translate(text, max_attempts=5):
    """Try multiple translation strategies."""
    if not text:
        return None
    
    # Strategy 1: Full translation
    for attempt in range(max_attempts):
        try:
            translated = GoogleTranslator(source='ru', target='en').translate(text[:5000])
            if translated:
                # Check if mostly translated
                cyrillic_count = sum(1 for c in translated if '\u0400' <= c <= '\u04FF')
                total_chars = len(translated.replace(' ', ''))
                if total_chars > 0:
                    cyrillic_ratio = cyrillic_count / total_chars
                    if cyrillic_ratio < 0.1:  # Less than 10% Cyrillic - accept it
                        return translated
                    elif cyrillic_ratio < 0.3:  # Try cleaning
                        cleaned = clean_cyrillic_text(translated)
                        if cleaned and len(cleaned) > len(translated) * 0.5:
                            return cleaned
                time.sleep(0.5)
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1)
            continue
    
    # Strategy 2: Split into sentences and translate separately
    try:
        sentences = re.split(r'[.!?]+', text)
        translated_parts = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            try:
                translated_sent = GoogleTranslator(source='ru', target='en').translate(sentence[:500])
                if translated_sent and not any('\u0400' <= c <= '\u04FF' for c in translated_sent):
                    translated_parts.append(translated_sent)
                time.sleep(0.3)
            except:
                continue
        if translated_parts:
            return '. '.join(translated_parts) + '.'
    except:
        pass
    
    # Strategy 3: Try auto-detect
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text[:5000])
        if translated:
            cyrillic_count = sum(1 for c in translated if '\u0400' <= c <= '\u04FF')
            total_chars = len(translated.replace(' ', ''))
            if total_chars > 0 and cyrillic_count / total_chars < 0.2:
                return translated
    except:
        pass
    
    return None

def retry_missing_summaries(input_csv, output_csv):
    """Find and retry films without summaries."""
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        if 'web_summary' not in fieldnames:
            fieldnames.append('web_summary')
        for row in reader:
            if 'web_summary' not in row:
                row['web_summary'] = ''
            rows.append(row)
    
    missing = [(i, row) for i, row in enumerate(rows) if not row.get('web_summary', '').strip()]
    print(f"Found {len(missing)} films without summaries")
    print()
    
    searcher = WebFilmSummarySearcher(delay=1.5)
    found = 0
    not_found = 0
    
    for idx, (i, row) in enumerate(missing):
        film_name = row.get('name_russian', '').strip()
        name_original = row.get('name_original', '').strip()
        year = row.get('production_year', '').strip() or row.get('soviet_release_year', '').strip()
        year_int = int(year) if year and year.isdigit() else None
        
        print(f"[{idx+1}/{len(missing)}] Retrying: Film #{i+1} - {film_name} ({year_int or 'no year'})")
        
        # Try to find summary
        summary = searcher.find_summary(film_name, year_int, name_original)
        
        if summary:
            # Try aggressive translation
            print(f"    Found summary, attempting aggressive translation...")
            translated = aggressive_translate(summary)
            
            if translated:
                # Final check - remove any remaining Cyrillic
                has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in translated)
                if has_cyrillic:
                    # Clean it
                    translated = clean_cyrillic_text(translated)
                
                if translated and len(translated.strip()) > 50:
                    row['web_summary'] = translated
                    found += 1
                    print(f"    ✓ Successfully translated ({len(translated)} chars)")
                else:
                    not_found += 1
                    print(f"    ✗ Translation result too short or empty")
            else:
                not_found += 1
                print(f"    ✗ Could not translate summary")
        else:
            not_found += 1
            print(f"    ✗ No summary found")
        
        # Save progress every 5 films
        if (idx + 1) % 5 == 0:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"    Progress saved: {found} found, {not_found} not found")
            print()
    
    # Final save
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Complete!")
    print(f"  Found and translated: {found}")
    print(f"  Not found/failed: {not_found}")
    print(f"  Saved to: {output_csv}")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    retry_missing_summaries(input_file, output_file)

