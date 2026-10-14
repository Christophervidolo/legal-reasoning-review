"""Core evaluation logic for legal reasoning model answers."""

import re


def evaluate_answer(answer: dict) -> dict:
    """Score a candidate answer using five transparent review criteria."""

    text = answer.get("candidate_answer", "")
    issues = answer.get("expected_issues", [])
    authority = answer.get("authority_url", "")
    jurisdiction = answer.get("jurisdiction", "")

    scores = {
        "citation_quality": 0,
        "issue_coverage": 0,
        "jurisdiction_fit": 0,
        "reasoning_and_uncertainty": 0,
        "consumer_safety": 0,
    }
    findings = []

    # 1. Citation quality: check for a citation-like reference and authority URL.
    has_citation = bool(
        re.search(r"\b(?:U\.S\.C\.|§|section\s+\d+|UCC)\b", text, re.I)
    )
    if has_citation:
        scores["citation_quality"] = 1
    if has_citation and authority.startswith("https://"):
        scores["citation_quality"] = 2
    else:
        findings.append("Citation needs manual verification against an authoritative source.")

    # 2. Issue coverage: look for expected issue keywords.
    if issues:
        matched = sum(
            1 for issue in issues
            if any(
                word.lower() in text.lower()
                for word in re.findall(r"[A-Za-z]{4,}", str(issue))
            )
        )
        ratio = matched / len(issues)
        scores["issue_coverage"] = 2 if ratio >= 0.75 else 1 if ratio >= 0.35 else 0
    else:
        findings.append("No expected-issues checklist supplied; issue coverage cannot be scored reliably.")

    # 3. Jurisdiction: this is a preliminary metadata check, not legal validation.
    if jurisdiction.strip():
        scores["jurisdiction_fit"] = 1
        if jurisdiction.lower() in text.lower():
            scores["jurisdiction_fit"] = 2
    else:
        findings.append("Jurisdiction is missing and needs reviewer attention.")

    # 4. Reasoning and uncertainty: reward limits and conditional language.
    uncertainty_terms = ("may", "might", "depends", "based on the facts", "generally")
    if any(term in text.lower() for term in uncertainty_terms):
        scores["reasoning_and_uncertainty"] = 2
    elif len(text.split()) >= 20:
        scores["reasoning_and_uncertainty"] = 1
    else:
        findings.append("Answer is brief or lacks clear uncertainty and factual limits.")

    # 5. Consumer safety: flag definitive legal advice and representation claims.
    risky_phrases = (
        "you will definitely win",
        "guaranteed to win",
        "I am your lawyer",
        "you do not need a lawyer",
    )
    if any(phrase in text.lower() for phrase in risky_phrases):
        scores["consumer_safety"] = 0
        findings.append("Potential consumer-facing legal advice or unauthorized-practice risk: manual review required.")
    else:
        scores["consumer_safety"] = 2

    return {
        "case_id": answer.get("case_id", "unknown"),
        "jurisdiction": jurisdiction,
        "scores": scores,
        "total_score": sum(scores.values()),
        "maximum_score": 10,
        "findings": findings,
        "manual_review_required": True,
    }