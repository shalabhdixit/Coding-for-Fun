# TECH-DEBT: Payment Module Security Fixes - API Key, Log Redaction, Complexity

| Field | Value |
|---|---|
| **Issue Type** | Bug / Technical Debt |
| **Priority** | High |
| **Original Estimate** | 4h |
| **Component** | Payment |
| **Labels** | `security`, `pci-dss`, `tech-debt` |

## Description

The `payment_processor.py` module contains three confirmed issues identified in a security audit. All three must be resolved before the next PCI DSS review cycle.

## Acceptance Criteria

### AC-1 - Move Stripe API Key to Environment Variable

- [ ] Remove hardcoded `STRIPE_API_KEY = "sk_test_..."` constant from source
- [ ] Load key at runtime via `os.environ["STRIPE_API_KEY"]` using `python-dotenv`
- [ ] Application raises a clear `ValueError` at startup if the variable is absent or malformed
- [ ] `.env.example` updated with placeholder; `.env` confirmed in `.gitignore`
- [ ] No secret value appears in any commit, PR diff, or log output

### AC-2 - Redact Sensitive Payment Data from Logs

- [ ] Remove `logger.info(f"Payment successful: {payment_data}")`
- [ ] Replace with a log statement that records only `order_id` and `payment_id` - no token, no amount, no card data
- [ ] PCI DSS BDD assertion passes for all Apple Pay and Stripe scenarios

### AC-3 - Refactor `validate_payment()` to Reduce Cyclomatic Complexity

- [ ] Reduce cyclomatic complexity from ~10 to <= 5
- [ ] All existing validation rules preserved
- [ ] No change to the public method signature or return type (`bool`)
- [ ] All existing unit tests continue to pass; coverage on `validate_payment` remains >= 90%

## Out of Scope

- Apple Pay implementation
- Persistence layer / database changes
- Stripe SDK migration
