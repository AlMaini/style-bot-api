import os
from google import genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
_ = load_dotenv()

editing_model = "gemini-2.5-flash-image-preview"
analysis_model = "gemini-1.5-flash"


def get_gemini_client() -> genai.Client:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def get_supabase_client() -> Client:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return client
