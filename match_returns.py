import csv
import sqlite3
from decimal import Decimal
from pathlib import Path

project = Path(__file__).resolve().parent


def load_csv(filename):
    with (project / filename).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def to_cents(amount):
    return int(Decimal(amount) * 100)


with sqlite3.connect(":memory:") as db:
    db.execute("""
        CREATE TABLE returns (
            bank TEXT, return_id TEXT, original_transaction_id TEXT,
            amount_cents INTEGER
        )
    """)
    db.execute("""
        CREATE TABLE original_transactions (
            bank TEXT, transaction_id TEXT, amount_cents INTEGER,
            PRIMARY KEY (bank, transaction_id)
        )
    """)

    db.executemany("INSERT INTO returns VALUES (?, ?, ?, ?)", [
        (row["bank"], row["return_id"], row["original_transaction_id"],
         to_cents(row["amount"]))
        for row in load_csv("reportable_returns.csv")
    ])
    db.executemany("INSERT INTO original_transactions VALUES (?, ?, ?)", [
        (row["bank"], row["transaction_id"], to_cents(row["amount"]))
        for row in load_csv("original_transactions.csv")
    ])

    results = db.execute("""
        SELECT r.bank, r.return_id, r.original_transaction_id,
               CASE
                   WHEN t.transaction_id IS NULL THEN 'Original transaction missing'
                   WHEN r.amount_cents <> t.amount_cents THEN 'Amount mismatch'
                   ELSE 'Matched'
               END AS status
        FROM returns AS r
        LEFT JOIN original_transactions AS t
          ON r.bank = t.bank
         AND r.original_transaction_id = t.transaction_id
        ORDER BY r.bank, r.return_id
    """)

    for bank, return_id, transaction_id, status in results:
        print(f"{bank} | {return_id} | {transaction_id} | {status}")