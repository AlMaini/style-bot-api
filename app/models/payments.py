from pydantic import BaseModel


class CheckoutSessionRequest(BaseModel):
    price_id: str
