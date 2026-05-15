"""Generate deterministic living documentation for the Apple Pay demo.

The workflow uses this script to prove that code, BDD scenarios, OpenAPI
documentation, and README content stay in sync after every push.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
README_SEED = ROOT / "README copy.md"
WORKFLOW_DOC = ROOT / "docs" / "generated" / "integrated-ai-demo-quality-gates.md"

README_START = "<!-- AI-DEMO-DOCS:START -->"
README_END = "<!-- AI-DEMO-DOCS:END -->"

SOURCE_INPUTS = [
    ROOT / "src" / "payment" / "payment_processor.py",
    ROOT / "src" / "payment" / "apple_pay_payment_method.py",
    ROOT / "tests" / "payment" / "apple_pay.feature",
    ROOT / "tests" / "payment" / "test_apple_pay.py",
    ROOT / "docs" / "api" / "apple-pay-openapi.yaml",
    ROOT / "docs" / "tickets" / "TECH-DEBT-payment-module-security-fixes.md",
    ROOT / "tools" / "generate_workflow_report.py",
    ROOT / ".github" / "workflows" / "integrated-ai-demo-quality-gates.yml",
]


@dataclass(frozen=True)
class Scenario:
    kind: str
    title: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in SOURCE_INPUTS:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def extract_classes(path: Path) -> list[str]:
    tree = ast.parse(read_text(path))
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def extract_functions(path: Path) -> list[str]:
    tree = ast.parse(read_text(path))
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def extract_scenarios(feature_path: Path) -> list[Scenario]:
    scenarios: list[Scenario] = []
    pattern = re.compile(r"^\s*(Scenario(?: Outline)?):\s+(.+?)\s*$")
    for line in read_text(feature_path).splitlines():
        match = pattern.match(line)
        if match:
            scenarios.append(Scenario(kind=match.group(1), title=match.group(2)))
    return scenarios


def markdown_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Gate | Evidence |", "|---|---|"]
    lines.extend(f"| {gate} | {evidence} |" for gate, evidence in rows)
    return "\n".join(lines)


def build_readme_section(digest: str, scenarios: list[Scenario]) -> str:
    scenario_titles = ", ".join(s.title for s in scenarios[:4])
    if len(scenarios) > 4:
        scenario_titles += f", plus {len(scenarios) - 4} more"

    rows = markdown_table(
        [
            (
                "Architecture discovery",
                "Confirms PaymentProcessor strategy registration and ApplePayPaymentMethod extension points.",
            ),
            (
                "Technical debt guardrail",
                "Requires the legacy security debt ticket while preventing new Apple Pay secret or raw-token logging regressions.",
            ),
            (
                "BDD test contract",
                f"Runs {len(scenarios)} Apple Pay scenarios covering happy path, validation, retries, timeout, and rollback.",
            ),
            (
                "API documentation",
                "Validates docs/api/apple-pay-openapi.yaml for auth, schemas, examples, retry headers, and error responses.",
            ),
            (
                "Living README",
                f"This section is regenerated from source digest `{digest}` on every workflow run.",
            ),
            (
                "HTML execution report",
                "Publishes a self-contained debugging report with gate results, file inventory, raw logs, and troubleshooting guidance.",
            ),
        ]
    )

    return f"""{README_START}
## Integrated AI Workflow Quality Gates

This repository includes an end-to-end GitHub Actions demo that mirrors the five stages in the workshop script: architecture discovery, technical debt assessment, test-first development, implementation validation, and API documentation generation.

{rows}

**Current Apple Pay scenario map:** {scenario_titles}.

Generated docs:
- [Integrated AI demo quality gates](docs/generated/integrated-ai-demo-quality-gates.md)
- [Apple Pay OpenAPI spec](docs/api/apple-pay-openapi.yaml)
- `reports/integrated-ai-workflow-report.html` as a workflow artifact after each Actions run

Workflow entry points:
- `.github/workflows/integrated-ai-demo-quality-gates.yml` when `ecommerce-app` is the repository root
- `../../../.github/workflows/python-integrated-ai-demo-quality-gates.yml` when the full workshop folder is the repository root

Source digest: `{digest}`
{README_END}"""


def build_workflow_doc(digest: str, scenarios: list[Scenario]) -> str:
    payment_classes = extract_classes(ROOT / "src" / "payment" / "payment_processor.py")
    apple_pay_classes = extract_classes(ROOT / "src" / "payment" / "apple_pay_payment_method.py")
    apple_pay_functions = extract_functions(ROOT / "src" / "payment" / "apple_pay_payment_method.py")
    scenario_lines = "\n".join(f"| {index} | {s.kind} | {s.title} |" for index, s in enumerate(scenarios, start=1))

    return f"""# Integrated AI Demo Quality Gates

This file is generated by `tools/generate_demo_docs.py`. Edit the source, tests, or OpenAPI file, then run the generator instead of editing this file by hand.

Source digest: `{digest}`

## Demo Story

The workflow validates the same learning arc as `Facilitator Prompts/multi-track-demo.md`, but turns it into a repeatable branch-push automation:

1. Discover the payment architecture from source.
2. Preserve the technical debt register for known legacy risks.
3. Run BDD tests as the Apple Pay acceptance contract.
4. Validate the Apple Pay implementation surface and security guardrails.
5. Regenerate and validate README plus OpenAPI documentation.

## Architecture Discovery Evidence

Payment module classes discovered from source:

- `src/payment/payment_processor.py`: {", ".join(payment_classes)}
- `src/payment/apple_pay_payment_method.py`: {", ".join(apple_pay_classes)}

Apple Pay public and helper functions discovered from source include: {", ".join(sorted(set(apple_pay_functions)))}.

## BDD Acceptance Contract

| # | Type | Scenario |
|---|---|---|
{scenario_lines}

## Quality Gates

| Stage | Gate | What breaks the build |
|---|---|---|
| Architecture | Strategy-pattern contract | Missing `PaymentProcessor`, missing `ApplePayPaymentMethod`, or missing registration-compatible payment methods. |
| Technical debt | Known-risk containment | Missing tech-debt ticket, new Apple Pay hardcoded secrets, raw token logging, or non-HTTPS Apple Pay API configuration. |
| Testing | BDD suite | Any failing pytest-bdd Apple Pay scenario. |
| Implementation | Payment behavior | Missing token validation, retry orchestration, refund method, or idempotency header support. |
| Documentation | Living docs | README section or this generated document is stale compared with the source digest. |
| API docs | OpenAPI contract | Missing endpoint, schemas, bearer auth, examples, rate-limit metadata, or expected error responses. |
| Evidence | HTML report | Missing execution summary, change summary, file inventory, troubleshooting guidance, or raw workflow logs. |

## Automatic README Update

On every push to any branch, GitHub Actions runs the generator. If README or generated docs change, the workflow commits those generated documentation changes back to the same branch using the GitHub Actions bot. A second run should then be clean because the digest is stable.

This app also has a root-level wrapper workflow at `../../../.github/workflows/python-integrated-ai-demo-quality-gates.yml` for workshop repositories that keep all language tracks in one repo.

## Files Watched By The Digest

{chr(10).join(f"- `{path.relative_to(ROOT).as_posix()}`" for path in SOURCE_INPUTS)}
"""


def insert_readme_section(base: str, section: str) -> str:
    if README_START in base and README_END in base:
        pattern = re.compile(f"{re.escape(README_START)}.*?{re.escape(README_END)}", re.S)
        return pattern.sub(section, base)

    license_heading = "\n## License\n"
    if license_heading in base:
        return base.replace(license_heading, f"\n{section}\n{license_heading}", 1)

    return base.rstrip() + "\n\n" + section + "\n"


def build_artifacts() -> dict[Path, str]:
    digest = source_digest()
    scenarios = extract_scenarios(ROOT / "tests" / "payment" / "apple_pay.feature")
    seed = read_text(README if README.exists() else README_SEED)
    readme_section = build_readme_section(digest, scenarios)
    return {
        README: insert_readme_section(seed, readme_section),
        WORKFLOW_DOC: build_workflow_doc(digest, scenarios),
    }


def write_artifacts(artifacts: dict[Path, str]) -> list[Path]:
    changed: list[Path] = []
    for path, content in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        current = read_text(path) if path.exists() else ""
        normalized = content.rstrip() + "\n"
        if current != normalized:
            path.write_text(normalized, encoding="utf-8")
            changed.append(path)
    return changed


def check_artifacts(artifacts: dict[Path, str]) -> list[Path]:
    stale: list[Path] = []
    for path, expected in artifacts.items():
        if not path.exists() or read_text(path) != expected.rstrip() + "\n":
            stale.append(path)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic demo documentation.")
    parser.add_argument("--check", action="store_true", help="Fail if generated docs are stale.")
    args = parser.parse_args()

    missing = [path for path in SOURCE_INPUTS if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing source input: {path.relative_to(ROOT).as_posix()}", file=sys.stderr)
        return 2

    artifacts = build_artifacts()
    if args.check:
        stale = check_artifacts(artifacts)
        if stale:
            print("Generated documentation is stale:", file=sys.stderr)
            for path in stale:
                print(f"- {path.relative_to(ROOT).as_posix()}", file=sys.stderr)
            return 1
        print("Generated documentation is in sync.")
        return 0

    changed = write_artifacts(artifacts)
    if changed:
        print("Updated generated documentation:")
        for path in changed:
            print(f"- {path.relative_to(ROOT).as_posix()}")
    else:
        print("Generated documentation already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
