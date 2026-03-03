#!/usr/bin/env python3
"""
RAG evaluation harness.

Runs every question in the eval dataset through the pipeline, scores each
result on two metrics, and prints a summary table.

Metrics:
  - Keyword match:    any expected keyword appears in the answer (case-insensitive)
  - Context recall:   expected source page appears in retrieved sources (skipped if null)

Usage:
    python evals/run_evals.py
    python evals/run_evals.py --dataset evals/eval_dataset.json
    python evals/run_evals.py --output evals/results.json

Requirements:
    Documents referenced in eval_dataset.json must already be ingested into
    the production ChromaDB collection before running evals.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path so `src` imports work when run directly.
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pipelines.rag import answer  # noqa: E402


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_keyword_match(answer_text: str, keywords: list[str]) -> tuple[bool, list[str]]:
    """Return (passed, matched_keywords). Passes if any keyword found (case-insensitive)."""
    lower = answer_text.lower()
    matched = [kw for kw in keywords if kw.lower() in lower]
    return len(matched) > 0, matched


def score_context_recall(sources: list[dict], expected_page: int | None) -> tuple[bool, str]:
    """Return (passed, detail). Passes if expected_page is in retrieved sources."""
    if expected_page is None:
        return True, "skipped (no expected page)"
    retrieved = [s["page"] for s in sources]
    if expected_page in retrieved:
        return True, f"page {expected_page} found in {retrieved}"
    return False, f"page {expected_page} NOT in {retrieved}"


# ---------------------------------------------------------------------------
# Eval runner
# ---------------------------------------------------------------------------

def run_evals(dataset_path: str, output_path: str | None = None) -> dict:
    dataset = json.loads(Path(dataset_path).read_text())
    results = []

    for case in dataset:
        cid = case["id"]
        question = case["question"]
        keywords = case["expected_answer_keywords"]
        expected_page = case.get("expected_source_page")

        print(f"\n[{cid}] {question}")

        try:
            result = answer(question)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            results.append({"id": cid, "question": question, "error": str(exc),
                            "keyword_pass": False, "context_recall_pass": False, "overall_pass": False})
            continue

        kw_pass, matched = score_keyword_match(result["answer"], keywords)
        cr_pass, cr_detail = score_context_recall(result["sources"], expected_page)
        overall = kw_pass and cr_pass

        print(f"  Keyword match:  {'PASS' if kw_pass else 'FAIL'}  matched={matched}")
        print(f"  Context recall: {'PASS' if cr_pass else 'FAIL'}  {cr_detail}")
        print(f"  Answer: {result['answer'][:120]}{'...' if len(result['answer']) > 120 else ''}")

        results.append({
            "id": cid,
            "document": case.get("document"),
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "context_found": result["context_found"],
            "expected_keywords": keywords,
            "matched_keywords": matched,
            "keyword_pass": kw_pass,
            "expected_source_page": expected_page,
            "context_recall_detail": cr_detail,
            "context_recall_pass": cr_pass,
            "overall_pass": overall,
        })

    # Summary
    total = len(results)
    kw_n = sum(1 for r in results if r.get("keyword_pass"))
    cr_n = sum(1 for r in results if r.get("context_recall_pass"))
    ov_n = sum(1 for r in results if r.get("overall_pass"))

    print("\n" + "=" * 68)
    print(f"{'ID':<22} {'Keyword':>10} {'Context Recall':>16} {'Overall':>10}")
    print("-" * 68)
    for r in results:
        if "error" in r:
            print(f"{r['id']:<22} {'ERROR':>10} {'ERROR':>16} {'ERROR':>10}")
        else:
            kw = "PASS" if r["keyword_pass"] else "FAIL"
            cr = "PASS" if r["context_recall_pass"] else "FAIL"
            ov = "PASS" if r["overall_pass"] else "FAIL"
            print(f"{r['id']:<22} {kw:>10} {cr:>16} {ov:>10}")
    print("=" * 68)
    print(f"{'TOTAL':<22} {kw_n}/{total:>8} {cr_n}/{total:>14} {ov_n}/{total:>8}")
    print(f"  Keyword match rate:    {kw_n / total * 100:.1f}%")
    print(f"  Context recall rate:   {cr_n / total * 100:.1f}%")
    print(f"  Overall pass rate:     {ov_n / total * 100:.1f}%")
    print("=" * 68)

    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset_path,
        "summary": {
            "total": total,
            "keyword_pass_count": kw_n,
            "context_recall_pass_count": cr_n,
            "overall_pass_count": ov_n,
            "keyword_match_rate": round(kw_n / total, 3) if total else 0,
            "context_recall_rate": round(cr_n / total, 3) if total else 0,
            "overall_pass_rate": round(ov_n / total, 3) if total else 0,
        },
        "results": results,
    }

    if output_path:
        Path(output_path).write_text(json.dumps(output, indent=2))
        print(f"\nResults written to {output_path}")

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG evaluations")
    parser.add_argument("--dataset", default="evals/eval_dataset.json")
    parser.add_argument("--output", default=None, help="Write results to this JSON file")
    args = parser.parse_args()
    run_evals(args.dataset, args.output)
