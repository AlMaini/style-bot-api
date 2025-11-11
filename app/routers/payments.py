import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_user

router = APIRouter(prefix="/api/payments")

_ = load_dotenv()
success_url = "http://127.0.0.1:3000/dashboard"
cancel_url = "http://127.0.0.1:3000/cancel"
return_url = "http://127.0.0.1:3000/dashboard"

stripe.api_key = os.getenv("STRIPE_KEY")


@router.post("/create-checkout-session")
async def create_checkout_session(product_id: str, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=user.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": product_id,  # This uses the Stripe Price ID directly
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {"sessionId": checkout_session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.id, return_url=return_url
        )

        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
