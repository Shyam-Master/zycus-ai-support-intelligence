import sys
import json
from pathlib import Path
from evaluation.evaluator import Evaluator
from evaluation.test_cases import TRIAGE_TEST_CASES, TAM_TEST_CASES
from app.utils.data_loader import DataLoader
from datetime import datetime

def run_eval():
    evaluator = Evaluator()
    
    triage_results = []
    tam_results = []
    
    print("=" * 40)
    print("ZYCUS AI SUPPORT EVALUATION REPORT")
    print("=" * 40 + "\n")
    
    print("TRIAGE TESTS")
    for tc in TRIAGE_TEST_CASES:
        res = evaluator.evaluate_triage(tc)
        triage_results.append(res)
        mark = "[PASS]" if res['status'] == "PASS" else "[FAIL]"
        print(f"{mark} {res['test_name']} - {res['quality_score']:.2f} {res['status']}")
        
    print("\nTAM TESTS")
    for tc in TAM_TEST_CASES:
        res = evaluator.evaluate_tam(tc)
        tam_results.append(res)
        mark = "[PASS]" if res['status'] == "PASS" else "[FAIL]"
        print(f"{mark} {res['test_name']} - {res['quality_score']:.2f} {res['status']}")
        
    all_results = triage_results + tam_results
    total = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == "PASS")
    failed = total - passed
    avg_score = sum(r['quality_score'] for r in all_results) / total if total > 0 else 0
    
    # Deterministic generated_at value based on the dataset
    valid_tickets = [t for t in evaluator.all_tickets if '_created_at_dt' in t]
    max_date = max(t['_created_at_dt'] for t in valid_tickets)
    generated_at_str = max_date.isoformat()
    
    report = {
        "generated_at": generated_at_str,
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "average_score": round(avg_score, 2)
        },
        "triage_tests": triage_results,
        "tam_tests": tam_results
    }
    
    report_path = Path("eval_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print("\n" + "=" * 40)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Average Score: {avg_score:.2f}")
    print("=" * 40)
    print(f"\nReport written to {report_path.absolute()}")
    
    if failed > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    run_eval()
