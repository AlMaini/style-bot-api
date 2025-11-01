from _typeshed import SupportsRichComparison
import os
from supabase import create_client, Client
from dotenv import load_dotenv

_ = load_dotenv()


def get_supabase_client() -> Client:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )

    client = create_client(supabase_url, supabase_key)
    return client
