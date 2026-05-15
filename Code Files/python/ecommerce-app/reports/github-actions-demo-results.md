# Python Integrated AI Demo Quality Gates: GitHub Actions Runbook

**Repository:** <https://github.com/shalabhdixit/Coding-for-Fun>  
**Workflow:** Python Integrated AI Demo Quality Gates  
**Prepared on:** May 15, 2026  
**Demo objective:** trigger the workflow in GitHub Actions, prove the Apple Pay implementation gates pass, and collect shareable evidence for workshop closeout.

---

## Executive Summary

The local preflight validates the core workflow content successfully: generated documentation, integrated quality gates, Python compilation, and Apple Pay BDD tests all pass. The only local gap is environmental: the workspace virtual environment has a corrupted `pip`, so `pytest-cov` could not be installed locally for the coverage command. GitHub Actions installs dependencies in a clean Ubuntu runner, so this local `pip` issue should not block the hosted workflow.

The public `Coding-for-Fun` repository currently shows only the older `.github/workflows/main.yml` Documentation Compliance workflow on `master`. To demonstrate this Python integrated AI quality-gates workflow, first push the workshop content and the workflow file into that repository, then trigger it from the Actions tab or by pushing a branch.

## Readiness Snapshot

| Area | Status | Evidence |
|---|---:|---|
| Workflow trigger design | Ready | Supports `push`, `pull_request`, and `workflow_dispatch`. |
| Documentation generation | Passed locally | `python tools/generate_demo_docs.py` completed. |
| Integrated quality gates | Passed locally | `7/7` quality gates passed. |
| Python compilation | Passed locally | `python -m compileall src tests tools` completed. |
| Apple Pay BDD suite | Passed locally | `14 passed` in `tests/payment/test_apple_pay.py`. |
| Coverage gate | Needs hosted runner or repaired local venv | Local `pytest-cov` install blocked by corrupted `pip`; workflow installs this in GitHub Actions. |
| Public GitHub repo workflow availability | Setup required | `Coding-for-Fun` currently exposes `.github/workflows/main.yml`, not this Python workflow. |

## Recommended Live Demo Path

Use the full workshop repository layout if you want to keep the existing folder structure exactly as it appears locally.

### 1. Prepare the Repository Content

The demo branch has been prepared at `demo/python-integrated-ai-quality-gates`.

### 2. Trigger the Workflow from GitHub Actions

1. Open <https://github.com/shalabhdixit/Coding-for-Fun/actions>.
2. Select **Python Integrated AI Demo Quality Gates** in the left workflow list.
3. Select **Run workflow**.
4. Choose branch `demo/python-integrated-ai-quality-gates`.
5. Select **Run workflow**.

Expected result: GitHub starts a new run named **Validate Python integrated AI workflow**.

### 3. Alternative Trigger: Push a Commit

The workflow also runs on every branch push. Any new commit to `demo/python-integrated-ai-quality-gates` will trigger a new run automatically.

## Expected Workflow Stages

| Stage | What It Proves | Expected Outcome |
|---|---|---:|
| Check out source | Repository content is available to the runner. | Pass |
| Set up Python | Python 3.11 and dependency cache are configured. | Pass |
| Install test dependencies | App dependencies plus `pytest-cov` install cleanly. | Pass |
| Generate living documentation | README and generated quality-gate docs are refreshed. | Pass |
| Validate integrated quality gates | Architecture, implementation, security guardrails, docs, BDD, and workflow checks pass. | Pass |
| Compile Python sources | `src`, `tests`, and `tools` are syntactically valid. | Pass |
| Run Apple Pay BDD acceptance suite | Apple Pay behavior is validated through executable scenarios. | Pass |
| Run coverage quality gate | Coverage for `src.payment` meets the configured minimum. | Pass |
| Generate HTML execution report | A self-contained report is produced for demos and troubleshooting. | Pass |
| Publish quality gate summary | Markdown summary is added to the Actions run summary. | Pass |
| Upload workflow evidence | Logs, reports, README, generated docs, and OpenAPI contract are retained as an artifact. | Pass |

## Evidence to Show During the Demo

After the workflow completes, open the run and show these artifacts in order:

1. **Job summary:** confirms the `7/7` quality gates table.
2. **BDD test log:** shows the Apple Pay acceptance suite passing.
3. **Coverage log:** shows the coverage percentage and threshold result.
4. **Artifact:** download `python-integrated-ai-quality-gate-evidence`.
5. **HTML report:** open `reports/integrated-ai-workflow-report.html` from the artifact bundle.
6. **Generated docs:** show `docs/generated/integrated-ai-demo-quality-gates.md` and `docs/api/apple-pay-openapi.yaml`.

## Success Criteria for the GitHub Run

- The Actions run completes with a green status.
- The job summary shows `Passed: 7/7`.
- The Apple Pay BDD suite passes.
- The coverage gate meets or exceeds the configured `55%` minimum.
- The artifact `python-integrated-ai-quality-gate-evidence` is available for download.
- The artifact includes `reports/integrated-ai-workflow-report.html`.
