import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Cache connection params but create fresh clients to avoid concurrency issues
_url: str = ""
_key: str = ""
_initialized: bool = False


def _init():
    global _url, _key, _initialized
    if _initialized:
        return
    _url = os.getenv("SUPABASE_URL", "").strip()
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    anon_key = os.getenv("SUPABASE_KEY", "").strip()
    _key = service_key or anon_key
    if not _url:
        raise RuntimeError("SUPABASE_URL is not set. Check your .env file.")
    if not _key:
        raise RuntimeError("Neither SUPABASE_SERVICE_KEY nor SUPABASE_KEY is set.")
    using = "service_role" if service_key else "anon"
    print(f"[Supabase] Configured: {_url} using {using} key")
    _initialized = True


def get_supabase() -> Client:
    """Return a fresh Supabase client per request (thread-safe)."""
    _init()
    return create_client(_url, _key)
