# Pipeline Design: Industry Intelligence Tracker

## Overview

Daily batch pipeline that fetches sector-level news, classifies signals, pulls ETF performance data, and generates sector narratives. Same architectural pattern as the sales tracker (fetch -> classify -> store), adapted for industry-level analysis.

## Pipeline Flow

```
1. Fetch sector news (RSS)          -- per sector, multiple feeds
2. Dedup & filter articles           -- URL dedup, relevance check
3. Batch classify signals (Claude)   -- signal type, sentiment, IR relevance
4. Fetch sector financials (yfinance)-- ETF performance, relative vs SPY
5. Generate sector narratives        -- one summary per sector from top signals
```

## Data Sources

### Primary: Google News RSS

Same approach as the sales tracker, but with sector-level queries instead of company names.

```python
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
```

**Query strategy per sector** (2-3 queries each to balance coverage vs noise):

| Sector | Query 1 (broad) | Query 2 (specific) |
|--------|-----------------|-------------------|
| Information Technology | "technology sector" OR "tech industry" | "semiconductor industry" OR "AI regulation" OR "software sector" |
| Health Care | "healthcare industry" OR "pharmaceutical sector" | "FDA regulation" OR "biotech sector" OR "drug pricing" |
| Financials | "banking sector" OR "financial services" | "interest rate" bank OR "SEC regulation" financial |
| Energy | "energy sector" OR "oil industry" | "renewable energy" OR "OPEC" OR "energy transition" |
| Industrials | "industrial sector" OR "manufacturing industry" | "supply chain" OR "defense industry" OR "infrastructure" |
| Consumer Discretionary | "retail sector" OR "consumer spending" | "e-commerce industry" OR "housing market" |
| Consumer Staples | "consumer staples" OR "food industry" | "grocery industry" OR "consumer goods" |
| Materials | "materials sector" OR "mining industry" | "commodity prices" OR "steel industry" OR "chemicals sector" |
| Real Estate | "real estate sector" OR "REIT" industry | "commercial real estate" OR "housing market" |
| Communication Services | "media industry" OR "telecom sector" | "streaming industry" OR "social media regulation" |
| Utilities | "utilities sector" OR "power industry" | "renewable energy" utility OR "grid infrastructure" |

**Articles per sector**: Limit to 15-20 per query (vs 10 for company-level). Sector queries are broader, so more articles but also more noise.

### Supplementary: EINNews RSS (V2)

EINNews provides pre-organized industry feeds. URL pattern: `https://{industry}.einnews.com/all_rss`

Useful sectors: `technology`, `healthcare`, `financial`, `energy`, `automotive`, `semiconductors`, `pharmaceutical`, `realestate`

### Supplementary: Federal Register API (V2)

For regulatory signal detection. REST API at `https://www.federalregister.gov/api/v1/documents.json`

Key parameters:
- `conditions[agencies][]` — filter by agency (FDA, SEC, EPA, etc.)
- `conditions[type][]` — filter by document type (rule, proposed_rule, notice)
- `conditions[publication_date][gte]` — date range
- `per_page` — results per page

Agency-to-sector mapping:

| Agency | Sectors |
|--------|---------|
| FDA, HHS, CMS | Health Care |
| SEC, FDIC, OCC, CFPB | Financials |
| EPA, DOE, FERC | Energy, Utilities, Materials |
| FCC | Communication Services |
| FTC, DOJ Antitrust | All (especially Technology) |
| DOT, DOD | Industrials |
| Commerce (BIS) | Technology (export controls), Materials (tariffs) |

## Classification

### Signal Classification Prompt

Adapted from the sales tracker's prompt, but focused on sector-level analysis instead of company-specific IR pain.

```
<role>
You are a macro sector analyst. Your job is to determine whether a news headline
represents a meaningful signal about an industry sector's direction — something
that institutional investors or IR teams would want to know about.
</role>

<first_check>
BEFORE analyzing, check: is this headline actually about the {sector_name} sector
as a whole, or is it about a single company's internal matter?

If it's purely about one company with no sector-wide implications, classify as
"neutral" with ir_relevance 0.0.

If it reflects a sector-wide trend, regulatory change, or pattern that affects
multiple companies, proceed with full analysis.
</first_check>

<signal_types>
- regulatory: Government regulation, policy changes, enforcement actions affecting the sector
- analyst_sentiment: Sector-wide analyst actions, outlook changes, rating trends
- earnings_trend: Patterns in earnings across the sector (beat/miss rates, guidance trends)
- m_and_a: M&A activity, consolidation trends, deal flow
- competitive: Market structure changes, disruption, competitive dynamics
- macro_economic: Interest rates, commodities, FX, employment — as they affect this sector
- esg: ESG/sustainability trends, climate regulation, reporting changes
- neutral: Not a meaningful sector signal
</signal_types>

<sentiment_guide>
- positive: Tailwind for the sector (deregulation, strong earnings, capital inflows)
- negative: Headwind (new regulation, downgrades, capital outflows, disruption)
- neutral: Informational, no clear directional signal
</sentiment_guide>

<scoring_guide>
ir_relevance reflects how likely institutional investors are to ask about this:
- 0.8-1.0: Major — regulatory overhaul, multiple analyst downgrades, sector crisis
- 0.5-0.7: Significant — notable M&A, emerging trend, policy proposal
- 0.2-0.4: Minor — routine coverage, single data point
- 0.0: Not a sector signal — single-company news, operational detail
</scoring_guide>

<input>
Sector: {sector_name}
Headline: {title}
Source: {source}
</input>

Respond with ONLY this JSON:
{{
    "summary": "1-2 sentence summary focused on sector-level implication",
    "signal_type": "one of the types above",
    "sentiment": "positive | negative | neutral",
    "ir_relevance": 0.0-1.0
}}
```

### Batch Classification Prompt

Same pattern as the sales tracker — classify up to 8 articles per API call:

```
<role>
You are a macro sector analyst classifying headlines for the {sector_name} sector.
</role>

<input>
Sector: {sector_name}
Headlines:
{headlines_block}
</input>

[Same signal_types, sentiment_guide, scoring_guide as above]

Respond with ONLY this JSON:
{{
  "results": [
    {{
      "headline_index": 0,
      "summary": "...",
      "signal_type": "...",
      "sentiment": "positive | negative | neutral",
      "ir_relevance": 0.0-1.0
    }}
  ]
}}
```

### Sector Narrative Prompt

One call per sector after classification. Takes the top signals and generates a coherent summary.

```
<role>
You are a senior macro strategist writing a sector briefing for IR professionals.
</role>

<task>
Write a brief sector update for {sector_name} based on the signals below.

Short summary (1 sentence): What's the single most important thing happening
in this sector right now?

Full summary (2-3 paragraphs): Synthesize the signals into a coherent narrative.
What's driving this sector? What should IR teams be prepared to discuss with
investors? Connect the dots between individual signals into a theme.

Key themes: List 2-4 short theme labels (e.g., "FDA regulatory pressure",
"M&A consolidation wave").
</task>

<signals>
{signals_block}
</signals>

<sector_context>
ETF: {etf_ticker}
7D performance: {price_change_7d}
30D performance: {price_change_30d}
vs S&P 500 (30D): {vs_spy_30d}
</sector_context>

Respond with ONLY this JSON:
{{
    "summary_short": "1 sentence",
    "summary_full": "2-3 paragraphs",
    "key_themes": ["theme1", "theme2"],
    "sentiment": "positive | negative | neutral | mixed"
}}
```

### Relevance Filtering

Same lesson from the sales tracker: Claude Haiku sometimes misclassifies. Apply a code-level filter for headlines that are clearly single-company news appearing in a sector feed.

```python
# If headline mentions only one company and no sector keywords,
# override to neutral. Check for presence of sector-level terms:
SECTOR_KEYWORDS = [
    "sector", "industry", "market", "regulation", "policy",
    "across", "widespread", "multiple", "wave", "trend",
]
```

This is less critical than the sales tracker's keyword override (where Haiku consistently misclassified EEOC probes) but worth having as a safety net.

## Pipeline Implementation

### process_sector() — per-sector processing

```python
def process_sector(sector: dict) -> dict:
    """Fetch and classify news for a single sector."""
    stats = {"articles_fetched": 0, "articles_new": 0, "signals_created": 0}

    # 1. Fetch from all active feeds for this sector
    feeds = db.get_sector_feeds(sector["id"])
    all_articles = []
    for feed in feeds:
        articles = fetch_sector_news(feed)
        all_articles.extend(articles)

    # 2. Dedup against existing URLs
    new_articles = dedup_and_filter(all_articles)

    # 3. Batch classify (same batching pattern as sales tracker)
    classifications = batch_classify_sector_articles(new_articles, sector["name"])

    # 4. Store articles + signals
    store_articles_and_signals(sector["id"], new_articles, classifications)

    return stats
```

### run_pipeline() — orchestration

```python
def run_pipeline() -> dict:
    """Run full pipeline for all sectors."""
    sectors = db.get_sectors()

    # 1. Process all sectors (parallel, 5 workers — same as sales tracker)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_sector, s): s for s in sectors}
        # ... collect results

    # 2. Refresh sector financials (all 11 ETFs in one yfinance call)
    refresh_sector_financials()

    # 3. Generate narratives (one Claude call per sector with signals)
    generate_all_narratives()

    return totals
```

### Batch Size Estimates

| Step | Per Sector | Total (11 sectors) | Claude API Calls |
|------|-----------|-------------------|-----------------|
| Fetch articles | ~30 articles | ~330 articles | 0 |
| Classify (batch of 8) | ~4 API calls | ~44 API calls | 44 |
| Narrative generation | 1 API call | 11 API calls | 11 |
| **Total** | | | **~55 calls/run** |

At Claude Haiku pricing (~$0.00025/call for short prompts): **~$0.014/run**, or ~$0.42/month for daily runs.

### Financial Data Fetching

```python
def refresh_sector_financials():
    """Fetch all sector ETF data in one yfinance call."""
    etf_tickers = ["XLK", "XLV", "XLF", "XLE", "XLI", "XLY",
                   "XLP", "XLB", "XLRE", "XLC", "XLU", "SPY"]

    data = yf.download(etf_tickers, period="1mo")
    spy_data = extract_spy(data)  # for relative performance calculation

    for sector in sectors:
        etf = sector["etf_ticker"]
        financials = {
            "etf_price": current_price(data, etf),
            "price_change_7d": calc_change(data, etf, 5),  # 5 trading days
            "price_change_30d": calc_change(data, etf, 20), # 20 trading days
            "price_change_ytd": calc_ytd(data, etf),
            "vs_spy_7d": calc_change(data, etf, 5) - calc_change(data, "SPY", 5),
            "vs_spy_30d": calc_change(data, etf, 20) - calc_change(data, "SPY", 20),
        }
        db.upsert_sector_financials(sector["id"], financials)
```

One `yf.download()` call for all 12 tickers (11 sectors + SPY) — very efficient.
