# Data Model: Industry Intelligence Tracker

## Entity Relationship Overview

```
sectors (11 GICS sectors)
  ├── sector_feeds (RSS/news sources per sector)
  ├── sector_articles (fetched news)
  │   └── sector_signals (AI-classified signals)
  ├── sector_financials (ETF performance data)
  ├── sector_narratives (AI-generated summaries)
  └── sector_regulatory (federal register entries)
```

## Tables

### sectors

The 11 GICS sectors. Seeded on first deploy, rarely changes.

```sql
CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,          -- "Information Technology"
    gics_code TEXT UNIQUE NOT NULL,     -- "45"
    etf_ticker TEXT NOT NULL,           -- "XLK"
    description TEXT,                   -- "Software, hardware, semiconductors, IT services"
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Seed data (11 rows):

| name | gics_code | etf_ticker |
|------|-----------|------------|
| Information Technology | 45 | XLK |
| Health Care | 35 | XLV |
| Financials | 40 | XLF |
| Energy | 10 | XLE |
| Industrials | 20 | XLI |
| Consumer Discretionary | 25 | XLY |
| Consumer Staples | 30 | XLP |
| Materials | 15 | XLB |
| Real Estate | 60 | XLRE |
| Communication Services | 50 | XLC |
| Utilities | 55 | XLU |

### sector_feeds

RSS feed configurations per sector. Multiple feeds per sector.

```sql
CREATE TABLE sector_feeds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    feed_type TEXT NOT NULL,            -- "google_news", "einnews", "federal_register"
    query TEXT NOT NULL,                -- search query or feed URL
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Example rows:

| sector | feed_type | query |
|--------|-----------|-------|
| Information Technology | google_news | "technology sector" OR "semiconductor industry" OR "software industry" |
| Information Technology | google_news | "AI regulation" OR "tech antitrust" |
| Information Technology | einnews | https://technology.einnews.com/all_rss |
| Health Care | google_news | "healthcare industry" OR "pharmaceutical sector" OR "biotech sector" |
| Health Care | federal_register | agency=FDA,HHS,CMS |
| Financials | google_news | "banking sector" OR "financial services industry" |
| Financials | federal_register | agency=SEC,FDIC,OCC,CFPB |

### sector_articles

Fetched news articles, deduplicated by URL (same pattern as sales tracker).

```sql
CREATE TABLE sector_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    feed_id UUID REFERENCES sector_feeds(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sector_articles_sector ON sector_articles(sector_id);
CREATE INDEX idx_sector_articles_url ON sector_articles(url);
CREATE INDEX idx_sector_articles_published ON sector_articles(published_at DESC);
```

### sector_signals

AI-classified signals from articles. One signal per article.

```sql
CREATE TABLE sector_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES sector_articles(id) ON DELETE CASCADE,
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    summary TEXT,                       -- AI-generated 1-2 sentence summary
    signal_type TEXT NOT NULL,          -- see Signal Types below
    sentiment TEXT NOT NULL,            -- "positive", "negative", "neutral"
    ir_relevance REAL DEFAULT 0.5,     -- 0.0-1.0: how likely investors ask about this
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sector_signals_sector ON sector_signals(sector_id);
CREATE INDEX idx_sector_signals_type ON sector_signals(signal_type);
CREATE INDEX idx_sector_signals_created ON sector_signals(created_at DESC);
CREATE INDEX idx_sector_signals_relevance ON sector_signals(ir_relevance);
```

**Signal Types**:

| Type | Description | Examples |
|------|-------------|---------|
| `regulatory` | Government regulation, policy changes | FDA rule, SEC enforcement wave, tariff announcement |
| `analyst_sentiment` | Sector-wide analyst actions | Multiple downgrades, sector outlook changes |
| `earnings_trend` | Earnings patterns across the sector | Beat/miss rates, guidance trends |
| `m_and_a` | M&A activity, consolidation | Deal announcements, takeover waves |
| `competitive` | Competitive dynamics, market share shifts | New entrants, disruption, market structure changes |
| `macro_economic` | Macro factors affecting the sector | Interest rate impact, commodity prices, FX |
| `esg` | ESG/sustainability trends | Climate regulation, ESG reporting changes |
| `neutral` | General news, not a sector signal | |

### sector_financials

ETF performance data, refreshed daily.

```sql
CREATE TABLE sector_financials (
    sector_id UUID PRIMARY KEY REFERENCES sectors(id) ON DELETE CASCADE,
    etf_price REAL,
    price_change_7d REAL,              -- percentage as decimal (0.05 = 5%)
    price_change_30d REAL,
    price_change_ytd REAL,
    vs_spy_7d REAL,                    -- relative performance vs S&P 500
    vs_spy_30d REAL,
    volume_avg_30d BIGINT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### sector_narratives

AI-generated sector summaries. One per sector per pipeline run.

```sql
CREATE TABLE sector_narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    summary_short TEXT,                -- 1 sentence for dashboard card
    summary_full TEXT,                 -- 2-3 paragraphs for detail page
    key_themes TEXT[],                 -- ["FDA regulatory pressure", "M&A consolidation"]
    sentiment TEXT,                    -- overall: "positive", "negative", "neutral", "mixed"
    signal_count INT,                  -- signals used to generate this narrative
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sector_narratives_sector ON sector_narratives(sector_id);
CREATE INDEX idx_sector_narratives_created ON sector_narratives(created_at DESC);
```

### sector_regulatory (V2)

Federal Register entries relevant to each sector. Optional for MVP — can start with regulatory signals in the general signal feed.

```sql
CREATE TABLE sector_regulatory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    agency TEXT,                        -- "FDA", "SEC", "EPA"
    document_type TEXT,                 -- "rule", "proposed_rule", "notice"
    url TEXT UNIQUE,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Key Differences from Sales Tracker Schema

| Aspect | Sales Tracker | Industry Tracker |
|--------|--------------|-----------------|
| Core entity | `companies` (user-managed watchlist) | `sectors` (fixed 11 GICS sectors) |
| Articles | Per-company, company-specific queries | Per-sector, industry-level queries |
| Signals | IR pain score (0-1) for a specific company | IR relevance (0-1) + sentiment for a sector |
| Financials | Per-company stock data | Per-sector ETF data + relative performance |
| AI output | Talking points for outreach | Sector narratives for preparation |
| Outreach | contacted/snoozed tracking | None (monitoring, not action-tracking) |
| User data | profiles, profile_companies | Minimal (maybe saved sector preferences) |

## Migration Notes

No data migration needed — this is a greenfield app. Seed the `sectors` table on first deploy with the 11 GICS sectors and their ETF tickers. Seed `sector_feeds` with initial Google News queries per sector.
