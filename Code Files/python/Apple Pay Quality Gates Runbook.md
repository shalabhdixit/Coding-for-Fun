# Apple Pay Quality Gates Runbook

## Purpose

This runbook explains how to respond when the integrated AI workflow fails for the Apple Pay payment demo.

## Workflow Evidence

Every workflow run publishes the `python-integrated-ai-quality-gate-evidence` artifact. Download it and open:

- `reports/integrated-ai-workflow-report.html`
- `reports/quality-gates-summary.md`
- `reports/logs/04-bdd-tests.log`
- `reports/logs/05-coverage.log`

## Troubleshooting Paths

### Documentation Gate Fails

Run:

```bash
python tools/generate_demo_docs.py
python tools/generate_demo_docs.py --check
```
