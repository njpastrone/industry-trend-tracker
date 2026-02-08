import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import db
import etl
from config import SIGNAL_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Industry Intelligence Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Shared helper ---

def _build_sectors_with_metrics(days: int) -> list[dict]:
    """Build enriched sector list with financials, signal counts, and narrative summary."""
    sectors = db.get_sectors()
    all_financials = {f["sector_id"]: f for f in db.get_all_financials()}
    all_narratives = db.get_all_latest_narratives()

    result = []
    for s in sectors:
        sid = s["id"]
        fin = all_financials.get(sid)
        nar = all_narratives.get(sid)

        signals = db.get_sector_signals(sid, days=days)
        signal_count = len([sig for sig in signals if sig.get("signal_type") != "neutral"])

        result.append({
            "id": sid,
            "name": s["name"],
            "gics_code": s["gics_code"],
            "etf_ticker": s["etf_ticker"],
            "financials": fin,
            "signal_count": signal_count,
            "narrative": {
                "summary_short": nar.get("summary_short"),
                "sentiment": nar.get("sentiment"),
                "key_themes": nar.get("key_themes"),
            } if nar else None,
        })
    return result


# --- Endpoints ---

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/init")
def init(days: int = Query(default=7, ge=1)):
    """Combined dashboard load — one request, not N+1."""
    sectors = _build_sectors_with_metrics(days)

    # Derive last_pipeline_run from most recent narrative created_at
    all_narratives = db.get_all_latest_narratives()
    last_run = None
    for nar in all_narratives.values():
        created = nar.get("created_at")
        if created and (last_run is None or created > last_run):
            last_run = created

    return {"sectors": sectors, "last_pipeline_run": last_run}


@app.get("/api/sectors")
def get_sectors(days: int = Query(default=7, ge=1)):
    """All sectors with financials, signal counts, and narrative summary."""
    return _build_sectors_with_metrics(days)


@app.get("/api/sectors/{sector_id}")
def get_sector_detail(
    sector_id: str,
    days: int = Query(default=7, ge=1),
    signal_type: Optional[str] = Query(default=None),
    sentiment: Optional[str] = Query(default=None),
):
    """Full sector detail with signals, narrative, and financials."""
    try:
        sector = db.get_sector(sector_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Sector not found")
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    financials = db.get_sector_financials(sector_id)
    narrative = db.get_latest_narrative(sector_id)

    # Get ALL signals (unfiltered by type) for counts, then filtered for response
    all_signals = db.get_sector_signals(sector_id, days=days)
    signal_counts_by_type = {}
    for sig in all_signals:
        st = sig.get("signal_type", "neutral")
        signal_counts_by_type[st] = signal_counts_by_type.get(st, 0) + 1

    # Filtered signals for the response
    if signal_type or sentiment:
        filtered_signals = db.get_sector_signals(
            sector_id, days=days, signal_type=signal_type, sentiment=sentiment
        )
    else:
        filtered_signals = all_signals

    return {
        "sector": sector,
        "financials": financials,
        "narrative": narrative,
        "signals": filtered_signals,
        "signal_counts_by_type": signal_counts_by_type,
    }


@app.get("/api/signals")
def get_signals(
    sector_id: Optional[str] = Query(default=None),
    signal_type: Optional[str] = Query(default=None),
    sentiment: Optional[str] = Query(default=None),
    min_relevance: float = Query(default=0.5, ge=0.0, le=1.0),
    days: int = Query(default=7, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Cross-sector signal search with filters."""
    return db.get_all_signals(
        days=days,
        sector_id=sector_id,
        signal_type=signal_type,
        sentiment=sentiment,
        min_relevance=min_relevance,
        limit=limit,
    )


@app.post("/api/pipeline/run")
def pipeline_run():
    result = etl.run_pipeline()
    return result


@app.post("/api/pipeline/financials")
def pipeline_financials():
    """Refresh ETF data only."""
    sectors = db.get_sectors()
    count = etl.refresh_sector_financials(sectors)
    return {"financials_updated": count}


@app.get("/api/config/signal-types")
def get_signal_types():
    """Signal type metadata."""
    return SIGNAL_TYPES
