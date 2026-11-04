import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

project_folder = Path(__file__).resolve().parent
raw_folder = project_folder / "raw"

bank_a_columns = {
    "return_id": "return_id",
    "original_transaction_id": "original_transaction_id",
    "return_date": "return_date",
    "amount": "amount",
    "return_code": "return_code",
}

bank_b_columns = {
    "return_id": "Return Reference",
    "original_transaction_id": "Original Trace",
    "return_date": "Date Returned",
    "amount": "Returned Amount",
    "return_code": "Reason",
}


def read_bank(filename, bank, columns, date_format):
    with (raw_folder / filename).open(encoding="utf-8", newline="") as file:
        for source_row in csv.DictReader(file):
            row = {
                standard_name: source_row[source_name].strip()
                for standard_name, source_name in columns.items()
            }
            row["return_date"] = datetime.strptime(
                row["return_date"], date_format
            ).date().isoformat()
            row["amount"] = format(Decimal(row["amount"].lstrip("$")), ".2f")
            row["bank"] = bank
            yield row


with (project_folder / "standardized_returns.csv").open(
    "w", encoding="utf-8", newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=["bank", *bank_a_columns])
    writer.writeheader()

    for source_file in sorted(raw_folder.glob("bank_a_*.csv")):
        writer.writerows(
            read_bank(source_file.name, "Bank A", bank_a_columns, "%Y-%m-%d")
        )

    for source_file in sorted(raw_folder.glob("bank_b_*.csv")):
        writer.writerows(
            read_bank(source_file.name, "Bank B", bank_b_columns, "%m/%d/%Y")
        )