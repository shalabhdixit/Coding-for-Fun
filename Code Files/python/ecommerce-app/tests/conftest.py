"""
conftest.py - pytest configuration for the ecommerce-app test suite.
"""

import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

os.environ.setdefault("STRIPE_API_KEY", "sk_test_unit_test_placeholder")
os.environ.setdefault("APPLE_PAY_API_KEY", "apay_test_unit_test_placeholder")
os.environ.setdefault("APPLE_PAY_API_URL", "https://api.example.com/v1/payments/apple-pay")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def pytest_configure(config):
    config.addinivalue_line("markers", "apple_pay: marks tests that exercise Apple Pay payment flows")
    config.addinivalue_line("markers", "pci_dss: marks tests that validate PCI DSS log-sanitisation requirements")
    config.addinivalue_line("markers", "retry: marks tests that exercise exponential back-off retry behaviour")
    config.addinivalue_line("markers", "rollback: marks tests that exercise compensating-transaction rollback")


@pytest.fixture(autouse=True)
def reset_logging(caplog):
    caplog.clear()
    yield
