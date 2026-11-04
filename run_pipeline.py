import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parent

steps = [
    "standardize_returns.py",
    "validate_returns.py",
    "match_returns.py",
    "summarize_returns.py",
]

for script in steps:
    print(f"\n--- Running {script} ---", flush=True)
    subprocess.run([sys.executable, str(project / script)], check=True)

print("\nPipeline complete.")