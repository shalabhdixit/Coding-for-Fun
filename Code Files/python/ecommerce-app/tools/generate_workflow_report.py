"""Generate a self-contained HTML execution report for the demo workflow."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LOGS = REPORTS / "logs"
OUTPUT = REPORTS / "integrated-ai-workflow-report.html"

WATCHED_FILES = [
    "README.md",
    "docs/generated/integrated-ai-demo-quality-gates.md",
    "docs/api/apple-pay-openapi.yaml",
    "docs/tickets/TECH-DEBT-payment-module-security-fixes.md",
    "tests/payment/apple_pay.feature",
    "tests/payment/test_apple_pay.py",
    "src/payment/apple_pay_payment_method.py",
    "src/payment/payment_processor.py",
    "tools/generate_demo_docs.py",
    "tools/validate_quality_gates.py",
    "tools/generate_workflow_report.py",
    ".github/workflows/integrated-ai-demo-quality-gates.yml",
]


def read_text(path: Path, fallback: str = "") -> str:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return fallback
    for encoding in ("utf-8", "utf-16", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def load_quality_gates() -> dict:
    path = REPORTS / "quality-gates.json"
    if not path.exists():
        return {"passed": 0, "total": 0, "results": []}
    return json.loads(read_text(path))


def collect_logs() -> list[dict[str, str | int]]:
    logs: list[dict[str, str | int]] = []
    if not LOGS.exists():
        return logs
    for path in sorted(LOGS.glob("*.log")):
        text = read_text(path)
        logs.append(
            {
                "name": path.name,
                "path": path.relative_to(ROOT).as_posix(),
                "lines": len(text.splitlines()),
                "chars": len(text),
                "text": text,
            }
        )
    return logs


def extract_digest() -> str:
    match = re.search(r"Source digest: `([a-f0-9]+)`", read_text(ROOT / "README.md"))
    return match.group(1) if match else "not-found"


def summarize_tests(logs: list[dict[str, str | int]]) -> dict[str, str | int]:
    combined = "\n".join(str(log["text"]) for log in logs)
    passed_match = re.search(r"(\d+) passed", combined)
    failed_match = re.search(r"(\d+) failed", combined)
    coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+([0-9]+%)", combined)
    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "coverage": coverage_match.group(1) if coverage_match else "not captured",
    }


def file_inventory() -> list[dict[str, str | int | bool]]:
    rows: list[dict[str, str | int | bool]] = []
    for relative in WATCHED_FILES:
        path = ROOT / relative
        text = read_text(path)
        rows.append(
            {
                "path": relative,
                "exists": path.exists(),
                "lines": len(text.splitlines()) if path.exists() else 0,
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return rows


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_report(args: argparse.Namespace) -> str:
    gates = load_quality_gates()
    logs = collect_logs()
    tests = summarize_tests(logs)
    files = file_inventory()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    passed = int(gates.get("passed", 0))
    total = int(gates.get("total", 0))
    health = "PASS" if passed == total and tests["failed"] == 0 else "NEEDS ATTENTION"

    gate_rows = "\n".join(
        f"<tr><td>{'PASS' if item.get('passed') else 'FAIL'}</td><td>{escape(item.get('name'))}</td><td>{escape(item.get('detail'))}</td></tr>"
        for item in gates.get("results", [])
    )
    file_rows = "\n".join(
        f"<tr><td>{'FOUND' if item['exists'] else 'MISSING'}</td><td><code>{escape(item['path'])}</code></td><td>{item['lines']}</td><td>{item['bytes']}</td></tr>"
        for item in files
    )
    log_panels = "\n".join(
        f"<details><summary>{escape(log['name'])} - {log['lines']} lines</summary><pre>{escape(log['text'])}</pre></details>"
        for log in logs
    ) or "<p>No logs were captured.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Integrated AI Workflow Execution Report</title>
  <style>
    body {{ margin: 0; background: #071018; color: #e8f1f8; font-family: Segoe UI, system-ui, sans-serif; }}
    header {{ padding: 24px 32px; border-bottom: 1px solid #284057; background: #101b29; }}
    main {{ padding: 24px 32px; max-width: 1320px; margin: auto; }}
    section {{ margin-bottom: 20px; padding: 20px; background: #101b29; border: 1px solid #284057; border-radius: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }}
    .card {{ padding: 16px; background: #162538; border: 1px solid #284057; border-radius: 8px; }}
    .metric {{ font-size: 34px; font-weight: 750; }}
    .muted {{ color: #9fb3c8; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #284057; text-align: left; vertical-align: top; }}
    th {{ color: #9fb3c8; text-transform: uppercase; font-size: 12px; }}
    code, pre {{ font-family: Cascadia Code, Consolas, monospace; }}
    pre {{ overflow: auto; max-height: 420px; background: #07121d; padding: 14px; border-radius: 8px; border: 1px solid #284057; white-space: pre-wrap; }}
  </style>
</head>
<body>
<header>
  <h1>Integrated AI Workflow Execution Report</h1>
  <p class="muted">Generated: {escape(generated_at)} | Branch: {escape(args.branch)} | Event: {escape(args.event)} | Digest: {escape(extract_digest())}</p>
  <strong>{health}</strong>
</header>
<main>
  <section><h2>Executive Summary</h2><div class="grid">
    <div class="card"><div class="metric">{passed}/{total}</div><div class="muted">Quality gates passed</div></div>
    <div class="card"><div class="metric">{tests['passed']}</div><div class="muted">BDD tests passed</div></div>
    <div class="card"><div class="metric">{escape(tests['coverage'])}</div><div class="muted">Coverage captured</div></div>
    <div class="card"><div class="metric">{len(logs)}</div><div class="muted">Workflow logs captured</div></div>
  </div></section>
  <section><h2>Quality Gate Results</h2><table><thead><tr><th>Status</th><th>Gate</th><th>Detail</th></tr></thead><tbody>{gate_rows}</tbody></table></section>
  <section><h2>File Inventory</h2><table><thead><tr><th>Status</th><th>File</th><th>Lines</th><th>Bytes</th></tr></thead><tbody>{file_rows}</tbody></table></section>
  <section><h2>Raw Execution Logs</h2>{log_panels}</section>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate HTML report for the integrated AI workflow.")
    parser.add_argument("--run-url", default=os.getenv("GITHUB_RUN_URL", "local execution"))
    parser.add_argument("--branch", default=os.getenv("GITHUB_REF_NAME", "local"))
    parser.add_argument("--sha", default=os.getenv("GITHUB_SHA", "local"))
    parser.add_argument("--event", default=os.getenv("GITHUB_EVENT_NAME", "local"))
    args = parser.parse_args()

    REPORTS.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_report(args), encoding="utf-8")
    print(f"Generated HTML workflow report: {OUTPUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
