-- Industry Intelligence Tracker - Database Schema
-- Run in Supabase SQL Editor on first deploy

-- 11 GICS sectors (seeded, rarely changes)
CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    gics_code TEXT UNIQUE NOT NULL,
    etf_ticker TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RSS feed configurations per sector (multiple feeds per sector)
CREATE TABLE sector_feeds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    feed_type TEXT NOT NULL,
    query TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fetched news articles, deduplicated by URL
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

-- AI-classified signals from articles (one signal per article)
CREATE TABLE sector_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES sector_articles(id) ON DELETE CASCADE,
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    summary TEXT,
    signal_type TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    ir_relevance REAL DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sector_signals_sector ON sector_signals(sector_id);
CREATE INDEX idx_sector_signals_type ON sector_signals(signal_type);
CREATE INDEX idx_sector_signals_created ON sector_signals(created_at DESC);
CREATE INDEX idx_sector_signals_relevance ON sector_signals(ir_relevance);

-- ETF performance data, one row per sector, refreshed daily
CREATE TABLE sector_financials (
    sector_id UUID PRIMARY KEY REFERENCES sectors(id) ON DELETE CASCADE,
    etf_price REAL,
    price_change_7d REAL,
    price_change_30d REAL,
    price_change_ytd REAL,
    vs_spy_7d REAL,
    vs_spy_30d REAL,
    volume_avg_30d BIGINT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI-generated sector summaries, one per sector per pipeline run
CREATE TABLE sector_narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    summary_short TEXT,
    summary_full TEXT,
    key_themes TEXT[],
    ir_talking_points TEXT[],
    sentiment TEXT,
    signal_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sector_narratives_sector ON sector_narratives(sector_id);
CREATE INDEX idx_sector_narratives_created ON sector_narratives(created_at DESC);
