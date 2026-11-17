"""Count rows and columns of a CSV file (catalogue example, never run by the finder)."""
import csv
import sys

with open(sys.argv[1], encoding="utf-8", newline="") as handle:
    rows = list(csv.reader(handle))
print(f"rows: {max(len(rows) - 1, 0)} | columns: {len(rows[0]) if rows else 0}")
