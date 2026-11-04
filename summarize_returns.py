import csv
import sqlite3
from decimal import Decimal
from pathlib import Path

project = Path(__file__).resolve().parent

with (project / "reportable_returns.csv").open(
    encoding="utf-8", newline=""
) as file:
    rows = list(csv.DictReader(file))

with sqlite3.connect(":memory:") as db:
    db.execute("""
        CREATE TABLE returns (
            bank TEXT,
            return_date TEXT,
            amount_cents INTEGER
        )
    """)

    db.executemany(
        "INSERT INTO returns VALUES (?, ?, ?)",
        [
            (row["bank"], row["return_date"], int(Decimal(row["amount"]) * 100))
            for row in rows
        ],
    )

    results = db.execute("""
        WITH monthly AS (
            SELECT substr(return_date, 1, 7) AS report_month,
                   bank,
                   COUNT(*) AS return_count,
                   SUM(amount_cents) AS total_cents
            FROM returns
            GROUP BY report_month, bank
        )
        SELECT current.report_month,
               current.bank,
               current.return_count,
               current.total_cents,
               current.total_cents - previous.total_cents AS change_cents
        FROM monthly AS current
        LEFT JOIN monthly AS previous
          ON previous.bank = current.bank
         AND previous.report_month = strftime(
             '%Y-%m', current.report_month || '-01', '-1 month'
         )
        ORDER BY current.report_month, current.bank
    """).fetchall()

with (project / "monthly_returns_summary.csv").open(
    "w", encoding="utf-8", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerow([
        "report_month", "bank", "return_count",
        "returned_dollars", "change_from_prior_month_dollars",
    ])

    for month, bank, count, cents, change in results:
        writer.writerow([
            month, bank, count,
            f"{Decimal(cents) / 100:.2f}",
            "" if change is None else f"{Decimal(change) / 100:.2f}",
        ])

print("Created monthly_returns_summary.csv")
