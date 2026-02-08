# Product Spec: Industry Intelligence Tracker

## Vision

A dashboard that gives IR professionals a real-time view of what's happening across major industries — regulatory shifts, analyst sentiment, sector performance, M&A waves — so they can anticipate investor questions before they're asked.

## Target User

IR professionals and IR service salespeople who need to:
- Prepare for earnings calls by understanding sector-wide themes
- Anticipate investor questions about industry trends
- Spot patterns across companies (multiple downgrades in one sector = systemic, not idiosyncratic)
- Stay ahead of regulatory changes that affect their sector

## Core Problem

IR teams are reactive. A regulatory change hits their sector, and they scramble to prepare a response. Three competitors get downgraded in the same week, and they don't connect the dots until an analyst asks about it. Macro themes emerge gradually, and by the time they're obvious, investors have already been asking about them for weeks.

## User Stories

### Must Have (MVP)

1. **As an IR professional**, I want to see a dashboard of all 11 GICS sectors with their current health/sentiment, so I can quickly identify which sectors are under pressure.

2. **As an IR professional**, I want to drill into a specific sector and see the recent news, regulatory changes, and analyst sentiment driving the narrative, so I can prepare for investor questions.

3. **As an IR professional**, I want to see sector ETF performance alongside news signals, so I can connect narrative trends with market movements.

4. **As an IR professional**, I want AI-generated sector summaries that synthesize multiple signals into a coherent narrative (e.g., "Healthcare facing regulatory headwinds: FDA policy changes + 3 analyst downgrades this week"), so I don't have to piece it together myself.

5. **As an IR professional**, I want to filter by signal type (regulatory, analyst, M&A, macro) to focus on the category most relevant to my preparation.

### Should Have (V2)

6. **As an IR professional**, I want to track how sector sentiment has changed over time (trend lines), so I can identify emerging themes early.

7. **As an IR professional**, I want alerts when a sector experiences a significant shift (e.g., 3+ negative signals in 48 hours), so I'm not checking the dashboard constantly.

8. **As an IR professional**, I want to compare two sectors side-by-side, so I can understand relative positioning.

9. **As an IR professional**, I want to see which federal agencies have issued new rules relevant to each sector, so I can track regulatory risk.

### Nice to Have (V3)

10. **As an IR salesperson**, I want to deep-link from a sector trend to my Sales Intelligence Tracker to see which companies in my watchlist are affected.

11. **As an IR professional**, I want macro-economic indicators (interest rates, PPI, industrial production) layered onto sector views, so I can see how macro factors drive sector performance.

## Feature Set

### Sector Dashboard (Home Page)
- Grid/list of 11 GICS sectors
- Each sector card shows:
  - Sector name and SPDR ETF ticker
  - ETF performance (7D, 30D) with color coding
  - Signal count (last 7 days)
  - AI-generated one-line summary of current theme
  - Sentiment indicator (positive / neutral / negative)
- Sortable by: performance, signal count, sentiment
- Click to drill into sector detail

### Sector Detail Page
- Sector header: name, ETF performance chart (30D), key stats
- Signal feed: chronological list of classified signals with:
  - Headline, source, date
  - Signal type badge (regulatory, analyst, M&A, macro, earnings)
  - AI summary of IR relevance
- Sector narrative: AI-generated 2-3 paragraph summary of the current macro theme
- Regulatory tracker: recent federal register entries relevant to this sector
- Sub-industry breakdown (optional): 25 GICS industry groups within the sector

### Signal Classification
- Each news article classified into:
  - **Signal type**: regulatory, analyst_sentiment, earnings_trend, m_and_a, competitive, macro_economic, esg, neutral
  - **Sentiment**: positive, negative, neutral
  - **IR relevance score**: 0.0-1.0 (how likely are investors to ask about this?)
  - **Summary**: 1-2 sentence description focused on the sector-level implication

### Data Pipeline
- Daily batch job (like sales tracker)
- Per-sector RSS feeds + regulatory feeds
- AI classification via Claude Haiku
- Sector ETF performance via yfinance
- Sector narrative generation (one per sector per run)

## What's Out of Scope (MVP)

- Individual company tracking (that's the Sales Intelligence Tracker)
- Real-time streaming (daily batch is fine)
- User accounts / authentication (localStorage profile, like sales tracker)
- Paid data sources (all free tier)
- Mobile app (responsive web only)
- Email/Slack notifications (manual check for MVP)
- Historical trend analysis beyond 30 days (keep it simple)
- GICS sub-industry level (start with 11 sectors, expand later)

## Success Metrics

- User can identify the top 3 sectors under pressure within 30 seconds of opening the app
- Sector narrative summaries are accurate and actionable (manual quality check)
- Pipeline runs in under 2 minutes for all 11 sectors
- Total cost stays under $5/month
