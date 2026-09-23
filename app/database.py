from typing import Optional

from supabase import Client, create_client

from app.config import settings

supabase: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Lazily create (and cache) the Supabase client.
    Raises a clear RuntimeError if env vars are missing, instead of a
    confusing AttributeError deep inside a query.
    """
    global supabase

    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise RuntimeError(
                "Supabase configuration is missing. Set SUPABASE_URL and SUPABASE_KEY "
                "in your environment (.env file)."
            )
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    return supabase
