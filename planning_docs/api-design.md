# API Design: Industry Intelligence Tracker

## Base URL

Same pattern as sales tracker: FastAPI backend, `/api/` prefix.

## Endpoints

### Sectors

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sectors` | GET | List all sectors with latest financials and signal counts |
| `/api/sectors/{sector_id}` | GET | Sector detail: signals, narrative, financials |

#### GET /api/sectors

Returns the dashboard overview — all 11 sectors with key metrics.

Query params:
- `days` (int, default 7) — signal time window

Response:
```json
[
  {
    "id": "uuid",
    "name": "Information Technology",
    "gics_code": "45",
    "etf_ticker": "XLK",
    "financials": {
      "etf_price": 215.40,
      "price_change_7d": -0.032,
      "price_change_30d": 0.018,
      "price_change_ytd": 0.045,
      "vs_spy_7d": -0.015,
      "vs_spy_30d": 0.003
    },
    "signal_count": 12,
    "narrative": {
      "summary_short": "Tech sector facing regulatory headwinds as AI governance proposals accelerate.",
      "sentiment": "negative",
      "key_themes": ["AI regulation", "semiconductor export controls"]
    }
  }
]
```

#### GET /api/sectors/{sector_id}

Full detail for a single sector.

Query params:
- `days` (int, default 7) — signal time window
- `signal_type` (string, optional) — filter by signal type
- `sentiment` (string, optional) — filter by sentiment

Response:
```json
{
  "sector": {
    "id": "uuid",
    "name": "Information Technology",
    "gics_code": "45",
    "etf_ticker": "XLK"
  },
  "financials": {
    "etf_price": 215.40,
    "price_change_7d": -0.032,
    "price_change_30d": 0.018,
    "price_change_ytd": 0.045,
    "vs_spy_7d": -0.015,
    "vs_spy_30d": 0.003
  },
  "narrative": {
    "summary_short": "...",
    "summary_full": "2-3 paragraphs...",
    "key_themes": ["AI regulation", "semiconductor export controls"],
    "sentiment": "negative",
    "created_at": "2026-02-07T..."
  },
  "signals": [
    {
      "id": "uuid",
      "summary": "EU AI Act enforcement begins, requiring compliance...",
      "signal_type": "regulatory",
      "sentiment": "negative",
      "ir_relevance": 0.85,
      "article": {
        "title": "EU AI Act Takes Effect...",
        "url": "https://...",
        "source": "Reuters",
        "published_at": "2026-02-06T..."
      },
      "created_at": "2026-02-07T..."
    }
  ],
  "signal_counts_by_type": {
    "regulatory": 4,
    "analyst_sentiment": 3,
    "earnings_trend": 2,
    "m_and_a": 1,
    "competitive": 1,
    "macro_economic": 1,
    "neutral": 0
  }
}
```

### Init (combined load)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/init` | GET | Combined initial load for dashboard |

#### GET /api/init

Returns everything needed for the dashboard in one call (same optimization pattern as sales tracker).

Query params:
- `days` (int, default 7)

Response:
```json
{
  "sectors": [/* same as GET /api/sectors */],
  "last_pipeline_run": "2026-02-07T06:00:00Z"
}
```

### Signals

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signals` | GET | Query signals across all sectors |

#### GET /api/signals

Cross-sector signal search.

Query params:
- `sector_id` (string, optional)
- `signal_type` (string, optional)
- `sentiment` (string, optional)
- `min_relevance` (float, default 0.5)
- `days` (int, default 7)
- `limit` (int, default 50)

Response: Array of signal objects (same shape as in sector detail).

### Pipeline

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pipeline/run` | POST | Run full pipeline (news + classify + financials + narratives) |
| `/api/pipeline/financials` | POST | Refresh sector ETF data only |

#### POST /api/pipeline/run

Response:
```json
{
  "sectors_processed": 11,
  "articles_fetched": 287,
  "articles_new": 43,
  "signals_created": 38,
  "narratives_generated": 11,
  "errors": 0
}
```

### Config

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config/signal-types` | GET | Available signal types with descriptions |
| `/api/health` | GET | Health check |

## Design Decisions

### Why no CRUD for sectors?

Sectors are the 11 GICS sectors — they're seeded data, not user-managed. Unlike the sales tracker where users add companies to a watchlist, here the "watchlist" is fixed. This simplifies the app significantly.

### Why no outreach tracking?

This app is for monitoring and preparation, not sales execution. There's no "contact" or "snooze" action for a sector. If a user wants to act on a trend, they switch to the Sales Intelligence Tracker.

### Why combined /api/init?

Same lesson from the sales tracker: initial page load should be one request, not N+1 queries. The dashboard needs all 11 sectors with financials and narratives — that's one combined endpoint.

### Query param patterns

Following the same convention as the sales tracker:
- `days` for time window filtering
- Optional filters as query params (not path params)
- Sensible defaults so the frontend can call endpoints with minimal params
