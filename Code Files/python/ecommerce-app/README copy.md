# E-Commerce Payment Demo Application

## Overview

This is a demo e-commerce application used for the "Multi-Track - Your AI Development Toolkit" workshop. It demonstrates how to integrate documentation, testing, and technical debt analysis skills when adding new features to legacy code.

## Purpose

This codebase is intentionally designed with:
- **Legacy code patterns** - Shows realistic technical debt scenarios
- **Security issues** - Demonstrates how AI tools can identify vulnerabilities
- **Minimal test coverage** - Starting point for test-driven development exercises
- **Limited documentation** - Opportunity to practice documentation generation

## Structure

```
ecommerce-app/
├── src/
│   ├── payment/
│   │   ├── payment_processor.py  # Legacy payment processing (Stripe only)
│   │   └── __init__.py
│   └── orders/
│       └── order_service.py       # Order management service
├── tests/
│   └── payment/                   # Test files will be added here
├── docs/
│   └── api/                       # API documentation will be generated here
├── requirements.txt
└── README.md
```

## Current Features

- **Credit Card Payments**: Processes payments via Stripe API
- **Order Management**: Creates and tracks orders
- **Retry Logic**: Exponential backoff for failed payment attempts
- **Strategy Pattern**: Extensible payment method architecture

## Known Issues (Intentional Technical Debt)

These issues are included deliberately for workshop demonstration:

1. **Security Vulnerability (Line 47)**: API keys hardcoded in source code
2. **PCI DSS Violation (Line 112)**: Sensitive payment data logged in plaintext
3. **High Complexity (Line 203)**: `validate_payment` method has excessive cyclomatic complexity
4. **Missing Tests**: No test coverage for payment processing
5. **No Documentation**: No API documentation for payment endpoints

## Workshop Exercise

During the workshop, participants will:

1. **Use AI for Architecture Discovery**: Understand the existing payment module structure
2. **Run Security Analysis**: Identify vulnerabilities and technical debt
3. **Write Tests First**: Create BDD test specifications before implementing features
4. **Add Apple Pay Support**: Implement a new payment method following best practices
5. **Generate Documentation**: Auto-generate OpenAPI specs for the new feature

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone or download this repository
cd ecommerce-app

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (DO NOT use hardcoded keys in production!)
export STRIPE_API_KEY="your_test_key_here"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/payment/test_apple_pay.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Development Workflow (Demonstrated in Workshop)

### Phase 1: Architecture Discovery
Use AI to analyze the existing payment module and understand its structure.

### Phase 2: Risk Assessment
Run security scans to identify vulnerabilities before adding new features.

### Phase 3: Test-First Development
Write BDD test scenarios defining what the new feature should do.

### Phase 4: Implementation
Generate implementation code that satisfies tests and follows security best practices.

### Phase 5: Documentation
Auto-generate API documentation for downstream teams.

## Adding New Payment Methods

To add a new payment method (demonstrated with Apple Pay in the workshop):

1. **Extend `AbstractPaymentMethod`**: Create a new class inheriting from the abstract base
2. **Implement Required Methods**: `process_payment`, `validate_token`, `refund_payment`
3. **Follow Security Best practices**: 
   - Load API keys from environment variables
   - Redact sensitive data from logs
   - Implement proper error handling and rollback logic
4. **Register with PaymentProcessor**: Add the new method to the processor
5. **Write Comprehensive Tests**: Cover happy path and edge cases
6. **Document the API**: Generate OpenAPI specification

## Environment Variables

Create a `.env` file (not included in version control):

```bash
STRIPE_API_KEY=sk_test_your_key_here
APPLE_PAY_MERCHANT_ID=your_merchant_id_here
APPLE_PAY_API_KEY=your_apple_pay_key_here
```

## Resources

- **Workshop Materials**: See `/Facilitator Prompts/` and `/Participant Prompts/` folders
- **Slide Deck**: See `/PowerPoint/` folder
- **Integration Demo Script**: `multi-track-demo.md` in Facilitator Prompts

## License

This is a demonstration project for educational purposes only. Not intended for production use.

## Support

For workshop-related questions, contact your Collaborative Engineers or workshop facilitators.
