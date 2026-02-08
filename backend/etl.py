"""
ETL Pipeline for Industry Intelligence Tracker.

Pipeline stages:
1. Fetch RSS feeds per sector (Google News)
2. Deduplicate URLs against existing articles
3. Batch classify with Claude Haiku (8 articles per call)
4. Fetch ETF financials via yfinance
5. Generate sector narratives with Claude Haiku
"""

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import anthropic
import feedparser
import httpx
import yfinance as yf

import db
from config import (
    ALL_TICKERS,
    ANTHROPIC_API_KEY,
    ARTICLES_PER_FEED,
    BATCH_CLASSIFICATION_PROMPT,
    BATCH_SIZE,
    BENCHMARK_TICKER,
    GOOGLE_NEWS_RSS_URL,
    HAIKU_MODEL,
    MAX_WORKERS,
    NARRATIVE_PROMPT,
)

logger = logging.getLogger(__name__)

# Anthropic client (module-level singleton)
_anthropic_client: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


# ---------------------------------------------------------------------------
# 1. RSS Fetching
# ---------------------------------------------------------------------------

def fetch_feed_articles(feed: dict, sector_id: str) -> list[dict]:
    """Fetch articles from a Google News RSS feed. Returns article dicts ready for DB."""
    query = feed["query"]
    url = GOOGLE_NEWS_RSS_URL.format(query=query)

    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch feed {feed['id']}: {e}")
        return []

    parsed = feedparser.parse(resp.text)
    articles = []

    for entry in parsed.entries[:ARTICLES_PER_FEED]:
        # Google News RSS: title often ends with " - Source Name"
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        # Extract source from title suffix
        source = None
        if " - " in title:
            source = title.rsplit(" - ", 1)[-1].strip()

        # Parse published date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            except (ValueError, TypeError):
                pass

        articles.append({
            "sector_id": sector_id,
            "feed_id": feed["id"],
            "title": title,
            "url": link,
            "source": source,
            "published_at": published_at,
        })

    return articles


# ---------------------------------------------------------------------------
# 2. Relevance Filter (code-level override)
# ---------------------------------------------------------------------------

# Sector-level keywords — if headline contains these, it's likely sector-relevant
_SECTOR_KEYWORDS = re.compile(
    r"\b(sector|industry|industries|market|markets|regulation|regulatory|policy|"
    r"across|widespread|multiple|wave|trend|downgrade|upgrade|analyst|index|"
    r"benchmark|etf|outlook|forecast|tariff|trade war|antitrust|merger wave|"
    r"layoffs|hiring|strike)\b",
    re.IGNORECASE,
)

# Single-company patterns — earnings, exec moves, product launches for one company
_COMPANY_PATTERNS = re.compile(
    r"\b(reports earnings|beats estimates|misses estimates|quarterly results|"
    r"revenue (rises|falls|surges|drops)|stock (rises|falls|surges|drops|jumps|plunges)|"
    r"shares (rise|fall|surge|drop|jump|plunge)|CEO|CFO|appoints|names|hires|fires|"
    r"IPO filing|stock buyback|dividend (hike|cut)|price target|"
    r"launches product|unveils|announces partnership)\b",
    re.IGNORECASE,
)


def _is_single_company_news(title: str) -> bool:
    """Return True if headline is about a single company, not sector-level."""
    has_sector_keyword = bool(_SECTOR_KEYWORDS.search(title))
    has_company_pattern = bool(_COMPANY_PATTERNS.search(title))
    # If it has company patterns but NO sector keywords, it's single-company news
    return has_company_pattern and not has_sector_keyword


# ---------------------------------------------------------------------------
# 3. Batch Classification
# ---------------------------------------------------------------------------

def _classify_batch(batch: list[dict], sector_name: str) -> list[dict]:
    """Classify a batch of articles (up to BATCH_SIZE) with Claude Haiku."""
    headlines_block = "\n".join(
        f"[{i}] {a['title']}" for i, a in enumerate(batch)
    )
    prompt = BATCH_CLASSIFICATION_PROMPT.format(
        sector_name=sector_name,
        headlines_block=headlines_block,
    )

    try:
        response = _get_anthropic().messages.create(
            model=HAIKU_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        data = json.loads(text)
        return data.get("results", [])
    except (json.JSONDecodeError, anthropic.APIError, KeyError, IndexError) as e:
        logger.warning(f"Batch classification failed for {sector_name}: {e}")
        return []


def _classify_single(article: dict, sector_name: str) -> dict | None:
    """Fallback: classify a single article if batch fails."""
    results = _classify_batch([article], sector_name)
    return results[0] if results else None


def batch_classify(articles: list[dict], sector_name: str) -> list[dict]:
    """Classify articles in batches of BATCH_SIZE. Returns signal dicts ready for DB."""
    signals = []

    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i : i + BATCH_SIZE]
        results = _classify_batch(batch, sector_name)

        if results:
            # Map results back to articles by headline_index
            for result in results:
                idx = result.get("headline_index")
                if idx is None or idx < 0 or idx >= len(batch):
                    continue

                article = batch[idx]

                signal_type = result.get("signal_type", "neutral")
                sentiment = result.get("sentiment", "neutral")
                ir_relevance = float(result.get("ir_relevance", 0.0))

                # Code-level override: force single-company news to neutral
                if _is_single_company_news(article["title"]):
                    signal_type = "neutral"
                    ir_relevance = 0.0

                signals.append({
                    "article_id": article["id"],
                    "sector_id": article["sector_id"],
                    "summary": result.get("summary", ""),
                    "signal_type": signal_type,
                    "sentiment": sentiment,
                    "ir_relevance": ir_relevance,
                })
        else:
            # Fallback: classify individually
            for article in batch:
                result = _classify_single(article, sector_name)
                if result:
                    signal_type = result.get("signal_type", "neutral")
                    sentiment = result.get("sentiment", "neutral")
                    ir_relevance = float(result.get("ir_relevance", 0.0))

                    if _is_single_company_news(article["title"]):
                        signal_type = "neutral"
                        ir_relevance = 0.0

                    signals.append({
                        "article_id": article["id"],
                        "sector_id": article["sector_id"],
                        "summary": result.get("summary", ""),
                        "signal_type": signal_type,
                        "sentiment": sentiment,
                        "ir_relevance": ir_relevance,
                    })

    return signals


# ---------------------------------------------------------------------------
# 4. Financials (yfinance)
# ---------------------------------------------------------------------------

def refresh_sector_financials(sectors: list[dict]) -> int:
    """Fetch ETF data for all sectors + SPY. Returns count of sectors updated."""
    ticker_to_sector = {s["etf_ticker"]: s for s in sectors}

    try:
        # Single download call for all 12 tickers, 6 months for YTD calc
        data = yf.download(ALL_TICKERS, period="6mo", group_by="ticker", progress=False)
    except Exception as e:
        logger.error(f"yfinance download failed: {e}")
        return 0

    if data.empty:
        logger.warning("yfinance returned empty data")
        return 0

    # Calculate SPY changes for relative performance
    spy_changes = _calc_ticker_changes(data, BENCHMARK_TICKER)

    updated = 0
    for ticker, sector in ticker_to_sector.items():
        changes = _calc_ticker_changes(data, ticker)
        if changes is None:
            continue

        financials = {
            "etf_price": changes["price"],
            "price_change_7d": changes["change_7d"],
            "price_change_30d": changes["change_30d"],
            "price_change_ytd": changes["change_ytd"],
            "vs_spy_7d": round(changes["change_7d"] - (spy_changes["change_7d"] if spy_changes else 0), 4),
            "vs_spy_30d": round(changes["change_30d"] - (spy_changes["change_30d"] if spy_changes else 0), 4),
        }

        db.upsert_sector_financials(sector["id"], financials)
        updated += 1

    return updated


def _calc_ticker_changes(data, ticker: str) -> dict | None:
    """Calculate price changes for a single ticker from the downloaded data."""
    try:
        # Handle both multi-ticker (MultiIndex) and single-ticker DataFrames
        if isinstance(data.columns, __import__("pandas").MultiIndex):
            close = data[(ticker, "Close")].dropna()
        else:
            close = data["Close"].dropna()

        if close.empty or len(close) < 2:
            return None

        current_price = float(close.iloc[-1])

        # 7D = ~5 trading days
        price_5d_ago = float(close.iloc[-6]) if len(close) >= 6 else float(close.iloc[0])
        change_7d = round((current_price - price_5d_ago) / price_5d_ago * 100, 4)

        # 30D = ~21 trading days
        price_21d_ago = float(close.iloc[-22]) if len(close) >= 22 else float(close.iloc[0])
        change_30d = round((current_price - price_21d_ago) / price_21d_ago * 100, 4)

        # YTD = from first trading day of current year
        current_year = datetime.now().year
        ytd_data = close[close.index.year == current_year]
        if not ytd_data.empty and len(ytd_data) >= 2:
            ytd_start = float(ytd_data.iloc[0])
            change_ytd = round((current_price - ytd_start) / ytd_start * 100, 4)
        else:
            change_ytd = 0.0

        return {
            "price": round(current_price, 2),
            "change_7d": change_7d,
            "change_30d": change_30d,
            "change_ytd": change_ytd,
        }
    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Failed to calc changes for {ticker}: {e}")
        return None


# ---------------------------------------------------------------------------
# 5. Narratives
# ---------------------------------------------------------------------------

def generate_narrative(sector: dict, signals: list[dict], financials: dict | None) -> dict | None:
    """Generate a narrative for one sector from its top signals."""
    if not signals:
        return None

    # Build signals block for prompt
    signals_block = "\n".join(
        f"- [{s.get('signal_type', 'neutral')}] [{s.get('sentiment', 'neutral')}] "
        f"{s.get('summary', 'No summary')}"
        for s in signals
    )

    fin = financials or {}
    prompt = NARRATIVE_PROMPT.format(
        sector_name=sector["name"],
        signals_block=signals_block,
        etf_ticker=sector["etf_ticker"],
        price_change_7d=f"{fin.get('price_change_7d', 0):.1f}%" if fin.get("price_change_7d") is not None else "N/A",
        price_change_30d=f"{fin.get('price_change_30d', 0):.1f}%" if fin.get("price_change_30d") is not None else "N/A",
        vs_spy_30d=f"{fin.get('vs_spy_30d', 0):.1f}%" if fin.get("vs_spy_30d") is not None else "N/A",
    )

    try:
        response = _get_anthropic().messages.create(
            model=HAIKU_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        data = json.loads(text)
        narrative = {
            "sector_id": sector["id"],
            "summary_short": data.get("summary_short", ""),
            "summary_full": data.get("summary_full", ""),
            "key_themes": data.get("key_themes", []),
            "sentiment": data.get("sentiment", "neutral"),
            "signal_count": len(signals),
        }
        return db.insert_narrative(narrative)
    except (json.JSONDecodeError, anthropic.APIError, KeyError) as e:
        logger.warning(f"Narrative generation failed for {sector['name']}: {e}")
        return None


def generate_all_narratives(sectors: list[dict]) -> int:
    """Generate narratives for all sectors. Returns count generated."""
    generated = 0
    all_financials = {f["sector_id"]: f for f in db.get_all_financials()}

    for sector in sectors:
        # Get top signals for this sector (non-neutral, sorted by relevance)
        signals = db.get_sector_signals(sector["id"], days=7, min_relevance=0.2)
        # Filter out neutral and sort by relevance
        top_signals = sorted(
            [s for s in signals if s.get("signal_type") != "neutral"],
            key=lambda s: s.get("ir_relevance", 0),
            reverse=True,
        )[:10]

        if not top_signals:
            logger.info(f"No relevant signals for {sector['name']}, skipping narrative")
            continue

        financials = all_financials.get(sector["id"])
        result = generate_narrative(sector, top_signals, financials)
        if result:
            generated += 1

    return generated


# ---------------------------------------------------------------------------
# 6. Orchestration
# ---------------------------------------------------------------------------

def process_sector(sector: dict) -> dict:
    """Process one sector: fetch feeds -> dedup -> classify -> store. Returns stats."""
    sector_id = sector["id"]
    sector_name = sector["name"]

    stats = {"sector": sector_name, "feeds": 0, "fetched": 0, "new": 0, "signals": 0}

    # Get feed configs for this sector
    feeds = db.get_sector_feeds(sector_id)
    stats["feeds"] = len(feeds)

    # Fetch all articles from all feeds
    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, sector_id)
        all_articles.extend(articles)

    stats["fetched"] = len(all_articles)

    if not all_articles:
        return stats

    # Dedup: check which URLs already exist in DB
    all_urls = [a["url"] for a in all_articles]
    existing_urls = db.get_existing_urls(all_urls)

    # Also dedup within this batch (Google News returns dupes across queries)
    seen_urls = set()
    new_articles = []
    for article in all_articles:
        url = article["url"]
        if url not in existing_urls and url not in seen_urls:
            seen_urls.add(url)
            new_articles.append(article)

    stats["new"] = len(new_articles)

    if not new_articles:
        return stats

    # Insert articles into DB (get back rows with IDs)
    # Fallback: batch -> individual on failure (lesson #8)
    try:
        inserted = db.insert_articles(new_articles)
    except Exception as e:
        logger.warning(f"Batch insert failed for {sector_name}, falling back to individual: {e}")
        inserted = []
        for article in new_articles:
            try:
                result = db.insert_articles([article])
                inserted.extend(result)
            except Exception:
                pass
    if not inserted:
        return stats

    # Build a URL -> inserted row map for getting article IDs
    inserted_by_url = {a["url"]: a for a in inserted}
    # Attach IDs to our article dicts for classification
    articles_with_ids = []
    for article in new_articles:
        db_row = inserted_by_url.get(article["url"])
        if db_row:
            article["id"] = db_row["id"]
            articles_with_ids.append(article)

    # Classify
    signals = batch_classify(articles_with_ids, sector_name)
    if signals:
        db.insert_signals(signals)
    stats["signals"] = len(signals)

    return stats


def run_pipeline() -> dict:
    """Run the full pipeline. Returns summary stats."""
    logger.info("Pipeline started")
    start = datetime.now(timezone.utc)

    sectors = db.get_sectors()
    sector_stats = []

    # Process sectors in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_sector, s): s for s in sectors}
        for future in as_completed(futures):
            sector = futures[future]
            try:
                stats = future.result()
                sector_stats.append(stats)
                logger.info(f"  {stats['sector']}: {stats['new']} new articles, {stats['signals']} signals")
            except Exception as e:
                logger.error(f"  Failed to process {sector['name']}: {e}")
                sector_stats.append({"sector": sector["name"], "error": str(e)})

    # Financials (single call for all tickers)
    logger.info("Refreshing financials...")
    financials_updated = refresh_sector_financials(sectors)

    # Narratives (sequential, one Claude call per sector)
    logger.info("Generating narratives...")
    narratives_generated = generate_all_narratives(sectors)

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()

    result = {
        "status": "completed",
        "elapsed_seconds": round(elapsed, 1),
        "sectors_processed": len(sector_stats),
        "total_new_articles": sum(s.get("new", 0) for s in sector_stats),
        "total_signals": sum(s.get("signals", 0) for s in sector_stats),
        "financials_updated": financials_updated,
        "narratives_generated": narratives_generated,
        "sector_details": sector_stats,
    }

    logger.info(f"Pipeline completed in {elapsed:.1f}s")
    return result
