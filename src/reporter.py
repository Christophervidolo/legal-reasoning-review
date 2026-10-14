"""Generate a findings report from actual evaluation results."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = ROOT / "reports" / "evaluation_results.json"
REPORT_FILE = ROOT / "reports" / "evaluation_summary.md"


def main():
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            "Run 'python src/main.py' before generating the report."
        )

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))

    if not results:
        raise ValueError("No evaluation results are available.")

    average = sum(item["total_score"] for item in results) / len(results)

    lines = [
        "# Legal Reasoning Review — Evaluation Summary",
        "",
        "## Run summary",
        "",
        f"- Cases evaluated: {len(results)}",
        f"- Mean preliminary score: {average:.2f}/10",
        "- Human legal review required: Yes",
        "",
        "## Case-level findings",
        "",
    ]

    for item in results:
        lines.extend([
            f"### {item['case_id']}",
            f"- Jurisdiction: {item.get('jurisdiction') or 'Not supplied'}",
            f"- Score: {item['total_score']}/10",
            f"- Manual review required: {item['manual_review_required']}",
        ])

        if item["findings"]:
            lines.extend(
                f"- Finding: {finding}" for finding in item["findings"]
            )
        else:
            lines.append("- No automated flags were raised.")

        lines.append("")

    lines.extend([
        "## Methodology and limitations",
        "",
        "The evaluator uses deterministic pattern checks and a five-part "
        "rubric covering citation quality, issue coverage, jurisdiction fit, "
        "reasoning and uncertainty, and consumer safety.",
        "",
        "Scores are preliminary screening results, not a determination of "
        "legal correctness. Citation presence does not prove an authority "
        "is current, binding, or applicable. Keyword matching does not prove "
        "complete issue coverage. The authority links and statutory text "
        "require independent verification by a qualified reviewer.",
        "",
        "This report describes a constructed pilot dataset, not a dataset "
        "provided by the task platform. It is not legal advice.",
        "",
    ])

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report created: {REPORT_FILE}")
    print(f"Cases included: {len(results)}")
    print(f"Mean score: {average:.2f}/10")


if __name__ == "__main__":
    main()