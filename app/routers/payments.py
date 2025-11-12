import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic_core.core_schema import CustomErrorSchema
from utils.auth import get_current_user
from utils.clients import get_supabase_client
from utils.database import get_profile, update_stripe_id

router = APIRouter(prefix="/api/payments")

_ = load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
success_url = f"{FRONTEND_URL}/dashboard"
cancel_url = f"{FRONTEND_URL}/cancel"
return_url = f"{FRONTEND_URL}/dashboard"

stripe.api_key = os.getenv("STRIPE_KEY")


@router.post("/create-checkout-session")
async def create_checkout_session(price_id: str, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")
    try:
        profile = await get_profile(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        customer_id = profile["stripe_customer_id"]
        # Check if user already has a Stripe Customer ID
        if customer_id is None:
            # Create new Stripe customer
            stripe_customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )

            # Save the Stripe Customer ID to your database
            _ = await update_stripe_id(user.id, stripe_customer.id)

            customer_id = stripe_customer.id

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,  # This uses the Stripe Price ID directly
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {"sessionId": checkout_session.id, "url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")

    try:
        profile = await get_profile(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        customer_id = profile["stripe_customer_id"]
        # Check if user already has a Stripe Customer ID
        if customer_id is None:
            # Create new Stripe customer
            stripe_customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )

            # Save the Stripe Customer ID to your database
            _ = await update_stripe_id(user.id, stripe_customer.id)

            customer_id = stripe_customer.id

        portal_session = stripe.billing_portal.Session.create(
            customer=user.id, return_url=return_url
        )

        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
