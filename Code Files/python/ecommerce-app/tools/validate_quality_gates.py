"""Validate the integrated AI demo quality gates.

This script is intentionally dependency-free so it can run in GitHub Actions
without requiring extra packages beyond the project test dependencies.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import generate_demo_docs


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
SUMMARY_MD = REPORTS_DIR / "quality-gates-summary.md"
SUMMARY_JSON = REPORTS_DIR / "quality-gates.json"


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def class_names(path: Path) -> set[str]:
    tree = ast.parse(read_text(path))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def function_names(path: Path) -> set[str]:
    tree = ast.parse(read_text(path))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def gate(name: str, condition: bool, detail: str) -> GateResult:
    return GateResult(name=name, passed=condition, detail=detail)


def validate_architecture() -> GateResult:
    processor_path = ROOT / "src" / "payment" / "payment_processor.py"
    apple_path = ROOT / "src" / "payment" / "apple_pay_payment_method.py"
    processor_classes = class_names(processor_path)
    apple_classes = class_names(apple_path)
    required = {"PaymentProcessor", "AbstractPaymentMethod"}
    condition = required.issubset(processor_classes) and "ApplePayPaymentMethod" in apple_classes
    detail = "Strategy pattern classes present: PaymentProcessor, AbstractPaymentMethod, ApplePayPaymentMethod."
    return gate("Architecture discovery", condition, detail)


def validate_implementation_contract() -> GateResult:
    apple_path = ROOT / "src" / "payment" / "apple_pay_payment_method.py"
    source = read_text(apple_path)
    functions = function_names(apple_path)
    required = {
        "process_payment",
        "process_apple_pay_payment",
        "validate_token",
        "validate_payment",
        "refund_payment",
        "_execute_with_retry",
        "_build_request_headers",
    }
    condition = required.issubset(functions) and "Idempotency-Key" in source
    detail = "Apple Pay method exposes processing, validation, refund, retry, and idempotency behavior."
    return gate("Implementation contract", condition, detail)


def validate_technical_debt() -> GateResult:
    apple_source = read_text(ROOT / "src" / "payment" / "apple_pay_payment_method.py")
    ticket = ROOT / "docs" / "tickets" / "TECH-DEBT-payment-module-security-fixes.md"
    ticket_text = read_text(ticket) if ticket.exists() else ""

    logger_lines = [line for line in apple_source.splitlines() if "logger." in line]
    raw_payment_logging = any("payment_data" in line or "apple_pay_token" in line for line in logger_lines)
    hardcoded_secret = bool(re.search(r"['\"](?:sk|pk|apay)_(?:live|test)_[A-Za-z0-9]{12,}['\"]", apple_source))
    env_guardrail = "os.getenv(\"APPLE_PAY_API_KEY\"" in apple_source
    lowered_ticket = ticket_text.lower()
    debt_registered = (
        "hardcoded" in lowered_ticket
        and ("redact" in lowered_ticket or "sensitive payment data" in lowered_ticket)
        and "complexity" in lowered_ticket
    )

    condition = env_guardrail and debt_registered and not raw_payment_logging and not hardcoded_secret
    detail = "Known legacy debt is registered, and Apple Pay avoids hardcoded secrets plus raw payment-token logging."
    return gate("Technical debt guardrail", condition, detail)


def validate_openapi_contract() -> GateResult:
    text = read_text(ROOT / "docs" / "api" / "apple-pay-openapi.yaml")
    required_fragments = [
        "openapi: 3.0",
        "/payments/apple-pay:",
        "BearerAuth:",
        "payments:write",
        "ApplePayRequest:",
        "PaymentSuccessResponse:",
        "ErrorResponse:",
        "Retry-After:",
        "INVALID_TOKEN",
        "UPSTREAM_UNAVAILABLE",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    detail = "OpenAPI spec includes endpoint, bearer auth, schemas, examples, retry headers, and expected errors."
    return gate("API documentation", not missing, detail if not missing else f"Missing fragments: {', '.join(missing)}")


def validate_bdd_contract() -> GateResult:
    feature = read_text(ROOT / "tests" / "payment" / "apple_pay.feature")
    test_source = read_text(ROOT / "tests" / "payment" / "test_apple_pay.py")
    scenarios = re.findall(r"^\s*Scenario(?: Outline)?:", feature, flags=re.MULTILINE)
    required_topics = ["Successful", "invalid", "expired", "503", "limit", "timeout", "refunded"]
    topics_present = all(topic.lower() in feature.lower() for topic in required_topics)
    step_definitions_present = all(marker in test_source for marker in ["@given", "@when", "@then", "scenarios("])
    condition = len(scenarios) >= 8 and topics_present and step_definitions_present
    detail = f"BDD suite defines {len(scenarios)} Apple Pay scenarios with pytest-bdd step definitions."
    return gate("BDD test contract", condition, detail)


def validate_living_docs() -> GateResult:
    expected = generate_demo_docs.build_artifacts()
    stale = generate_demo_docs.check_artifacts(expected)
    if stale:
        detail = "Stale generated files: " + ", ".join(str(path.relative_to(ROOT)) for path in stale)
        return gate("Living README/docs", False, detail)
    detail = "README and generated quality-gate docs match the current source digest."
    return gate("Living README/docs", True, detail)


def validate_workflow() -> GateResult:
    workflow = ROOT / ".github" / "workflows" / "integrated-ai-demo-quality-gates.yml"
    text = read_text(workflow) if workflow.exists() else ""
    required = [
        "on:",
        "push:",
        "branches:",
        "'**'",
        "contents: write",
        "tools/generate_demo_docs.py",
        "tools/validate_quality_gates.py",
        "tools/generate_workflow_report.py",
        "reports/integrated-ai-workflow-report.html",
        "reports/logs/*.log",
        "pytest tests/payment/test_apple_pay.py",
        "github-actions[bot]",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    detail = "Workflow runs on all branch pushes, generates docs, validates gates, runs tests, and can commit docs."
    return gate("GitHub workflow", not missing, detail if not missing else f"Missing fragments: {', '.join(missing)}")


def write_reports(results: list[GateResult]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    lines = [
        "# Integrated AI Demo Quality Gate Summary",
        "",
        f"Passed: {passed}/{total}",
        "",
        "| Gate | Status | Detail |",
        "|---|---|---|",
    ]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"| {result.name} | {status} | {result.detail} |")
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    SUMMARY_JSON.write_text(
        json.dumps(
            {
                "passed": passed,
                "total": total,
                "results": [result.__dict__ for result in results],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    results = [
        validate_architecture(),
        validate_implementation_contract(),
        validate_technical_debt(),
        validate_openapi_contract(),
        validate_bdd_contract(),
        validate_living_docs(),
        validate_workflow(),
    ]
    write_reports(results)

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
