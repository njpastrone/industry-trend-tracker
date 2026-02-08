# Lessons Learned from the Sales Intelligence Tracker

Things we learned building the sales tracker that should be applied (or avoided) in the industry app.

## Architecture

### Combined /api/init endpoint is essential
The sales tracker originally had separate queries for summary, financials, and outreach. Combining them into `/api/init` cut the initial load from 3 sequential requests to 1. Do the same here — the dashboard needs all 11 sectors with financials and narratives in one call.

### Singleton Supabase client
Initialize the Supabase client once, reuse it. The sales tracker wasted time creating new connections per request before we fixed this.

### Python-side aggregation is fine at this scale
Supabase's free tier PostgREST doesn't support GROUP BY well. The sales tracker aggregates signals by company in Python. Same approach works here — 11 sectors with a few hundred signals total is trivial to aggregate in-memory.

## ETL Pipeline

### Batch classification is a huge win
The single biggest optimization in the sales tracker was grouping 8 articles into one Claude API call. Do this from day one in the industry app. The batch prompt format with `headline_index` mapping works well.

### Parallel processing with ThreadPoolExecutor
Processing 11 sectors in parallel with 5 workers will complete the pipeline much faster than sequential. Same pattern: `ThreadPoolExecutor(max_workers=5)` with `as_completed()`.

### URL deduplication is critical
Google News RSS returns duplicate URLs across different queries. The sales tracker does batch URL checking (`get_existing_urls()`) before inserting. Same approach needed here, especially since sector queries overlap (a major tech company's earnings miss might appear in both "technology sector" and "semiconductor industry" feeds).

### Fallback strategy for API failures
The sales tracker falls back from batch to individual classification if the batch call fails, and from batch to individual DB inserts. Same safety net should exist here.

## AI Classification

### Hard classification boundaries need code, not prompts
The single most important lesson: **Claude Haiku ignores prompt-level exclusion instructions when signal words are strong.** In the sales tracker, Haiku consistently classified EEOC discrimination probes as `governance_issue` despite explicit prompt instructions to classify them as neutral.

We tried:
- XML-structured prompts with `<first_check>` decision gates
- Few-shot examples with exact matching headlines
- Chain-of-thought instructions ("ask yourself: would the IR team brief investors?")
- Strategic end-of-prompt placement

None of it worked. **The solution was a code-level keyword override** (`_is_non_ir_headline()`) that deterministically forces certain headlines to neutral.

**For the industry app**: Expect similar issues. Single-company news will leak into sector feeds, and Haiku may classify them as sector signals despite prompt instructions. Build the code-level filter from day one:

```python
# Headlines that are clearly single-company, not sector-level
def _is_single_company_news(title: str) -> bool:
    """Override sector classification for obviously company-specific headlines."""
    # If headline doesn't contain any sector-level keywords, it's probably
    # about a single company and shouldn't be a sector signal
    ...
```

### Keep prompts compact for Haiku
Haiku works best with structured, concise prompts. XML tags (`<role>`, `<signal_types>`, `<scoring_guide>`) help, but don't overload with examples. 2-3 few-shot examples max in batch prompts to manage token costs.

### Talking point generation works well as a separate step
The sales tracker generates talking points in a separate API call after classification (not combined). This keeps the batch classification prompt simple and cheap. Apply the same pattern: classify first, then generate narratives in a separate step.

## Frontend

### TanStack Query patterns
- `queryKey` arrays with parameters enable automatic refetching when filters change: `['initData', timeWindow]`
- `staleTime: 1000 * 60 * 5` (5 min) prevents unnecessary refetches
- `invalidateQueries` for mutations, `refetchQueries` when you need data immediately after (like the financials refresh bug we fixed)

### localStorage for user preferences
The sales tracker uses localStorage for profile selection. Simple, no auth needed. For the industry app, use it for:
- Last selected time window
- Any saved filter preferences
- Last viewed sector (to return to it on reload)

### Don't over-complicate the UI
The sales tracker went through a UI overhaul to simplify — removing emojis, cleaning up color scheme, improving filter labels. Start simple in the industry app. The sector card grid + detail drill-down is clean and focused. Don't add bells and whistles.

### refetchQueries vs invalidateQueries
If you need data to be loaded before showing a success message (like after a pipeline run), use `refetchQueries` (waits for data) not `invalidateQueries` (marks stale, fetches in background).

## Data Sources

### Google News RSS is reliable but noisy
It works well for the sales tracker and will work for sector-level queries too. But sector queries are broader, so expect more noise. The relevance filtering (both AI-based and code-based) becomes more important.

### yfinance is good enough
It has quirks (earnings date fetching is unreliable, occasional rate limiting), but for daily batch jobs it's fine. For the industry app, fetching all 11 sector ETFs in one `yf.download()` call is efficient.

### Feed configuration should be in the database, not code
The sales tracker hardcodes the Google News RSS URL pattern. For the industry app, store feed configurations in `sector_feeds` table so you can add/modify feeds without code changes.

## Cost

### Claude Haiku is incredibly cheap
The sales tracker processes ~1000 companies for ~$0.50/month after batch optimization. The industry app has only 11 sectors, so costs will be even lower (~$0.42/month). Don't optimize prematurely — the batch approach is already efficient enough.

### Supabase free tier is sufficient
With 11 sectors and a few hundred signals per week, the free tier has more than enough storage and API calls. No need to upgrade.

## Common Pitfalls to Avoid

1. **Don't try to make Haiku follow complex exclusion rules via prompts alone.** Build code-level overrides for hard boundaries.

2. **Don't fetch data sequentially when you can parallelize.** Use ThreadPoolExecutor from day one.

3. **Don't make the frontend fetch N+1 endpoints.** Build a combined init endpoint.

4. **Don't add features before the core works.** MVP is: fetch sector news, classify it, show it on a dashboard. Federal Register integration, trend lines, alerts — all V2.

5. **Restart uvicorn when editing config.py or etl.py.** Auto-reload doesn't always pick up changes to imported modules.

6. **Don't fight the Supabase PostgREST API.** If a query is awkward with the REST API, do it in Python. At this scale, performance doesn't matter.
