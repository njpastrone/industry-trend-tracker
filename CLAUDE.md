# Industry Intelligence Tracker

Macro sector trend dashboard for IR professionals. Companion app to the Sales Intelligence Tracker (company-level outreach tool). Different unit of analysis (GICS sectors vs individual companies), different data sources, different UI.

## What This App Does

Tracks the 11 GICS sectors with AI-classified news signals, ETF performance data, and AI-generated sector narratives. Users see which sectors are under pressure, drill into the signals driving the narrative, and prepare for investor questions before they're asked.

Two pages: Sector Dashboard (grid of 11 sector cards) and Sector Detail (signals feed + narrative + financials for one sector).

## Tech Stack

- **Frontend**: React 19 + Vite 6 + TypeScript 5 + Tailwind CSS 4 + TanStack Query 5 + React Router 7
- **Backend**: FastAPI (Python) with uvicorn
- **Database**: Supabase (PostgreSQL, free tier, separate project from sales tracker)
- **AI**: Claude Haiku via Anthropic SDK (batch classification + narrative generation)
- **Financial data**: yfinance (sector ETFs + SPY for relative performance)
- **Deployment**: Render (static site for frontend, web service for backend)

## Project Structure

```
backend/
  main.py              # FastAPI routes + CORS
  db.py                # Singleton Supabase client + CRUD helpers
  config.py            # Constants, signal types, prompt templates
  etl.py               # Pipeline: fetch -> classify -> narratives (Phase 2)
  requirements.txt     # Python dependencies
  Dockerfile
frontend/              # (Phase 4-5)
  src/
    App.tsx             # Router setup (/ and /sector/:sectorId)
    pages/
      Dashboard.tsx     # Sector grid view
      SectorDetail.tsx  # Single sector drill-down
    components/
      SectorCard.tsx, SectorGrid.tsx, SignalFeed.tsx, SignalCard.tsx,
      NarrativeBlock.tsx, SectorHeader.tsx, SignalTypeTabs.tsx, Filters.tsx
    api/client.ts       # Axios instance + typed API functions
    types/index.ts      # Shared TypeScript types
  package.json
  vite.config.ts
schema.sql              # Database schema (6 tables) — run in Supabase SQL Editor
seed.sql                # Sector + feed seed data — run in Supabase SQL Editor
```

## Data Model (6 tables)

- `sectors` - 11 GICS sectors (seeded, fixed)
- `sector_feeds` - RSS feed configs per sector (google_news, einnews, federal_register)
- `sector_articles` - Fetched articles, deduplicated by URL (UNIQUE constraint)
- `sector_signals` - AI-classified signals (signal_type, sentiment, ir_relevance 0-1)
- `sector_financials` - ETF performance (7D, 30D, YTD, vs SPY), one row per sector
- `sector_narratives` - AI-generated summaries (short + full + key_themes + sentiment)
- `sector_regulatory` - Federal Register entries (V2, not MVP)

## API Endpoints

- `GET /api/init` - Combined dashboard load (all sectors + financials + narratives). One call, not N+1.
- `GET /api/sectors` - All sectors with financials and signal counts. Query: `days` (default 7).
- `GET /api/sectors/{sector_id}` - Full detail. Query: `days`, `signal_type`, `sentiment`.
- `GET /api/signals` - Cross-sector signal search. Query: `sector_id`, `signal_type`, `sentiment`, `min_relevance`, `days`, `limit`.
- `POST /api/pipeline/run` - Run full pipeline (fetch + classify + financials + narratives).
- `POST /api/pipeline/financials` - Refresh ETF data only.
- `GET /api/config/signal-types` - Signal type metadata.
- `GET /api/health` - Health check.

## Pipeline (etl.py)

1. Fetch sector news from Google News RSS (2-3 queries per sector, 15-20 articles per query)
2. Dedup against existing URLs in DB (`get_existing_urls()` batch check)
3. Batch classify with Claude Haiku (8 articles per API call, `headline_index` mapping)
4. Fetch ETF financials via `yf.download()` (all 12 tickers in one call: 11 ETFs + SPY)
5. Generate sector narratives (one Claude call per sector using top signals)

Parallel processing: `ThreadPoolExecutor(max_workers=5)` for sector processing. ~55 API calls per run, ~$0.42/month.

## Signal Types

`regulatory`, `analyst_sentiment`, `earnings_trend`, `m_and_a`, `competitive`, `macro_economic`, `esg`, `neutral`

## Critical Lessons from Sales Tracker (MUST follow)

1. **Combined /api/init endpoint** - Dashboard loads everything in one request. No N+1 queries.
2. **Singleton Supabase client** - Initialize once, reuse everywhere. Don't create per-request.
3. **Python-side aggregation** - Supabase PostgREST doesn't support GROUP BY well. Aggregate in Python. At this scale (11 sectors, few hundred signals) it's trivial.
4. **Batch classification from day one** - Group 8 articles per Claude API call. Use `headline_index` mapping. Fallback to individual calls if batch fails.
5. **Code-level keyword overrides for AI misclassification** - Haiku ignores prompt-level exclusion instructions when signal words are strong. Build `_is_single_company_news()` filter from day one that forces obviously company-specific headlines to neutral. Do NOT rely on prompts alone for hard classification boundaries.
6. **Separate classification and narrative generation** - Classify first (cheap batch calls), then generate narratives (separate step). Don't combine.
7. **URL deduplication is critical** - Google News returns duplicates across queries. Batch check existing URLs before insert. Especially important since sector queries overlap.
8. **Fallback strategy** - Batch to individual classification on API failure. Batch to individual DB inserts on failure.
9. **refetchQueries vs invalidateQueries** - Use `refetchQueries` when you need data loaded before showing success (e.g., after pipeline run). `invalidateQueries` just marks stale.
10. **TanStack Query patterns** - `queryKey` arrays with parameters (`['initData', timeWindow]`), `staleTime: 5min`.
11. **localStorage for preferences** - Time window, filter state, last viewed sector. No auth.
12. **Keep UI simple** - Blue/white color scheme. No emojis. Clean sector card grid + detail drill-down. Don't add bells and whistles.
13. **Feed config in database** - Store in `sector_feeds` table, not hardcoded. Add/modify without code changes.
14. **Restart uvicorn for config/etl changes** - Auto-reload doesn't always pick up imported module changes.

## Environment Variables

```
# Backend
SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY

# Frontend
VITE_API_URL
```

## Cost Target

Under $5/month total. Claude API ~$0.42/month. Supabase free tier. Render free/starter tier.

## Build Plan

### Methodology

Each phase follows a strict cycle:
1. **Gain context** — Read `CLAUDE.md` + relevant planning docs
2. **Plan** — Enter plan mode, explore what exists, design the phase
3. **Build** — Implement and test
4. **Persist** — Update `CLAUDE.md` with what's done, what's next, any gotchas discovered

If context runs low mid-phase, stop, persist progress, and pick up next session.

### Phases

| Phase | Scope | Key Files | Status |
|-------|-------|-----------|--------|
| 1 | Database + backend skeleton | `schema.sql`, `seed.sql`, `db.py`, `config.py`, `backend/main.py`, `requirements.txt` | DONE |
| 2 | ETL pipeline | `etl.py` — RSS fetch, URL dedup, batch classify, financials, narratives | DONE |
| 3 | API endpoints | All GET routes + pipeline trigger wired to real data | DONE |
| 4 | Frontend — Dashboard | Vite/React/TS setup, router, Dashboard page with sector grid | DONE |
| 5 | Frontend — Sector Detail | Detail page, signal feed, narrative block, filters | DONE |

### Phase Details

**Phase 1: Database + Backend Skeleton**
- Write `schema.sql` (5 MVP tables: sectors, sector_feeds, sector_articles, sector_signals, sector_financials, sector_narratives)
- Write `seed.sql` (11 GICS sectors + initial Google News feed configs per sector)
- `config.py` — constants, signal types, prompt templates
- `db.py` — singleton Supabase client, CRUD helpers for each table
- `backend/main.py` — FastAPI app with CORS, `/api/health` endpoint
- `backend/requirements.txt` — fastapi, uvicorn, supabase, anthropic, httpx, yfinance
- Run schema + seed in Supabase, verify backend starts and connects

**Phase 2: ETL Pipeline**
- RSS fetching from Google News (per sector, per feed config from DB)
- URL deduplication (batch check existing URLs before insert)
- Batch classification with Claude Haiku (8 per call, `headline_index` mapping)
- Code-level `_is_single_company_news()` filter (from day one)
- `yf.download()` for all 12 tickers (11 ETFs + SPY), compute relative performance
- Narrative generation (one Claude call per sector from top signals)
- `ThreadPoolExecutor(max_workers=5)` for parallel sector processing
- Fallback: batch → individual on API failure
- Wire up `POST /api/pipeline/run` and test end-to-end

**Phase 3: API Endpoints**
- `GET /api/init` — combined dashboard load (sectors + financials + narratives + signal counts)
- `GET /api/sectors` — all sectors with metrics
- `GET /api/sectors/{sector_id}` — full detail with signals, narrative, financials
- `GET /api/signals` — cross-sector search with filters
- `POST /api/pipeline/financials` — refresh ETF data only
- `GET /api/config/signal-types` — signal type metadata
- Python-side aggregation for signal counts by type
- Test all endpoints with real pipeline data

**Phase 4: Frontend — Dashboard**
- Vite + React + TypeScript + Tailwind project setup
- React Router (/ and /sector/:sectorId)
- TanStack Query setup with axios client
- TypeScript types matching API response shapes
- Dashboard page: sector grid (3 cols desktop, 2 tablet, 1 mobile)
- SectorCard component (name, ETF ticker, 7D performance, signal count, sentiment dot, AI summary)
- Filters bar (time window dropdown, signal type dropdown)
- Header with last pipeline run + refresh button
- Loading states

**Phase 5: Frontend — Sector Detail**
- SectorDetail page with back navigation
- SectorHeader (performance stats: 7D, 30D, YTD, vs SPY)
- NarrativeBlock (key theme tags + full AI narrative)
- SignalTypeTabs (counts per type, click to filter)
- SignalFeed + SignalCard (headline link, source, date, type badge, sentiment, AI summary)
- Signal type filtering
- Responsive layout

## Scope (MVP vs Later)

**MVP**: Sector dashboard, sector detail, signal classification, ETF performance, AI narratives, pipeline trigger.
**V2**: Federal Register integration, trend lines, alerts, sector comparison, EINNews feeds.
**V3**: Deep-link to Sales Intelligence Tracker, macro-economic indicator overlays.
**Out of scope**: Individual company tracking, real-time streaming, user auth, paid data sources, mobile app, email/Slack notifications.
