"""
Service de facturation Stripe.
"""

from typing import Optional

import stripe

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key


async def create_checkout_session(
    amount_cents: int,
    currency: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """Crée une session Checkout Stripe pour un paiement d'agent."""
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": "AgentForge Run"},
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
        metadata=metadata or {},
    )
    return {
        "checkout_url": checkout_session.url,
        "session_id": checkout_session.id,
    }


def calculate_marketplace_split(amount_cents: int, fee_pct: float = None) -> dict:
    """Répartit un paiement entre l'auteur de l'agent et la plateforme."""
    fee_pct = fee_pct if fee_pct is not None else settings.marketplace_fee_pct
    fee_cents = int(amount_cents * fee_pct / 100)
    author_cents = amount_cents - fee_cents
    return {
        "amount_cents": amount_cents,
        "fee_cents": fee_cents,
        "author_cents": author_cents,
        "fee_pct": fee_pct,
    }


def verify_webhook(payload: bytes, signature: str) -> Optional[dict]:
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
        return event.to_dict()
    except (ValueError, stripe.error.SignatureVerificationError):
        return None