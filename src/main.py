"""Run the legal reasoning evaluation and export results."""

import csv
import json
from pathlib import Path

from evaluator import evaluate_answer


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "evaluation_dataset.json"
REPORT_DIR = ROOT / "reports"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Place evaluation_dataset.json inside the data folder first."
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset if isinstance(dataset, list) else dataset.get("cases", [])
    if not cases:
        raise ValueError("Dataset contains no evaluation cases.")

    results = [evaluate_answer(case) for case in cases]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "evaluation_results.json"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    csv_path = REPORT_DIR / "evaluation_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        columns = [
            "case_id",
            "jurisdiction",
            "total_score",
            "maximum_score",
            "manual_review_required",
            "findings",
        ]
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for result in results:
            row = result.copy()
            row["findings"] = "; ".join(result["findings"])
            writer.writerow({column: row.get(column, "") for column in columns})

    print(f"Cases evaluated: {len(results)}")
    print(f"Average score: {sum(r['total_score'] for r in results) / len(results):.2f}/10")
    print(f"JSON results: {json_path}")
    print(f"CSV results: {csv_path}")
    print("Note: automated scores are preliminary; human legal review is still required.")


if __name__ == "__main__":
    main()