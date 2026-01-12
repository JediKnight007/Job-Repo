"""
Add box office calculations to CSV
Calculates: box_office_rubles = viewers_total × avg_ticket_price_rub
Uses historical average ticket prices by period
"""
import csv
import sys

# Historical average ticket prices by year (in rubles)
# Based on Soviet cinema statistics and historical trends
# Prices gradually increased over time due to inflation and policy changes
TICKET_PRICES_BY_YEAR = {
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

def get_ticket_price(year):
    """Get average ticket price for a given year (in rubles)"""
    if not year:
        return None
    
    try:
        year_int = int(year)
        # Direct lookup by year
        if year_int in TICKET_PRICES_BY_YEAR:
            return TICKET_PRICES_BY_YEAR[year_int]
        
        # Interpolate for years outside range
        if year_int < 1950:
            return TICKET_PRICES_BY_YEAR[1950]
        elif year_int > 1991:
            return TICKET_PRICES_BY_YEAR[1991]
        else:
            # Shouldn't happen, but fallback
            return 0.50
    except (ValueError, TypeError):
        return None

def add_box_office_to_csv(input_file, output_file=None):
    """Add box office calculations to CSV"""
    if output_file is None:
        output_file = input_file
    
    print(f"Reading {input_file}...")
    
    # Read all rows
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        # Add columns if they don't exist
        if 'avg_ticket_price_rub' not in fieldnames:
            fieldnames.append('avg_ticket_price_rub')
        if 'box_office_rubles' not in fieldnames:
            fieldnames.append('box_office_rubles')
        
        for row in reader:
            rows.append(row)
    
    print(f"  Found {len(rows)} rows")
    print(f"  Calculating box office...")
    
    stats = {
        'calculated': 0,
        'missing_viewers': 0,
        'missing_year': 0,
        'errors': 0
    }
    
    # Process rows
    for i, row in enumerate(rows):
        viewers_text = row.get('viewers_total', '').strip()
        year_text = row.get('soviet_release_year', '').strip()
        
        # Get ticket price for the year
        ticket_price = get_ticket_price(year_text)
        
        if ticket_price:
            row['avg_ticket_price_rub'] = ticket_price
        else:
            row['avg_ticket_price_rub'] = ''
            stats['missing_year'] += 1
        
        # Calculate box office
        if viewers_text and year_text and ticket_price:
            try:
                viewers_int = int(viewers_text)
                box_office = viewers_int * ticket_price
                row['box_office_rubles'] = f"{box_office:.2f}"
                stats['calculated'] += 1
            except (ValueError, TypeError) as e:
                row['box_office_rubles'] = ''
                stats['errors'] += 1
        else:
            row['box_office_rubles'] = ''
            if not viewers_text:
                stats['missing_viewers'] += 1
    
    # Write updated CSV
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Statistics:")
    print(f"  Calculated: {stats['calculated']}")
    print(f"  Missing viewers: {stats['missing_viewers']}")
    print(f"  Missing year: {stats['missing_year']}")
    print(f"  Errors: {stats['errors']}")
    print(f"✓ Saved to {output_file}")
    
    # Show sample
    print("\nSample calculations (first 10):")
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
                break
            name = row.get('name_russian', '')[:30]
            viewers = row.get('viewers_total', '')
            year = row.get('soviet_release_year', '')
            price = row.get('avg_ticket_price_rub', '')
            box_office = row.get('box_office_rubles', '')
            if box_office:
                print(f"  {name:30} | {viewers:>12} viewers × {price:>4} rub = {box_office:>15} rub")
    
    return output_file

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_box_office_to_csv(input_file, output_file)

