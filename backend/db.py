from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# --- Singleton Supabase Client ---
_supabase: Client | None = None


def get_client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


# --- Sectors ---

def get_sectors() -> list[dict]:
    res = get_client().table("sectors").select("*").execute()
    return res.data


def get_sector(sector_id: str) -> dict | None:
    res = get_client().table("sectors").select("*").eq("id", sector_id).execute()
    return res.data[0] if res.data else None


# --- Sector Feeds ---

def get_sector_feeds(sector_id: str) -> list[dict]:
    res = (
        get_client()
        .table("sector_feeds")
        .select("*")
        .eq("sector_id", sector_id)
        .eq("active", True)
        .execute()
    )
    return res.data


def get_all_active_feeds() -> list[dict]:
    res = (
        get_client()
        .table("sector_feeds")
        .select("*, sectors(name, etf_ticker)")
        .eq("active", True)
        .execute()
    )
    return res.data


# --- Sector Articles ---

def get_existing_urls(urls: list[str]) -> set[str]:
    """Batch check which URLs already exist. Returns set of existing URLs."""
    if not urls:
        return set()
    res = (
        get_client()
        .table("sector_articles")
        .select("url")
        .in_("url", urls)
        .execute()
    )
    return {row["url"] for row in res.data}


def insert_articles(articles: list[dict]) -> list[dict]:
    """Insert articles, skipping duplicates via ON CONFLICT."""
    if not articles:
        return []
    res = (
        get_client()
        .table("sector_articles")
        .upsert(articles, on_conflict="url", ignore_duplicates=True)
        .execute()
    )
    return res.data


def get_sector_articles(sector_id: str, days: int = 7) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    res = (
        get_client()
        .table("sector_articles")
        .select("*")
        .eq("sector_id", sector_id)
        .gte("fetched_at", since)
        .order("published_at", desc=True)
        .execute()
    )
    return res.data


# --- Sector Signals ---

def insert_signals(signals: list[dict]) -> list[dict]:
    if not signals:
        return []
    res = get_client().table("sector_signals").insert(signals).execute()
    return res.data


def get_sector_signals(
    sector_id: str,
    days: int = 7,
    signal_type: str | None = None,
    sentiment: str | None = None,
    min_relevance: float = 0.0,
) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    query = (
        get_client()
        .table("sector_signals")
        .select("*, sector_articles(title, url, source, published_at)")
        .eq("sector_id", sector_id)
        .gte("created_at", since)
        .gte("ir_relevance", min_relevance)
        .order("created_at", desc=True)
    )
    if signal_type:
        query = query.eq("signal_type", signal_type)
    if sentiment:
        query = query.eq("sentiment", sentiment)
    return query.execute().data


def get_all_signals(
    days: int = 7,
    sector_id: str | None = None,
    signal_type: str | None = None,
    sentiment: str | None = None,
    min_relevance: float = 0.5,
    limit: int = 50,
) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    query = (
        get_client()
        .table("sector_signals")
        .select("*, sector_articles(title, url, source, published_at)")
        .gte("created_at", since)
        .gte("ir_relevance", min_relevance)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if sector_id:
        query = query.eq("sector_id", sector_id)
    if signal_type:
        query = query.eq("signal_type", signal_type)
    if sentiment:
        query = query.eq("sentiment", sentiment)
    return query.execute().data


# --- Sector Financials ---

def upsert_sector_financials(sector_id: str, financials: dict) -> dict:
    data = {"sector_id": sector_id, "updated_at": datetime.now(timezone.utc).isoformat(), **financials}
    res = (
        get_client()
        .table("sector_financials")
        .upsert(data, on_conflict="sector_id")
        .execute()
    )
    return res.data[0] if res.data else {}


def get_all_financials() -> list[dict]:
    res = get_client().table("sector_financials").select("*").execute()
    return res.data


def get_sector_financials(sector_id: str) -> dict | None:
    res = (
        get_client()
        .table("sector_financials")
        .select("*")
        .eq("sector_id", sector_id)
        .execute()
    )
    return res.data[0] if res.data else None


# --- Sector Narratives ---

def insert_narrative(narrative: dict) -> dict:
    res = get_client().table("sector_narratives").insert(narrative).execute()
    return res.data[0] if res.data else {}


def get_latest_narrative(sector_id: str) -> dict | None:
    res = (
        get_client()
        .table("sector_narratives")
        .select("*")
        .eq("sector_id", sector_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def clear_pipeline_data() -> dict:
    """Delete all signals, articles, and narratives for a fresh pipeline run."""
    client = get_client()
    # Use gte with nil UUID to match all rows (PostgREST requires a filter for DELETE)
    nil_uuid = "00000000-0000-0000-0000-000000000000"
    sig = client.table("sector_signals").delete().gte("id", nil_uuid).execute()
    art = client.table("sector_articles").delete().gte("id", nil_uuid).execute()
    nar = client.table("sector_narratives").delete().gte("id", nil_uuid).execute()
    return {
        "signals_deleted": len(sig.data),
        "articles_deleted": len(art.data),
        "narratives_deleted": len(nar.data),
    }


def get_all_latest_narratives() -> dict[str, dict]:
    """Get the latest narrative for each sector. Returns dict keyed by sector_id."""
    res = (
        get_client()
        .table("sector_narratives")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    # Python-side: keep only the latest per sector
    latest: dict[str, dict] = {}
    for row in res.data:
        sid = row["sector_id"]
        if sid not in latest:
            latest[sid] = row
    return latest
