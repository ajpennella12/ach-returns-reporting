import csv
from decimal import Decimal
from pathlib import Path

project = Path(__file__).resolve().parent

with (project / "standardized_returns.csv").open(
    encoding="utf-8", newline=""
) as file:
    reader = csv.DictReader(file)
    columns = reader.fieldnames
    rows = list(reader)

seen = set()
report_rows = []
exceptions = []

for row in rows:
    row_key = tuple(row[column] for column in columns)

    if row_key in seen:
        exceptions.append({**row, "issue": "Exact duplicate excluded"})
        continue

    seen.add(row_key)
    report_rows.append(row)

    if not row["return_code"]:
        exceptions.append({**row, "issue": "Missing return code; kept in totals"})

for filename, output_columns, output_rows in [
    ("reportable_returns.csv", columns, report_rows),
    ("return_exceptions.csv", [*columns, "issue"], exceptions),
]:
    with (project / filename).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(output_rows)

total = sum(Decimal(row["amount"]) for row in report_rows)
print(f"Input rows: {len(rows)}")
print(f"Reportable returns: {len(report_rows)}")
print(f"Exceptions logged: {len(exceptions)}")
print(f"Reportable amount: \${total:,.2f}")