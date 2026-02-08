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
ARTICLES_PER_FEED = 10  # max articles to fetch per RSS feed (halved from 20)
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}+when:7d&hl=en-US&gl=US&ceid=US:en"

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
Today's date is {today_date}.
</role>

<default_behavior>
Your DEFAULT classification is "neutral" with ir_relevance 0.0. Only upgrade a headline to a non-neutral signal type when it clearly describes a pattern, trend, or force affecting MULTIPLE companies across the {sector_name} sector.
</default_behavior>

<signal_types>
Classify as a sector signal ONLY when the headline reflects a force affecting multiple companies:
- regulatory: Government regulation, policy changes, enforcement actions affecting the sector broadly
- analyst_sentiment: Sector-wide analyst actions, outlook changes, rating trends across firms
- earnings_trend: Patterns in earnings across multiple companies (beat/miss rates, guidance trends)
- m_and_a: Sector consolidation wave, multiple deal announcements, deal flow trends
- competitive: Market structure changes, disruption affecting multiple players
- macro_economic: Interest rates, commodities, FX, employment — as they reshape this sector
- esg: ESG/sustainability trends, climate regulation, sector-wide reporting changes
- neutral: DEFAULT — single-company news, operational details, product launches, executive changes, or anything not clearly sector-wide
</signal_types>

<examples>
Example 1 — Sector-level signal:
Headline: "FDA proposes sweeping new drug pricing rules affecting all pharmaceutical manufacturers"
Classification: signal_type="regulatory", sentiment="negative", ir_relevance=0.8
Summary: "FDA's proposed drug pricing rules would impact margins across all pharma manufacturers, representing a major regulatory shift for the sector."

Example 2 — Single-company news (classify as neutral):
Headline: "Pfizer beats Q3 earnings estimates, raises full-year guidance"
Classification: signal_type="neutral", sentiment="neutral", ir_relevance=0.0
Summary: "Single-company earnings report with no broader sector implications."
</examples>

<sentiment_guide>
- positive: Tailwind for the sector (deregulation, strong earnings across firms, capital inflows)
- negative: Headwind (new regulation, widespread downgrades, capital outflows, disruption)
- neutral: Informational, no clear directional signal, or single-company news
</sentiment_guide>

<scoring_guide>
ir_relevance — how likely institutional investors are to ask about this in a sector context:
- 0.8-1.0: "FDA proposes sweeping new drug pricing rules" — regulatory overhaul, sector crisis, multiple analyst downgrades
- 0.5-0.7: "Healthcare M&A volume hits 5-year high" — notable trend, policy proposal, emerging pattern
- 0.2-0.4: "Hospital staffing costs continue to rise" — routine sector coverage, single data point
- 0.0: "UnitedHealth CEO steps down" — single-company news, executive moves, individual earnings, product launches
</scoring_guide>

<freshness>
If a headline describes an event that is clearly old or no longer current relative to {today_date}, classify as neutral with ir_relevance 0.0.
</freshness>

<input>
Sector: {sector_name}
Headlines:
{headlines_block}
</input>

Remember: DEFAULT to neutral. Only classify as a non-neutral signal type when the headline clearly affects multiple companies across the sector.

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
Today's date is {today_date}.
</role>

<motivation>
IR teams use this briefing to prepare for investor calls. Generic summaries like "the sector faces headwinds and tailwinds" waste their time and erode trust in the tool. Every sentence must reference specific signals, name actual companies/regulators/data points, and be directly usable in an investor conversation.
</motivation>

<task>
Write a sector update for {sector_name} based on the signals below.

Short summary (1 sentence): State the single most important development — name the specific regulatory body, company, data point, or event driving it.

Full summary (2-3 paragraphs): Synthesize the signals into a coherent narrative. Reference specific signals by name. Name the actual regulatory bodies, companies, or data points driving the trend. Connect individual signals into a theme an IR team can explain to investors.

Key themes: List 2-4 short, specific theme labels (e.g., "FDA accelerated approval pathway overhaul", "Semiconductor capex cycle peaking").

IR talking points: Write 2-3 bullet points an IR team can use directly in investor conversations. Each should be a complete, specific statement — not a generic observation.
</task>

<example>
GOOD narrative excerpt: "The SEC's proposed climate disclosure rules (announced Jan 15) are driving compliance cost concerns across the sector, with estimated implementation costs of $2-5M per large-cap firm. Meanwhile, three major utilities — NextEra, Duke Energy, and Southern Company — announced accelerated renewable capex plans totaling $12B."

BAD narrative excerpt: "The sector faces regulatory headwinds and companies are adjusting their strategies accordingly. ESG considerations continue to be important for investors."
</example>

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
    "summary_short": "1 sentence naming the specific driver",
    "summary_full": "2-3 paragraphs referencing specific signals and data points",
    "key_themes": ["specific theme 1", "specific theme 2"],
    "ir_talking_points": ["Complete statement for investor conversations", "Another specific talking point"],
    "sentiment": "positive | negative | neutral | mixed"
}}"""
