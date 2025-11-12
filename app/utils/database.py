from uuid import UUID

import supabase

from .clients import get_supabase_client

supabase_client: supabase.Client = get_supabase_client()


async def get_profile_from_db(user_id: UUID):
    """Fetch user profile from Supabase."""
    try:
        response = (
            supabase_client.table("profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
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


async def has_available_usage(user_id: UUID) -> bool:
    """Check if the user has available usage left."""
    try:
        profile = await get_profile_from_db(user_id)
        if profile:
            return profile["image_usage"] <= profile["image_limit"]

        else:
            raise ValueError("Profile not found")
    except Exception as e:
        print(f"Error checking available usage: {e}")
        return False


async def increment_image_usage(user_id: UUID):
    """Increment the image usage count for the user."""
    try:
        profile = await get_profile_from_db(user_id)
        if profile:
            new_usage = profile["image_usage"] + 1
            response = (
                supabase_client.table("profiles")
                .update({"image_usage": new_usage})
                .eq("user_id", str(user_id))
                .execute()
            )
            return response.data
        else:
            raise ValueError("Profile not found")
    except Exception as e:
        print(f"Error incrementing image usage: {e}")
        return None
