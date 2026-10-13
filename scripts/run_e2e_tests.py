#!/usr/bin/env python3
"""
Sterling Prime Comprehensive E2E Test Suite Runner
Executes opaque-box test tiers (Tiers 1-4) covering requirements R1-R4 and features F1-F17.

Usage:
    python scripts/run_e2e_tests.py
    python scripts/run_e2e_tests.py --tier 1
    python scripts/run_e2e_tests.py --tier 2
    python scripts/run_e2e_tests.py --tier 3
    python scripts/run_e2e_tests.py --tier 4
    python scripts/run_e2e_tests.py --feature F10
    python scripts/run_e2e_tests.py --verbose --json report.json
"""

import argparse
import io
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Optional

# Ensure UTF-8 output on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Root directory configuration
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ANSI Color Codes with graceful fallback
USE_COLOR = os.name != "nt" or "WT_SESSION" in os.environ or "TERM" in os.environ
GREEN = "\033[92m" if USE_COLOR else ""
RED = "\033[91m" if USE_COLOR else ""
YELLOW = "\033[93m" if USE_COLOR else ""
BLUE = "\033[94m" if USE_COLOR else ""
CYAN = "\033[96m" if USE_COLOR else ""
BOLD = "\033[1m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""

TIER_FILES = {
    "1": ("Tier 1 - Feature Coverage (F1-F17)", "tests/test_tier1_features.py"),
    "2": ("Tier 2 - Boundary & Corner Cases", "tests/test_tier2_boundaries.py"),
    "3": ("Tier 3 - Cross-Feature Combinations", "tests/test_tier3_combinations.py"),
    "4": ("Tier 4 - Real-World Workloads & Latency", "tests/test_tier4_workloads.py"),
}


class DetailedTestResult(unittest.TextTestResult):
    """Custom test result collector capturing execution timings and errors."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_records = []
        self._test_start_time = None

    def startTest(self, test):
        super().startTest(test)
        self._test_start_time = time.time()

    def addSuccess(self, test):
        super().addSuccess(test)
        duration = time.time() - (self._test_start_time or time.time())
        self.test_records.append({
            "test": str(test),
            "status": "PASS",
            "duration_sec": round(duration, 4),
            "error": None,
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        duration = time.time() - (self._test_start_time or time.time())
        self.test_records.append({
            "test": str(test),
            "status": "FAIL",
            "duration_sec": round(duration, 4),
            "error": self._exc_info_to_string(err, test),
        })

    def addError(self, test, err):
        super().addError(test, err)
        duration = time.time() - (self._test_start_time or time.time())
        self.test_records.append({
            "test": str(test),
            "status": "ERROR",
            "duration_sec": round(duration, 4),
            "error": self._exc_info_to_string(err, test),
        })


def run_tier(tier_key: str, tier_name: str, test_file_rel: str, feature_filter: Optional[str], verbosity: int) -> Dict:
    """Run tests for a single tier or feature filter and return structured metrics."""
    test_file_path = REPO_ROOT / test_file_rel
    if not test_file_path.exists():
        return {
            "tier": tier_key,
            "name": tier_name,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "time_sec": 0.0,
            "records": [],
            "status": "SKIPPED",
        }

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Import test module
    module_name = test_file_rel.replace("/", ".").replace("\\", ".").replace(".py", "")
    try:
        module = __import__(module_name, fromlist=["*"])
    except Exception as exc:
        print(f"{RED}Error importing {module_name}: {exc}{RESET}")
        return {
            "tier": tier_key,
            "name": tier_name,
            "total": 1,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "time_sec": 0.0,
            "records": [{"test": module_name, "status": "ERROR", "error": str(exc)}],
            "status": "ERROR",
        }

    loaded_suite = loader.loadTestsFromModule(module)

    # Apply feature filter if specified (e.g., F10, F2)
    if feature_filter:
        clean_filter = feature_filter.upper().strip()
        filtered_suite = unittest.TestSuite()
        for test_case in loaded_suite:
            for test in test_case:
                test_str = str(test)
                if clean_filter in test_str.upper():
                    filtered_suite.addTest(test)
        suite = filtered_suite
    else:
        suite = loaded_suite

    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        resultclass=DetailedTestResult,
        verbosity=verbosity,
    )

    t0 = time.time()
    result = runner.run(suite)
    elapsed = time.time() - t0

    passed_count = result.testsRun - len(result.failures) - len(result.errors)
    status = "PASS" if (len(result.failures) == 0 and len(result.errors) == 0) else "FAIL"

    return {
        "tier": tier_key,
        "name": tier_name,
        "total": result.testsRun,
        "passed": passed_count,
        "failed": len(result.failures),
        "errors": len(result.errors),
        "time_sec": round(elapsed, 3),
        "records": result.test_records,
        "output": stream.getvalue(),
        "status": status,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sterling Prime Comprehensive Opaque-Box E2E Test Suite Runner"
    )
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Test tier to execute (default: all)",
    )
    parser.add_argument(
        "--feature",
        type=str,
        default=None,
        help="Filter execution to specific feature (e.g. F1, F10, F15)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed verbose output for each test",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=str,
        default=None,
        help="Output structured test execution report to specified JSON file",
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop execution on first test failure",
    )

    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}     Sterling Prime Multi-Catalogue E2E Test Runner (Tiers 1-4)       {RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f" Working Directory : {REPO_ROOT}")
    print(f" Target Scope      : Tiers {args.tier.upper()} | Feature Filter: {args.feature or 'None'}")
    print(f" Timestamp         : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"{CYAN}----------------------------------------------------------------------{RESET}\n")

    selected_tiers = ["1", "2", "3", "4"] if args.tier == "all" else [args.tier]
    overall_start = time.time()
    tier_results = []
    has_failures = False

    for t_key in selected_tiers:
        t_name, t_file = TIER_FILES[t_key]
        print(f"Running {BOLD}{t_name}{RESET}...")
        t_res = run_tier(
            tier_key=t_key,
            tier_name=t_name,
            test_file_rel=t_file,
            feature_filter=args.feature,
            verbosity=2 if args.verbose else 1,
        )
        tier_results.append(t_res)

        # Print tier status line
        if t_res["status"] == "PASS":
            badge = f"{GREEN}[ PASS ]{RESET}"
        else:
            badge = f"{RED}[ FAIL ]{RESET}"
            has_failures = True

        print(
            f"  {badge} {t_res['passed']}/{t_res['total']} passed in {t_res['time_sec']:.2f}s "
            f"(Fail: {t_res['failed']}, Err: {t_res['errors']})"
        )

        if args.verbose and t_res.get("output"):
            print(t_res["output"].strip())

        if args.failfast and has_failures:
            print(f"\n{RED}Stopping execution early due to --failfast flag.{RESET}")
            break

    total_time = round(time.time() - overall_start, 3)
    total_tests = sum(r["total"] for r in tier_results)
    total_passed = sum(r["passed"] for r in tier_results)
    total_failed = sum(r["failed"] for r in tier_results)
    total_errors = sum(r["errors"] for r in tier_results)
    pass_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0.0

    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}                        E2E TEST SUMMARY REPORT                       {RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{'Tier Name':<42} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Time (s)':<8}")
    print(f"{'-'*42}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*8}")
    for r in tier_results:
        color = GREEN if r["status"] == "PASS" else RED
        print(f"{r['name']:<42} | {r['total']:<6} | {color}{r['passed']:<6}{RESET} | {r['failed']:<6} | {r['time_sec']:<8.2f}")
    print(f"{'-'*42}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*8}")
    print(f"{'OVERALL TOTALS':<42} | {total_tests:<6} | {GREEN if not has_failures else RED}{total_passed:<6}{RESET} | {total_failed:<6} | {total_time:<8.2f}")
    print(f"{CYAN}======================================================================{RESET}")
    print(f" Overall Pass Rate: {BOLD}{GREEN if pass_pct == 100.0 else RED}{pass_pct:.1f}%{RESET}")
    print(f" Final Status     : {BOLD}{GREEN + 'ALL TIERS PASSING' if not has_failures else RED + 'TESTS FAILED'}{RESET}\n")

    # Save JSON report if requested
    if args.json_path:
        json_file = Path(args.json_path)
        report_data = {
            "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "pass_rate_pct": round(pass_pct, 2),
            "total_duration_sec": total_time,
            "tier_results": tier_results,
        }
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"Structured JSON report exported to: {json_file.resolve()}\n")

    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
