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
    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
    )


async def create_realtime_client() -> AsyncClient:
    return await acreate_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
    )