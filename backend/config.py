import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# --- Anthropic ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# --- Pipeline ---
BATCH_SIZE = 8  # articles per Claude API call
MAX_WORKERS = 5  # ThreadPoolExecutor for parallel sector processing
ARTICLES_PER_FEED = 20  # max articles to fetch per RSS feed
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# --- ETF Tickers ---
SECTOR_ETF_TICKERS = ["XLK", "XLV", "XLF", "XLE", "XLI", "XLY", "XLP", "XLB", "XLRE", "XLC", "XLU"]
BENCHMARK_TICKER = "SPY"
ALL_TICKERS = SECTOR_ETF_TICKERS + [BENCHMARK_TICKER]

# --- Signal Types ---
SIGNAL_TYPES = {
    "regulatory": "Government regulation, policy changes, enforcement actions affecting the sector",
    "analyst_sentiment": "Sector-wide analyst actions, outlook changes, rating trends",
    "earnings_trend": "Patterns in earnings across the sector (beat/miss rates, guidance trends)",
    "m_and_a": "M&A activity, consolidation trends, deal flow",
    "competitive": "Market structure changes, disruption, competitive dynamics",
    "macro_economic": "Interest rates, commodities, FX, employment — as they affect this sector",
    "esg": "ESG/sustainability trends, climate regulation, reporting changes",
    "neutral": "Not a meaningful sector signal",
}

# --- Prompts ---
BATCH_CLASSIFICATION_PROMPT = """<role>
You are a macro sector analyst classifying headlines for the {sector_name} sector.
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
Headlines:
{headlines_block}
</input>

Respond with ONLY this JSON:
{{
  "results": [
    {{
      "headline_index": 0,
      "summary": "1-2 sentence summary focused on sector-level implication",
      "signal_type": "one of the types above",
      "sentiment": "positive | negative | neutral",
      "ir_relevance": 0.0
    }}
  ]
}}"""

NARRATIVE_PROMPT = """<role>
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
}}"""
