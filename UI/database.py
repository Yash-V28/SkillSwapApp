import os

from dotenv import load_dotenv
from supabase import (
    AsyncClient,
    Client,
    acreate_client,
    create_client,
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError(
        "SUPABASE_URL or SUPABASE_ANON_KEY is missing from .env"
    )


def create_supabase_client() -> Client:
    """
    Normal synchronous client used by main.py for:
    login, database queries, inserts and updates.
    """
    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
    )


async def create_realtime_client() -> AsyncClient:
    """
    Asynchronous client used by friends_chat.py for Realtime.
    """
    return await acreate_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
    )