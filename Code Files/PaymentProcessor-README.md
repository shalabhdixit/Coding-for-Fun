# PaymentProcessor

**A secure, PCI-DSS compliant payment processing service with gateway abstraction, input validation, and comprehensive error handling. Supports multiple payment gateways with configurable routing and tokenization.**

---

## Badges

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![TypeScript](https://img.shields.io/badge/typescript-5.0%2B-blue)
![Java](https://img.shields.io/badge/java-17%2B-red)
![.NET](https://img.shields.io/badge/.NET-8.0%2B-purple)
![License](https://img.shields.io/badge/license-MIT-green)
![PCI-DSS](https://img.shields.io/badge/PCI--DSS-Level%201-critical)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)

---

## Features

- **Secure Payment Processing**: Process transactions with full encryption and tokenization
- **Gateway Abstraction**: Pluggable gateway layer supporting Stripe, PayPal, and custom providers
- **PCI-DSS Compliance**: Card data never stored in plaintext; tokenization enforced at entry
- **Input Validation**: Luhn algorithm card validation, amount bounds checking, currency verification
- **Refund Handling**: Full and partial refunds with idempotency guarantees
- **Rate Limiting**: Configurable per-merchant rate limits to prevent abuse
- **Comprehensive Error Handling**: Typed exceptions with actionable error codes
- **Audit Logging**: All transactions logged with masked card data for compliance

---

## Installation

### Python
```bash
pip install payment-processor
# or from source
pip install -r requirements.txt
```

### TypeScript/Node.js
```bash
npm install @atmosera/payment-processor
```

### Java
Add to your `pom.xml`:
```xml
<dependency>
    <groupId>com.atmosera</groupId>
    <artifactId>payment-processor</artifactId>
    <version>1.0.0</version>
</dependency>
```

### .NET/C#
```bash
dotnet add package Atmosera.PaymentProcessor
```

---

## Quick Start

### Python Example
```python
from payment_processor import PaymentProcessor

processor = PaymentProcessor(gateway="stripe")
result = processor.process_payment(
    amount=99.99,
    currency="USD",
    card_number="4111111111111111",
    expiry="12/26",
    cvv="123"
)
print(f"Transaction ID: {result.transaction_id}")
print(f"Status: {result.status}")
```

### TypeScript Example
```typescript
import { PaymentProcessor } from './PaymentProcessor';

const processor = new PaymentProcessor({ gateway: 'stripe' });
const result = await processor.processPayment({
  amount: 99.99,
  currency: 'USD',
  cardNumber: '4111111111111111',
  expiry: '12/26',
  cvv: '123'
});
console.log(`Transaction ID: ${result.transactionId}`);
```

### Java Example
```java
PaymentProcessor processor = new PaymentProcessor("stripe");
PaymentResult result = processor.processPayment(
    99.99, "USD", "4111111111111111", "12/26", "123"
);
System.out.println("Transaction ID: " + result.getTransactionId());
```

### .NET Example
```csharp
var processor = new PaymentProcessor(gateway: "stripe");
var result = processor.ProcessPayment(
    amount: 99.99m,
    currency: "USD",
    cardNumber: "4111111111111111",
    expiry: "12/26",
    cvv: "123"
);
Console.WriteLine($"Transaction ID: {result.TransactionId}");
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PAYMENT_GATEWAY` | Payment gateway provider (stripe, paypal, mock) | `mock` | Yes (production) |
| `PAYMENT_API_KEY` | Gateway API key for authentication | `None` | Yes (production) |
| `PAYMENT_API_SECRET` | Gateway API secret | `None` | Yes (production) |
| `PAYMENT_ENVIRONMENT` | Environment (sandbox, production) | `sandbox` | No |
| `PAYMENT_TIMEOUT` | Gateway request timeout in seconds | `30` | No |
| `PAYMENT_MAX_RETRIES` | Maximum retry attempts on transient failures | `3` | No |
| `PAYMENT_RATE_LIMIT` | Max transactions per minute per merchant | `100` | No |
| `PAYMENT_LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARN, ERROR) | `INFO` | No |
| `PAYMENT_ENCRYPTION_KEY` | AES-256 key for data-at-rest encryption | `None` | Yes (production) |

### Environment Selection

```bash
# Development (uses mock gateway, no real charges)
export PAYMENT_GATEWAY="mock"
export PAYMENT_ENVIRONMENT="sandbox"

# Staging (uses sandbox gateway for integration tests)
export PAYMENT_GATEWAY="stripe"
export PAYMENT_ENVIRONMENT="sandbox"
export PAYMENT_API_KEY="sk_test_..."

# Production
export PAYMENT_GATEWAY="stripe"
export PAYMENT_ENVIRONMENT="production"
export PAYMENT_API_KEY="sk_live_..."
export PAYMENT_API_SECRET="whsec_..."
export PAYMENT_ENCRYPTION_KEY="base64-encoded-256-bit-key"
```

### API Key Management

- **Never commit API keys** to version control
- Use secrets managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Rotate keys every 90 days (or immediately if compromised)
- Use separate keys for sandbox/production
- Restrict API key permissions to minimum required scope

---

## API Reference

### Core Methods

#### `process_payment(amount, currency, card_number, expiry, cvv)`

**Description**: Processes a payment transaction through the configured gateway. Validates card data, tokenizes sensitive information, and submits the charge.

**Parameters**:
- `amount` (float/decimal, required): Transaction amount. Must be > 0 and <= gateway maximum
- `currency` (string, required): ISO 4217 currency code (e.g., "USD", "EUR", "GBP")
- `card_number` (string, required): Full card number (validated via Luhn algorithm)
- `expiry` (string, required): Card expiration in MM/YY format
- `cvv` (string, required): 3-4 digit Card Verification Value

**Returns**: `PaymentResult` object containing:
- `transaction_id` (string): Unique transaction identifier
- `status` (string): "approved", "declined", "pending"
- `gateway_response` (object): Raw gateway response (masked)
- `timestamp` (datetime): Transaction timestamp (UTC)

**Example**:
```python
result = processor.process_payment(
    amount=149.99,
    currency="USD",
    card_number="4111111111111111",
    expiry="12/26",
    cvv="123"
)
if result.status == "approved":
    print(f"Payment successful: {result.transaction_id}")
```

---

#### `refund(transaction_id, amount=None)`

**Description**: Issues a full or partial refund for a previously successful transaction.

**Parameters**:
- `transaction_id` (string, required): Original transaction ID to refund
- `amount` (float/decimal, optional): Partial refund amount. If omitted, full refund is issued

**Returns**: `RefundResult` object containing:
- `refund_id` (string): Unique refund identifier
- `status` (string): "processed", "pending", "failed"
- `refunded_amount` (float): Amount actually refunded

**Example**:
```python
# Full refund
refund = processor.refund(transaction_id="txn_abc123")

# Partial refund
refund = processor.refund(transaction_id="txn_abc123", amount=50.00)
```

---

#### `validate_card(card_number)`

**Description**: Validates a card number using the Luhn algorithm without processing a transaction.

**Parameters**:
- `card_number` (string, required): Card number to validate

**Returns**: `bool` - True if card number passes Luhn check

**Example**:
```python
is_valid = processor.validate_card("4111111111111111")  # True
is_valid = processor.validate_card("1234567890123456")  # False
```

---

#### `tokenize(card_number, expiry)`

**Description**: Converts raw card data into a secure, reusable token for future transactions.

**Parameters**:
- `card_number` (string, required): Full card number
- `expiry` (string, required): Card expiration in MM/YY format

**Returns**: `Token` object containing:
- `token_id` (string): Secure token for future use
- `last_four` (string): Last 4 digits for display
- `card_brand` (string): Detected card brand (Visa, Mastercard, etc.)

**Example**:
```python
token = processor.tokenize("4111111111111111", "12/26")
# Use token for future payments (no raw card data needed)
result = processor.process_payment_with_token(token.token_id, amount=99.99)
```

---

## Error Handling

### Exception Types

| Error | Code | HTTP Status | Cause | Solution |
|-------|------|-------------|-------|----------|
| `InvalidCardError` | `CARD_001` | 400 | Card number fails Luhn validation | Verify card number, check for typos |
| `CardExpiredError` | `CARD_002` | 400 | Card expiration date is in the past | Request updated card from customer |
| `InsufficientFundsError` | `PAY_001` | 402 | Account balance too low | Suggest alternative payment or lower amount |
| `CardDeclinedError` | `PAY_002` | 402 | Issuer declined the transaction | Contact card issuer or try another card |
| `GatewayTimeoutError` | `GW_001` | 504 | Payment gateway did not respond | Retry with exponential backoff |
| `GatewayUnavailableError` | `GW_002` | 503 | Gateway is down or unreachable | Fallback to secondary gateway if configured |
| `RateLimitExceededError` | `RATE_001` | 429 | Too many requests in time window | Wait and retry, implement client-side throttling |
| `DuplicateTransactionError` | `TXN_001` | 409 | Idempotency key already used | Use a new idempotency key or retrieve existing result |
| `InvalidAmountError` | `VAL_001` | 400 | Amount is zero, negative, or exceeds limits | Validate amount before submission |
| `InvalidCurrencyError` | `VAL_002` | 400 | Unsupported currency code | Use ISO 4217 codes; check supported list |
| `AuthenticationError` | `AUTH_001` | 401 | Invalid API key or secret | Verify credentials and environment |
| `RefundExceedsChargeError` | `REF_001` | 400 | Refund amount > original charge | Verify refund amount <= remaining balance |

### Error Handling Pattern

**Python**:
```python
from payment_processor import (
    PaymentProcessor,
    InvalidCardError,
    InsufficientFundsError,
    GatewayTimeoutError,
    CardDeclinedError
)

processor = PaymentProcessor(gateway="stripe")

try:
    result = processor.process_payment(
        amount=99.99,
        currency="USD",
        card_number=card_number,
        expiry=expiry,
        cvv=cvv
    )
except InvalidCardError as e:
    # Client error: bad card data
    print(f"Card validation failed: {e.message} (code: {e.code})")
    # Prompt user to re-enter card details
except InsufficientFundsError as e:
    # Insufficient balance
    print(f"Payment declined: {e.message}")
    # Suggest lower amount or different card
except CardDeclinedError as e:
    # Issuer declined
    print(f"Card declined: {e.message}")
    # Suggest contacting card issuer
except GatewayTimeoutError as e:
    # Transient error: safe to retry
    print(f"Gateway timeout: {e.message}")
    # Implement retry with exponential backoff
except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
    # Log full error (without sensitive data) and alert ops
```

**TypeScript**:
```typescript
import {
  PaymentProcessor,
  InvalidCardError,
  InsufficientFundsError,
  GatewayTimeoutError
} from './PaymentProcessor';

const processor = new PaymentProcessor({ gateway: 'stripe' });

try {
  const result = await processor.processPayment({
    amount: 99.99,
    currency: 'USD',
    cardNumber,
    expiry,
    cvv
  });
} catch (error) {
  if (error instanceof InvalidCardError) {
    console.error(`Card invalid: ${error.message} (${error.code})`);
  } else if (error instanceof InsufficientFundsError) {
    console.error(`Insufficient funds: ${error.message}`);
  } else if (error instanceof GatewayTimeoutError) {
    console.error(`Gateway timeout - retrying...`);
    // Implement retry logic
  } else {
    console.error(`Unexpected error: ${error}`);
  }
}
```

---

## Security Considerations

### PCI-DSS Compliance

This service is designed with **PCI-DSS Level 1** requirements in mind:

| PCI-DSS Requirement | Implementation |
|---------------------|---------------|
| **Req 3**: Protect stored cardholder data | Card numbers are **never stored**; tokenized immediately upon receipt |
| **Req 4**: Encrypt transmission | All gateway communication uses **TLS 1.2+** |
| **Req 6**: Develop secure systems | Input validation, secure coding practices, dependency scanning |
| **Req 7**: Restrict access | API key-based authentication with least-privilege access |
| **Req 8**: Identify and authenticate | Unique transaction IDs, idempotency keys |
| **Req 10**: Track and monitor access | Audit logging with masked card data |
| **Req 11**: Test security systems | Automated security scanning in CI/CD |
| **Req 12**: Maintain security policy | Security-focused code review checklist |

### Card Data Handling

```
+-------------------------------------------------------------+
|  CARD DATA LIFECYCLE (PCI-DSS Compliant)                    |
|                                                             |
|  1. RECEIVE    -> Card data enters system via HTTPS/TLS 1.2+|
|  2. VALIDATE   -> Luhn check + format validation (in memory)|
|  3. TOKENIZE   -> Immediately convert to token              |
|  4. TRANSMIT   -> Only token + encrypted payload to gateway |
|  5. DESTROY    -> Raw card data wiped from memory           |
|                                                             |
|  WARNING: RAW CARD DATA NEVER:                              |
|     - Written to disk                                       |
|     - Stored in database                                    |
|     - Written to log files                                  |
|     - Cached in memory beyond transaction scope             |
|     - Transmitted without encryption                        |
+-------------------------------------------------------------+
```

### Logging Security

**What IS Logged** (safe for audit trails):
- Transaction IDs
- Timestamps (UTC)
- Amounts and currencies
- Masked card numbers (first 6, last 4 only: `411111******1111`)
- Card brand (Visa, Mastercard)
- Transaction status (approved/declined)
- Error codes (without sensitive context)
- Merchant ID

**What is NEVER Logged**:
- Full card numbers (PAN)
- CVV/CVC codes
- Card expiration dates
- API keys or secrets
- Full gateway responses containing card data
- Customer PII (names, addresses) in payment logs

### Secure Logging Example

```python
import logging

logger = logging.getLogger("payment_processor")

# CORRECT: Masked card data in logs
logger.info(
    "Payment processed",
    extra={
        "transaction_id": result.transaction_id,
        "amount": amount,
        "currency": currency,
        "card_last_four": card_number[-4:],
        "card_brand": "visa",
        "status": "approved",
        "timestamp": datetime.utcnow().isoformat()
    }
)

# WRONG: NEVER do this (PCI violation)
# logger.info(f"Processing card {card_number} with CVV {cvv}")
# logger.debug(f"Gateway response: {raw_gateway_response}")
# logger.info(f"API Key used: {api_key}")
```

### Input Validation Security

| Input | Validation | Threat Mitigated |
|-------|-----------|------------------|
| `card_number` | Luhn algorithm + length check + allowed characters | Invalid data, injection |
| `amount` | > 0, <= max limit, numeric only | Negative charges, overflow |
| `currency` | ISO 4217 whitelist | Injection, invalid processing |
| `expiry` | MM/YY format + future date check | Expired cards, format injection |
| `cvv` | 3-4 digits only | Injection, brute force |
| `transaction_id` | UUID format validation | Injection, enumeration |

### Rate Limiting

```python
# Rate limiting prevents:
# - Brute-force card testing (BIN attacks)
# - Denial of service
# - Excessive refund attempts

# Default limits:
# - 100 transactions/minute per merchant
# - 10 failed attempts -> 15-minute cooldown
# - 3 refunds/hour per transaction
```

### Security Checklist for Deployment

- [ ] API keys stored in secrets manager (not env files in repo)
- [ ] TLS 1.2+ enforced on all endpoints
- [ ] Card data tokenized before any persistence
- [ ] No PAN/CVV in any log output (verified via log audit)
- [ ] Rate limiting enabled and tuned
- [ ] Dependency vulnerability scan passes
- [ ] Penetration test completed (annual minimum)
- [ ] PCI SAQ (Self-Assessment Questionnaire) current
- [ ] Incident response plan documented
- [ ] Key rotation schedule configured (90-day max)

---

## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit changes: `git commit -m "Add description of changes"`
4. Push to branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

### Coding Style

- Follow language-specific conventions (PEP 8 for Python, ESLint for TypeScript, checkstyle for Java)
- Write clear, descriptive commit messages
- Add tests for new features (minimum 80% coverage)
- Update documentation to reflect changes

### Security-Specific PR Requirements

- **No hardcoded secrets** (automated scanning enforced)
- **No raw card data in tests** (use test card numbers only: `4111111111111111`)
- **Security review required** for changes to payment flow, validation, or logging
- **Dependency updates** must pass vulnerability scanning

### Testing

```bash
# Python
pytest tests/ -v --cov=src

# TypeScript
npm test -- --coverage

# Java
mvn test -Dtest=PaymentProcessorTest

# .NET
dotnet test --filter "Category=PaymentProcessor"
```

### Code Review Process

1. All PRs require at least 2 approvals (1 must be security team for payment changes)
2. CI/CD tests must pass before merging
3. Security scanning (SAST/DAST) must pass
4. No merge conflicts allowed
5. PCI compliance checklist reviewed for relevant changes

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Support

For issues, bugs, or feature requests, please open an issue on the project's GitHub repository.

**Security Vulnerabilities**: If you discover a security vulnerability, do **NOT** open a public issue. Email security@[TODO: your-domain].com with details.
