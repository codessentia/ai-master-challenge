"""Run the diagnosis (bottlenecks, satisfaction drivers, waste) and write outputs/diagnosis/diagnosis.json.

Run from the solution folder:  uv run python scripts/run_diagnosis.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.diagnosis import bottlenecks, csat_drivers, prepare
from support_triage.paths import OUTPUTS_DIR, TICKETS_DIR
from support_triage.waste import estimate

OUT = OUTPUTS_DIR / "diagnosis"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = prepare(pd.read_csv(TICKETS_DIR / "customer_support_tickets.csv"))
    result = {
        "bottlenecks": bottlenecks(df),
        "csat_drivers": csat_drivers(df),
        "waste": estimate(),
    }
    (OUT / "diagnosis.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"wrote {OUT / 'diagnosis.json'}")


if __name__ == "__main__":
    main()
