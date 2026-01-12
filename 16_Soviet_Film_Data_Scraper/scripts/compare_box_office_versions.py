"""
Compare box office results between two CSV files (old vs. new ticket prices).

Usage:
    python compare_box_office_versions.py old.csv new.csv

The script reports:
- Total box office (sum of box_office_rubles) in each file
- Difference by soviet_release_year (if available)
"""

import csv
import sys
from collections import defaultdict
from typing import Dict, Tuple


def load_totals(path: str) -> Tuple[float, Dict[str, float]]:
    """Load total box office overall and by soviet_release_year."""
    total = 0.0
    by_year: Dict[str, float] = defaultdict(float)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            box_str = (row.get("box_office_rubles") or "").strip()
            year = (row.get("soviet_release_year") or "").strip()
            if not box_str:
                continue
            try:
                box = float(box_str)
            except ValueError:
                continue
            total += box
            if year:
                by_year[year] += box

    return total, by_year


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python compare_box_office_versions.py old.csv new.csv")
        sys.exit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    print(f"Loading OLD data from {old_path}...")
    old_total, old_by_year = load_totals(old_path)

    print(f"Loading NEW data from {new_path}...")
    new_total, new_by_year = load_totals(new_path)

    print("\n=== Overall totals ===")
    print(f"Old total box office: {old_total:,.2f} rubles")
    print(f"New total box office: {new_total:,.2f} rubles")
    diff = new_total - old_total
    print(f"Difference (new - old): {diff:,.2f} rubles")

    print("\n=== By soviet_release_year (top 20 by absolute difference) ===")
    all_years = set(old_by_year.keys()) | set(new_by_year.keys())
    year_diffs = []
    for year in all_years:
        o = old_by_year.get(year, 0.0)
        n = new_by_year.get(year, 0.0)
        d = n - o
        year_diffs.append((year, o, n, d))

    # Sort by absolute difference, descending
    year_diffs.sort(key=lambda t: abs(t[3]), reverse=True)

    print(f"{'Year':<6} {'Old total':>18} {'New total':>18} {'Diff (new-old)':>18}")
    for year, o, n, d in year_diffs[:20]:
        print(f"{year:<6} {o:>18,.2f} {n:>18,.2f} {d:>18,.2f}")


if __name__ == "__main__":
    main()



