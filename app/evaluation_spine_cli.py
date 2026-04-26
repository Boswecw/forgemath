from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.services.evaluation_spine_authority import evaluate_calibration_report_file_or_raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an eval-cal-node calibration report through ForgeMath authority."
    )
    parser.add_argument("input_path", help="Path to eval_calibration_report.contract.json")
    parser.add_argument("output_dir", help="Directory for ForgeMath lane evaluation output")
    args = parser.parse_args()

    result = evaluate_calibration_report_file_or_raise(Path(args.input_path), Path(args.output_dir))
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
