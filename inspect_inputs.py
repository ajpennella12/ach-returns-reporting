import csv
from pathlib import Path

raw_folder = Path(__file__).resolve().parent / "raw"

for filename in ("bank_a_january.csv", "bank_b_january.csv"):
    with (raw_folder / filename).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"\n{filename}: {len(rows)} rows")
    print(f"Columns: {reader.fieldnames}")
    for row in rows:
        print(row)