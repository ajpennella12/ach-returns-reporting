import csv
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

project = Path(__file__).resolve().parent
by_bank = {}

with (project / "monthly_returns_summary.csv").open(
    encoding="utf-8", newline=""
) as file:
    for row in csv.DictReader(file):
        month = date.fromisoformat(row["report_month"] + "-01")
        dollars = float(row["returned_dollars"])
        by_bank.setdefault(row["bank"], []).append((month, dollars))

fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")

for bank, values in sorted(by_bank.items()):
    months, dollars = zip(*sorted(values))
    ax.plot(months, dollars, marker="o", linewidth=2, label=bank)

months = sorted({month for values in by_bank.values() for month, _ in values})
ax.set_xticks(months)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
ax.set_ylim(bottom=0)
ax.set_title("Monthly ACH returned dollars by bank")
ax.set_ylabel("Returned dollars")
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.text(0.99, 0.01, "Synthetic portfolio data", ha="right", fontsize=8)

fig.savefig(project / "monthly_returns_chart.png", dpi=180)