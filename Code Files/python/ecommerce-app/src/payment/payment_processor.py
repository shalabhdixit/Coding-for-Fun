"""
Legacy Payment Processor Module
Handles credit card payments via Stripe API
WARNING: This code contains intentional technical debt for demonstration purposes
"""

import requests
import time
import logging
import os

from dotenv import load_dotenv

STRIPE_API_URL = "https://api.stripe.com/v1"
VALID_CURRENCIES = frozenset({"usd", "eur", "gbp", "cad", "aud"})
MIN_CARD_TOKEN_LENGTH = 20
MAX_PAYMENT_AMOUNT = 999999

load_dotenv()

logger = logging.getLogger(__name__)


def _load_stripe_api_key():
    try:
        api_key = os.environ["STRIPE_API_KEY"]
    except KeyError as exc:
        raise ValueError("STRIPE_API_KEY environment variable is required") from exc

    if not _is_valid_stripe_api_key(api_key):
        raise ValueError(
            "STRIPE_API_KEY must be a non-empty Stripe secret key starting with sk_test_ or sk_live_"
        )

    return api_key


def _is_valid_stripe_api_key(api_key):
    return (
        isinstance(api_key, str)
        and api_key.startswith(("sk_test_", "sk_live_"))
        and len(api_key) > len("sk_test_")
    )


class PaymentProcessor:
    """
    Main payment processing class using strategy pattern
    Currently only supports Stripe credit card payments
    """
    
    def __init__(self):
        self.payment_methods = {}
        self.max_retries = 3
        self.base_delay = 1
        
    def register_payment_method(self, method_name, handler):
        """Register a new payment method handler"""
        self.payment_methods[method_name] = handler
        
    def process_payment(self, order_id, payment_method, payment_data):
        """
        Process a payment for the given order
        
        Args:
            order_id: Unique order identifier
            payment_method: Payment method type (e.g., 'credit_card')
            payment_data: Dict containing payment details
            
        Returns:
            Dict with payment result
        """
        if payment_method not in self.payment_methods:
            return {"status": "error", "message": f"Unknown payment method: {payment_method}"}
            
        handler = self.payment_methods[payment_method]
        return handler(order_id, payment_data)


class StripePaymentMethod:
    """Handles Stripe credit card payments"""
    
    def __init__(self):
        self.api_key = _load_stripe_api_key()
        self.api_url = STRIPE_API_URL
        self.base_delay = 1
        
    def process_credit_card_payment(self, order_id, payment_data):
        """
        Process credit card payment via Stripe
        
        Args:
            order_id: Order ID to process payment for
            payment_data: Dict with card_token, amount, currency
            
        Returns:
            Payment result dict
        """
        # Validate payment data
        if not self.validate_payment(payment_data):
            return {"status": "error", "message": "Invalid payment data"}
            
        # Process with retry logic
        for attempt in range(3):
            try:
                result = self._call_stripe_api(order_id, payment_data)
                
                if result.get("status") == "success":
                    logger.info(
                        "Payment successful: order_id=%s payment_id=%s",
                        order_id,
                        result.get("payment_id"),
                    )
                    return result
                    
            except requests.exceptions.RequestException as e:
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Payment attempt {attempt + 1} failed, retrying in {delay}s")
                time.sleep(delay)
                
        return {"status": "error", "message": "Payment processing failed after retries"}
        
    def _call_stripe_api(self, order_id, payment_data):
        """Make API call to Stripe"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "amount": int(payment_data["amount"] * 100),  # Convert to cents
            "currency": payment_data.get("currency", "usd"),
            "source": payment_data["card_token"],
            "description": f"Order {order_id}"
        }
        
        response = requests.post(
            f"{self.api_url}/charges",
            headers=headers,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "payment_id": response.json()["id"],
                "timestamp": response.json()["created"]
            }
        else:
            return {
                "status": "error",
                "message": response.json().get("error", {}).get("message", "Unknown error")
            }
    
    def validate_payment(self, payment_data):
        """
        Validate payment data before processing
        """
        validators = (
            lambda: isinstance(payment_data, dict) and bool(payment_data),
            lambda: self._has_required_payment_fields(payment_data),
            lambda: self._has_valid_amount(payment_data["amount"]),
            lambda: self._has_valid_currency(payment_data.get("currency", "usd")),
            lambda: self._has_valid_card_token(payment_data["card_token"]),
        )
        return all(validate() for validate in validators)

    def _has_required_payment_fields(self, payment_data):
        return "card_token" in payment_data and "amount" in payment_data

    def _has_valid_amount(self, amount):
        return (
            isinstance(amount, (int, float))
            and amount > 0
            and amount <= MAX_PAYMENT_AMOUNT
        )

    def _has_valid_currency(self, currency):
        return isinstance(currency, str) and currency.lower() in VALID_CURRENCIES

    def _has_valid_card_token(self, token):
        return (
            isinstance(token, str)
            and token.startswith("tok_")
            and len(token) >= MIN_CARD_TOKEN_LENGTH
        )


class AbstractPaymentMethod:
    """
    Abstract base class for payment method implementations
    New payment methods should extend this class
    """
    
    def process_payment(self, order_id, payment_data):
        """Process a payment - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process_payment")
        
    def validate_token(self, token):
        """Validate payment token format"""
        raise NotImplementedError("Subclasses must implement validate_token")
        
    def refund_payment(self, payment_id):
        """Refund a previously processed payment"""
        raise NotImplementedError("Subclasses must implement refund_payment")


# Initialize default payment processor
default_processor = PaymentProcessor()
stripe_method = StripePaymentMethod()
default_processor.register_payment_method("credit_card", stripe_method.process_credit_card_payment)
