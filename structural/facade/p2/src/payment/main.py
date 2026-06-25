from __future__ import annotations

import os

from flask import Flask, Response, jsonify, request

from src.payment.application.facade import PaymentFacade
from src.payment.domain.entities import CreditCard, Customer
from src.payment.domain.exceptions import (
    CardDeclinedError,
    InvalidCardError,
    PaymentProcessingError,
    TransactionNotFoundError,
)
from src.payment.infrastructure.card_validator import LuhnCardValidator
from src.payment.infrastructure.database import create_tables, get_session, init_engine
from src.payment.infrastructure.receipt_service import EmailReceiptService
from src.payment.infrastructure.stripe_gateway import (
    MockStripeGateway,
    StripePaymentGateway,
)
from src.payment.infrastructure.transaction_repository import MySQLTransactionRepository


def create_app() -> Flask:
    """Application factory — wires the Flask app and initializes the database."""
    app = Flask(__name__)

    database_url = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://app:secret@db:3306/appdb"
    )
    init_engine(database_url)
    create_tables(database_url)

    register_routes(app)
    return app


def build_facade() -> PaymentFacade:
    """Composition root — assembles the Facade with all subsystem dependencies."""
    session = get_session()
    use_mock_gateway = os.environ.get("USE_MOCK_STRIPE", "true").lower() == "true"
    gateway = MockStripeGateway() if use_mock_gateway else StripePaymentGateway()

    return PaymentFacade(
        validator=LuhnCardValidator(),
        gateway=gateway,
        repository=MySQLTransactionRepository(session),
        receipts=EmailReceiptService(),
    )


def register_routes(app: Flask) -> None:
    @app.post("/payments")
    def charge_payment() -> tuple[Response, int]:
        """Process a payment. The Flask route never touches Stripe or MySQL
        directly — it only talks to PaymentFacade."""
        payload = request.get_json(force=True)
        customer = Customer(
            id=payload["customer_id"],
            name=payload["customer_name"],
            email=payload["customer_email"],
        )
        card = CreditCard(
            number=payload["card_number"],
            exp_month=payload["card_exp_month"],
            exp_year=payload["card_exp_year"],
            cvc=payload["card_cvc"],
            holder_name=payload["customer_name"],
        )
        amount_cents = payload["amount_cents"]
        currency = payload.get("currency", "usd")

        facade = build_facade()
        try:
            result = facade.process_payment(customer, card, amount_cents, currency)
        except InvalidCardError as exc:
            return jsonify({"error": str(exc)}), 400
        except CardDeclinedError as exc:
            return (
                jsonify({"error": str(exc), "transaction_id": exc.transaction_id}),
                402,
            )
        except PaymentProcessingError as exc:
            return jsonify({"error": str(exc)}), 500

        return (
            jsonify(
                {
                    "transaction_id": result.transaction_id,
                    "status": result.status.value,
                    "amount_cents": result.amount_cents,
                    "currency": result.currency,
                    "receipt_id": result.receipt_id,
                    "message": result.message,
                }
            ),
            201,
        )

    @app.get("/payments/<transaction_id>")
    def get_payment(transaction_id: str) -> tuple[Response, int]:
        facade = build_facade()
        try:
            transaction = facade.get_transaction(transaction_id)
        except TransactionNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404

        return (
            jsonify(
                {
                    "transaction_id": transaction.id,
                    "customer_id": transaction.customer_id,
                    "amount_cents": transaction.amount_cents,
                    "currency": transaction.currency,
                    "status": transaction.status.value,
                    "charge_id": transaction.charge_id,
                    "failure_reason": transaction.failure_reason,
                }
            ),
            200,
        )

    @app.post("/payments/<transaction_id>/refund")
    def refund_payment(transaction_id: str) -> tuple[Response, int]:
        facade = build_facade()
        try:
            result = facade.refund_payment(transaction_id)
        except TransactionNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PaymentProcessingError as exc:
            return jsonify({"error": str(exc)}), 409

        return (
            jsonify(
                {
                    "transaction_id": result.transaction_id,
                    "status": result.status.value,
                    "message": result.message,
                }
            ),
            200,
        )

    @app.get("/health")
    def health_check() -> tuple[Response, int]:
        return jsonify({"status": "ok"}), 200


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
