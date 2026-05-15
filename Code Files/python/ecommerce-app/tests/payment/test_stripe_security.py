import logging
from unittest.mock import MagicMock, patch

import pytest

from src.payment.payment_processor import StripePaymentMethod, _load_stripe_api_key


@pytest.fixture
def stripe_api_key(monkeypatch):
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_unit_test_placeholder")


def test_stripe_api_key_is_required(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="STRIPE_API_KEY environment variable is required"):
        _load_stripe_api_key()


@pytest.mark.parametrize("api_key", ["", "pk_test_public_key", "not_a_stripe_key"])
def test_stripe_api_key_must_be_secret_key(monkeypatch, api_key):
    monkeypatch.setenv("STRIPE_API_KEY", api_key)

    with pytest.raises(ValueError, match="sk_test_ or sk_live_"):
        _load_stripe_api_key()


def test_credit_card_success_log_excludes_sensitive_payment_data(stripe_api_key, caplog):
    method = StripePaymentMethod()
    payment_data = {
        "card_token": "tok_unit_test_token_12345",
        "amount": 42.50,
        "currency": "usd",
    }
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"id": "ch_test_123", "created": 1767225600}

    with caplog.at_level(logging.INFO), patch("requests.post", return_value=response):
        result = method.process_credit_card_payment("ORD-001", payment_data)

    assert result["status"] == "success"
    full_log = " ".join(record.getMessage() for record in caplog.records)
    assert "order_id=ORD-001" in full_log
    assert "payment_id=ch_test_123" in full_log
    assert payment_data["card_token"] not in full_log
    assert str(payment_data["amount"]) not in full_log


@pytest.mark.parametrize(
    "payment_data,expected",
    [
        ({"card_token": "tok_unit_test_token_12345", "amount": 10, "currency": "usd"}, True),
        ({"card_token": "bad_token", "amount": 10, "currency": "usd"}, False),
        ({"card_token": "tok_unit_test_token_12345", "amount": 0, "currency": "usd"}, False),
        ({"card_token": "tok_unit_test_token_12345", "amount": 1_000_000, "currency": "usd"}, False),
        ({"card_token": "tok_unit_test_token_12345", "amount": 10, "currency": "jpy"}, False),
        ({"amount": 10, "currency": "usd"}, False),
        ({"card_token": "tok_unit_test_token_12345", "currency": "usd"}, False),
        ({"card_token": "tok_unit_test_token_12345", "amount": 10}, True),
    ],
)
def test_validate_payment_preserves_existing_rules(stripe_api_key, payment_data, expected):
    assert StripePaymentMethod().validate_payment(payment_data) is expected
