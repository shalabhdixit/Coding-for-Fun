"""
Apple Pay Payment Method
========================
Implements AbstractPaymentMethod for Apple Pay wallet payments,
integrating into the existing PaymentProcessor strategy pattern.

Security:
  - API key loaded exclusively from APPLE_PAY_API_KEY environment variable.
  - No payment token, card data, or raw payment_data dict is ever written
    to logs (PCI DSS Req 3.4 / Req 10.3).
  - HTTPS is enforced on the configured API URL.
  - An Idempotency-Key header (order-{order_id}) prevents double-charges on retry.
"""

import logging
import os
import time
from typing import Optional

import requests

from .payment_processor import AbstractPaymentMethod

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level constants — all tuneable via environment variables
# ---------------------------------------------------------------------------
_TOKEN_PREFIX: str = "apay_tok_"
_TOKEN_MIN_LENGTH: int = 20
_MAX_AMOUNT: float = 10_000.00
_VALID_CURRENCIES: frozenset = frozenset({"usd", "eur", "gbp", "cad", "aud"})
_MAX_RETRIES: int = 3
_BASE_DELAY_SECONDS: float = 1.0
_DEFAULT_API_URL: str = "https://api.example.com/v1/payments/apple-pay"
_REQUEST_TIMEOUT_SECONDS: int = 10


class ApplePayProcessor(AbstractPaymentMethod):
    """
    Apple Pay payment processor for the PaymentProcessor strategy pattern.

    Register with PaymentProcessor as::

        processor.register_payment_method(
            "apple_pay", apple_pay_processor.process_apple_pay_payment
        )

    Environment variables:
        APPLE_PAY_API_KEY  — Required. Apple Pay merchant API key.
        APPLE_PAY_API_URL  — Optional. Defaults to _DEFAULT_API_URL.
    """

    def __init__(self) -> None:
        self._api_key: str = os.getenv("APPLE_PAY_API_KEY", "")
        self._api_url: str = os.getenv("APPLE_PAY_API_URL", _DEFAULT_API_URL)
        self._max_retries: int = _MAX_RETRIES
        self._base_delay: float = _BASE_DELAY_SECONDS

        if self._api_key:
            self._validate_api_url(self._api_url)
        else:
            logger.warning(
                "APPLE_PAY_API_KEY is not set. Apple Pay payments will fail at runtime."
            )

    # ------------------------------------------------------------------
    # AbstractPaymentMethod interface
    # ------------------------------------------------------------------

    def process_payment(self, order_id: str, payment_data: dict) -> dict:
        """
        AbstractPaymentMethod entry point. Delegates to process_apple_pay_payment.

        Args:
            order_id: Unique identifier of the pending order.
            payment_data: Dict with apple_pay_token, amount, and currency.

        Returns:
            Dict with 'status' key ('success' or 'error').
        """
        return self.process_apple_pay_payment(order_id, payment_data)

    def validate_token(self, token: str) -> bool:
        """
        Validate the format of an Apple Pay payment token.

        Args:
            token: Apple Pay token string to validate.

        Returns:
            True if the token starts with 'apay_tok_' and is at least
            20 characters long, False otherwise.
        """
        return (
            isinstance(token, str)
            and token.startswith(_TOKEN_PREFIX)
            and len(token) >= _TOKEN_MIN_LENGTH
        )

    def refund_payment(self, payment_id: str) -> dict:
        """
        Refund a previously captured Apple Pay charge.

        Makes a single POST to {api_url}/{payment_id}/refund.
        Does not retry — callers are responsible for retry on refund failures.

        Args:
            payment_id: Identifier of the Apple Pay charge to refund.

        Returns:
            Dict with 'status' ('success' or 'error') and 'message' on error.

        Raises:
            requests.exceptions.RequestException: Propagated to caller so
                rollback orchestration can distinguish network vs. API errors.
        """
        if not payment_id:
            return {"status": "error", "message": "payment_id is required for refund"}

        refund_url = f"{self._api_url}/{payment_id}/refund"
        headers = self._build_request_headers()

        try:
            response = requests.post(refund_url, headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS)
        except requests.exceptions.RequestException:
            logger.error("Refund network error for payment_id=%s", payment_id)
            raise

        if response.status_code == 200:
            logger.info("Refund issued successfully for payment_id=%s", payment_id)
            return {"status": "success", "payment_id": payment_id}

        error_message = _extract_api_error(response)
        logger.error("Refund declined for payment_id=%s: %s", payment_id, error_message)
        return {"status": "error", "message": error_message}

    # ------------------------------------------------------------------
    # Primary payment entry point
    # ------------------------------------------------------------------

    def process_apple_pay_payment(self, order_id: str, payment_data: dict) -> dict:
        """
        Validate payment data and execute an Apple Pay charge with retry.

        Validation failures are returned immediately without any network call.
        Transient network errors are retried up to _max_retries times using
        exponential back-off. Timeout errors are distinguished in the final
        error message.

        Args:
            order_id: Unique identifier of the pending order.
            payment_data: Dict containing:
                apple_pay_token (str)  — wallet token from the Apple Pay SDK.
                amount (float)         — charge amount in major currency units.
                currency (str)         — ISO 4217 code; defaults to 'usd'.

        Returns:
            On success: {'status': 'success', 'payment_id': str, 'timestamp': int}
            On failure: {'status': 'error', 'message': str}
        """
        validation_error = self._validate_payment_data(payment_data)
        if validation_error:
            logger.warning(
                "Apple Pay validation failed for order_id=%s: %s", order_id, validation_error
            )
            return {"status": "error", "message": validation_error}

        return self._execute_with_retry(order_id, payment_data)

    def validate_payment(self, payment_data: dict) -> bool:
        """
        Public convenience wrapper — returns True when all payment fields are valid.

        Args:
            payment_data: Dict with apple_pay_token, amount, and optional currency.

        Returns:
            True if valid, False otherwise.
        """
        return self._validate_payment_data(payment_data) is None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_payment_data(self, payment_data: dict) -> Optional[str]:
        """
        Validate all required payment fields.

        Checks are ordered to fail fast on the most likely errors first.

        Args:
            payment_data: Raw payment data dict from the caller.

        Returns:
            None when all fields are valid, or a human-readable error string
            describing the first failing constraint.
        """
        if not payment_data:
            return "Invalid Apple Pay token: payment data is missing"

        token_error = self._validate_token_field(payment_data.get("apple_pay_token"))
        if token_error:
            return token_error

        amount_error = self._validate_amount_field(payment_data.get("amount"))
        if amount_error:
            return amount_error

        currency_error = self._validate_currency_field(payment_data.get("currency", "usd"))
        if currency_error:
            return currency_error

        return None

    def _validate_token_field(self, token: object) -> Optional[str]:
        """
        Validate the apple_pay_token field.

        Args:
            token: Value from payment_data['apple_pay_token'].

        Returns:
            None if valid, error string otherwise.
        """
        if not self.validate_token(token):  # type: ignore[arg-type]
            return (
                f"Invalid Apple Pay token: must start with '{_TOKEN_PREFIX}' "
                f"and be at least {_TOKEN_MIN_LENGTH} characters"
            )
        return None

    def _validate_amount_field(self, amount: object) -> Optional[str]:
        """
        Validate the amount field against type and Apple Pay transaction limits.

        Args:
            amount: Value from payment_data['amount'].

        Returns:
            None if valid, error string otherwise.
        """
        if amount is None or not isinstance(amount, (int, float)):
            return "Invalid payment data: amount is required and must be numeric"
        if amount <= 0:
            return "Invalid payment data: amount must be greater than zero"
        if amount > _MAX_AMOUNT:
            return (
                f"Payment amount {amount} exceeds Apple Pay transaction limit of {_MAX_AMOUNT}"
            )
        return None

    def _validate_currency_field(self, currency: object) -> Optional[str]:
        """
        Validate the currency field against the supported currency allowlist.

        Args:
            currency: Value from payment_data.get('currency', 'usd').

        Returns:
            None if valid, error string otherwise.
        """
        if not isinstance(currency, str) or currency.lower() not in _VALID_CURRENCIES:
            return f"Invalid payment data: unsupported currency '{currency}'"
        return None

    # ------------------------------------------------------------------
    # Retry orchestration
    # ------------------------------------------------------------------

    def _execute_with_retry(self, order_id: str, payment_data: dict) -> dict:
        """
        Call the Apple Pay API with exponential back-off on transient errors.

        Makes up to self._max_retries attempts. On each failure the delay
        doubles: base_delay × 2^attempt (1 s, 2 s, 4 s by default).

        Timeout errors are tracked separately and reflected in the final
        error message to aid incident response.

        Args:
            order_id: Used as the idempotency key (order-{order_id}).
            payment_data: Pre-validated payment payload.

        Returns:
            Payment result dict — always contains 'status'.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                result = self._call_apple_pay_api(order_id, payment_data)

                if result.get("status") == "success":
                    logger.info(
                        "Apple Pay payment succeeded: order_id=%s payment_id=%s",
                        order_id,
                        result.get("payment_id"),
                    )
                    return result

                # Non-retryable API-level error (e.g. card declined, bad token).
                # Return immediately — retrying won't help.
                return result

            except requests.exceptions.Timeout as exc:
                last_exception = exc
                delay = self._base_delay * (2 ** attempt)
                logger.warning(
                    "Apple Pay API timeout on attempt %d/%d for order_id=%s, "
                    "retrying in %.1fs",
                    attempt + 1, self._max_retries, order_id, delay,
                )
                time.sleep(delay)

            except requests.exceptions.RequestException as exc:
                last_exception = exc
                delay = self._base_delay * (2 ** attempt)
                logger.warning(
                    "Apple Pay API error on attempt %d/%d for order_id=%s "
                    "(%s), retrying in %.1fs",
                    attempt + 1, self._max_retries, order_id, type(exc).__name__, delay,
                )
                time.sleep(delay)

        if isinstance(last_exception, requests.exceptions.Timeout):
            return {
                "status": "error",
                "message": "Payment processing failed: connection timeout after retries",
            }
        return {"status": "error", "message": "Payment processing failed after retries"}

    # ------------------------------------------------------------------
    # HTTP layer
    # ------------------------------------------------------------------

    def _call_apple_pay_api(self, order_id: str, payment_data: dict) -> dict:
        """
        Execute a single charge request against the Apple Pay API.

        The Idempotency-Key header is set to 'order-{order_id}' so that
        retrying the same order never creates a duplicate charge.

        Args:
            order_id: Order identifier, used as the idempotency key.
            payment_data: Validated payment payload.

        Returns:
            Payment result dict with 'status' key.

        Raises:
            requests.exceptions.RequestException: Propagated to the retry
                loop in _execute_with_retry.
        """
        headers = self._build_request_headers(idempotency_key=f"order-{order_id}")
        body = {
            "order_id": order_id,
            "apple_pay_token": payment_data["apple_pay_token"],
            "amount": payment_data["amount"],
            "currency": payment_data.get("currency", "usd"),
        }

        response = requests.post(
            self._api_url,
            json=body,
            headers=headers,
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            payload = response.json()
            return {
                "status": "success",
                "payment_id": payload["id"],
                "timestamp": payload["created"],
            }

        error_message = _extract_api_error(response)
        return {"status": "error", "message": error_message}

    def _build_request_headers(self, *, idempotency_key: Optional[str] = None) -> dict:
        """
        Build HTTP headers for Apple Pay API requests.

        The Authorization value is never logged; callers must not log
        the returned dict.

        Args:
            idempotency_key: When provided, added as the Idempotency-Key header.

        Returns:
            Dict of HTTP request headers.
        """
        headers: dict = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_api_url(url: str) -> None:
        """
        Raise ValueError if the configured API URL does not use HTTPS.

        Args:
            url: URL string to validate.

        Raises:
            ValueError: When the URL scheme is not 'https://'.
        """
        if not url.startswith("https://"):
            raise ValueError(
                f"APPLE_PAY_API_URL must use HTTPS to protect credentials in transit. "
                f"Got: '{url}'"
            )


class ApplePayPaymentMethod(ApplePayProcessor):
    """
    Backward-compatible Apple Pay payment method name.

    Args:
        None.

    Returns:
        ApplePayPaymentMethod instance using the ApplePayProcessor implementation.
    """


# ---------------------------------------------------------------------------
# Module-level helper (not a method — keeps classes lean)
# ---------------------------------------------------------------------------

def _extract_api_error(response: requests.Response) -> str:
    """
    Extract a human-readable error message from an Apple Pay API error response.

    Args:
        response: The failed HTTP response object.

    Returns:
        Error message string, falling back to 'Unknown error' if the
        response body cannot be parsed.
    """
    try:
        return response.json().get("error", {}).get("message", "Unknown error")
    except ValueError:
        return f"Unknown error (HTTP {response.status_code})"
