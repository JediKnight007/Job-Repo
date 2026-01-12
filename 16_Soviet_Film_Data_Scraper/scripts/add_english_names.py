"""
Add English names column to CSV by looking up from film pages
Uses existing name_original where available, then looks up from film pages
"""
import csv
import sys
from main import KinoTeatrScraper

def add_english_names(input_file, output_file=None, start_idx=0, batch_size=100):
    """Add name_english column by looking up from film pages"""
    if output_file is None:
        output_file = input_file
    
    print(f"Reading {input_file}...")
    
    # Read all rows
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        # Add name_english column after name_russian if not exists
        if 'name_english' not in fieldnames:
            if 'name_russian' in fieldnames:
                idx = fieldnames.index('name_russian') + 1
                fieldnames.insert(idx, 'name_english')
            else:
                fieldnames.append('name_english')
        
        for row in reader:
            rows.append(row)
    
    print(f"  Found {len(rows)} total rows")
    
    # Find rows that need English names
    need_lookup = []
    has_english = 0
    
    for i, row in enumerate(rows):
        name_english = row.get('name_english', '').strip()
        name_original = row.get('name_original', '').strip()
        
        # If already has English name, skip
        if name_english and all(ord(c) < 128 for c in name_english):
            has_english += 1
            continue
        
        # Use name_original if it's in English
        if name_original and all(ord(c) < 128 for c in name_original):
            rows[i]['name_english'] = name_original
            has_english += 1
            continue
        
        # Need to look up
        need_lookup.append(i)
    
    print(f"  Already have English: {has_english}")
    print(f"  Need lookup: {len(need_lookup)}")
    
    if start_idx > 0:
        need_lookup = need_lookup[start_idx:]
        print(f"  Resuming from index {start_idx}")
    
    if not need_lookup:
        print("\n✓ All rows already have English names!")
        # Just save to ensure name_english column exists
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return output_file
    
    print(f"\nLooking up English names from film pages...")
    print(f"  This will process {len(need_lookup)} films")
    print(f"  Estimated time: ~{len(need_lookup) * 3 / 60:.1f} minutes\n")
    
    # Setup Selenium scraper
    scraper = KinoTeatrScraper(headless=True, delay=1)
    scraper.setup_driver()
    
    stats = {'found': 0, 'not_found': 0, 'errors': 0}
    
    try:
        for batch_num, row_idx in enumerate(need_lookup):
            row = rows[row_idx]
            film_url = row.get('film_url', '').strip()
            name_russian = row.get('name_russian', '').strip()
            
            if not film_url:
                stats['errors'] += 1
                continue
            
            try:
                # Look up from film page
                metadata = scraper.scrape_film_page(film_url)
                
                if metadata and metadata.get('name_original'):
                    name_original = metadata.get('name_original', '').strip()
                    # Check if it's in English (Latin characters)
                    if name_original and all(ord(c) < 128 for c in name_original):
                        rows[row_idx]['name_english'] = name_original
                        stats['found'] += 1
                        print(f"  [{batch_num+1}/{len(need_lookup)}] ✓ {name_russian[:35]:35} -> {name_original[:40]}")
                    else:
                        stats['not_found'] += 1
                else:
                    stats['not_found'] += 1
                    if (batch_num + 1) % 10 == 0:  # Only print every 10th to reduce noise
                        print(f"  [{batch_num+1}/{len(need_lookup)}] ✗ {name_russian[:35]:35} -> (not found)")
                
            except Exception as e:
                stats['errors'] += 1
                if (batch_num + 1) % 10 == 0:
                    print(f"  [{batch_num+1}/{len(need_lookup)}] ✗ Error: {name_russian[:30]} - {str(e)[:40]}")
            
            # Save progress every batch_size
            if (batch_num + 1) % batch_size == 0:
                print(f"\n  Saving progress... ({batch_num+1}/{len(need_lookup)} processed)")
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                print(f"  Progress saved. Found: {stats['found']}, Not found: {stats['not_found']}, Errors: {stats['errors']}\n")
    
    finally:
        scraper.cleanup_driver()
    
    # Final save
    print(f"\nSaving final results...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Statistics:")
    print(f"  Found: {stats['found']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"  Errors: {stats['errors']}")
    print(f"✓ Saved to {output_file}")
    
    return output_file

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    start_idx = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 0
    
    if '--test' in sys.argv:
        # For testing, limit to first 20 missing
        print("TEST MODE: Processing first 20 films only")
        add_english_names(input_file, output_file, start_idx, batch_size=10)
    else:
        add_english_names(input_file, output_file, start_idx)


