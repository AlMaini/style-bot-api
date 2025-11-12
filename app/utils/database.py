from uuid import UUID

import supabase

from .clients import get_supabase_client

supabase_client: supabase.Client = get_supabase_client()


async def get_profile(user_id: UUID):
    """Fetch user profile from Supabase."""
    try:
        response = (
            supabase_client.table("profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        print(response.data)

        return response.data[0]
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return None


async def update_stripe_id(user_id: UUID, stripe_customer_id: str):
    """Update user profile with the stripe_customer_id in Supabase."""
    try:
        response = (
            supabase_client.table("profiles")
            .update({"stripe_customer_id": stripe_customer_id})
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error updating profile: {e}")
        return None
