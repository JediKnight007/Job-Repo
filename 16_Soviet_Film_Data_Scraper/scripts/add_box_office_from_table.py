"""
Add box office calculations to a NEW CSV using an external, sourced ticket price table.

Usage:
    python add_box_office_from_table.py input.csv output.csv ticket_prices_by_year.csv

- input.csv  : original data (e.g., soviet_releases_1950_1991.csv)
- output.csv : new file with box office recomputed from the ticket price table
- ticket_prices_by_year.csv : mapping of year -> avg_ticket_price_rub, ideally from
  primary / well-documented sources.
"""

import csv
import sys
from typing import Dict, Optional


def load_ticket_prices(path: str) -> Dict[int, float]:
    """Load ticket prices from a CSV with columns: year, avg_ticket_price_rub."""
    prices: Dict[int, float] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year_str = (row.get("year") or "").strip()
            price_str = (row.get("avg_ticket_price_rub") or "").strip()
            if not year_str or not price_str:
                continue
            try:
                year = int(year_str)
                price = float(price_str)
            except ValueError:
                continue
            prices[year] = price
    return prices


def get_ticket_price(year: Optional[str], prices: Dict[int, float]) -> Optional[float]:
    """Get average ticket price for a given year (in rubles) from the loaded table."""
    if not year:
        return None
    try:
        year_int = int(year)
    except (ValueError, TypeError):
        return None

    if year_int in prices:
        return prices[year_int]

    # If the exact year is missing, you can choose a policy.
    # Here: use nearest available year within the range, otherwise None.
    if not prices:
        return None

    years_sorted = sorted(prices.keys())
    if year_int <= years_sorted[0]:
        return prices[years_sorted[0]]
    if year_int >= years_sorted[-1]:
        return prices[years_sorted[-1]]

    # Find closest year
    closest_year = min(years_sorted, key=lambda y: abs(y - year_int))
    return prices[closest_year]


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: python add_box_office_from_table.py "
            "input.csv output.csv ticket_prices_by_year.csv"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    prices_path = sys.argv[3]

    print(f"Loading ticket prices from {prices_path}...")
    prices = load_ticket_prices(prices_path)
    if not prices:
        print("✗ No ticket prices loaded. Check the ticket_prices_by_year.csv file.")
        sys.exit(1)

    print(f"Reading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    print(f"  Found {len(rows)} rows")
    if not rows:
        print("✗ No rows found in input CSV.")
        sys.exit(1)

    fieldnames = list(reader.fieldnames or [])
    # Ensure output has these columns
    if "avg_ticket_price_rub" not in fieldnames:
        fieldnames.append("avg_ticket_price_rub")
    if "box_office_rubles" not in fieldnames:
        fieldnames.append("box_office_rubles")

    calculated = 0
    missing_year = 0
    missing_viewers = 0

    print("  Calculating box office using sourced ticket prices...")
    for row in rows:
        year = row.get("soviet_release_year") or row.get("year")
        viewers_str = row.get("viewers_total") or row.get("viewers") or ""

        # Parse viewers
        try:
            viewers = int(viewers_str)
        except (ValueError, TypeError):
            viewers = None

        price = get_ticket_price(year, prices)

        if year is None or year == "":
            missing_year += 1
        if viewers is None:
            missing_viewers += 1

        if price is not None:
            row["avg_ticket_price_rub"] = f"{price:.2f}"
        else:
            row["avg_ticket_price_rub"] = ""

        if price is not None and viewers is not None:
            box_office = viewers * price
            row["box_office_rubles"] = f"{box_office:.2f}"
            calculated += 1
        else:
            row["box_office_rubles"] = ""

    print(f"\nWriting to {output_path}...")
    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n✓ Statistics:")
    print(f"  Calculated: {calculated}")
    print(f"  Missing viewers: {missing_viewers}")
    print(f"  Missing year: {missing_year}")
    print("✓ Done.")


if __name__ == "__main__":
    main()


