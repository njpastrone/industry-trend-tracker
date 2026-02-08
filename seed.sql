-- Industry Intelligence Tracker - Seed Data
-- Run in Supabase SQL Editor after schema.sql

-- 11 GICS Sectors with SPDR ETF tickers
INSERT INTO sectors (name, gics_code, etf_ticker, description) VALUES
    ('Information Technology', '45', 'XLK', 'Software, hardware, semiconductors, IT services'),
    ('Health Care', '35', 'XLV', 'Pharma, biotech, medical devices, health services'),
    ('Financials', '40', 'XLF', 'Banks, insurance, capital markets, financial services'),
    ('Energy', '10', 'XLE', 'Oil & gas, energy equipment, renewable energy'),
    ('Industrials', '20', 'XLI', 'Aerospace, defense, machinery, transportation'),
    ('Consumer Discretionary', '25', 'XLY', 'Retail, automotive, apparel, hospitality'),
    ('Consumer Staples', '30', 'XLP', 'Food, beverage, tobacco, household products'),
    ('Materials', '15', 'XLB', 'Chemicals, metals, mining, construction materials'),
    ('Real Estate', '60', 'XLRE', 'REITs, real estate services, property development'),
    ('Communication Services', '50', 'XLC', 'Media, telecom, entertainment, social platforms'),
    ('Utilities', '55', 'XLU', 'Electric, gas, water utilities, renewable power');

-- Google News RSS feed configs per sector (2 feeds each: broad + specific)
INSERT INTO sector_feeds (sector_id, feed_type, query) VALUES
    ((SELECT id FROM sectors WHERE gics_code = '45'), 'google_news', '"technology sector" OR "tech industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '45'), 'google_news', '"semiconductor industry" OR "AI regulation" OR "software sector"'),
    ((SELECT id FROM sectors WHERE gics_code = '35'), 'google_news', '"healthcare industry" OR "pharmaceutical sector" OR "biotech sector"'),
    ((SELECT id FROM sectors WHERE gics_code = '35'), 'google_news', '"FDA regulation" OR "drug pricing" OR "medical devices"'),
    ((SELECT id FROM sectors WHERE gics_code = '40'), 'google_news', '"banking sector" OR "financial services industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '40'), 'google_news', '"interest rate" bank OR "SEC regulation" financial'),
    ((SELECT id FROM sectors WHERE gics_code = '10'), 'google_news', '"energy sector" OR "oil industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '10'), 'google_news', '"renewable energy" OR "OPEC" OR "energy transition"'),
    ((SELECT id FROM sectors WHERE gics_code = '20'), 'google_news', '"industrial sector" OR "manufacturing industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '20'), 'google_news', '"supply chain" OR "defense industry" OR "infrastructure spending"'),
    ((SELECT id FROM sectors WHERE gics_code = '25'), 'google_news', '"retail sector" OR "consumer spending"'),
    ((SELECT id FROM sectors WHERE gics_code = '25'), 'google_news', '"e-commerce industry" OR "housing market" consumer'),
    ((SELECT id FROM sectors WHERE gics_code = '30'), 'google_news', '"consumer staples" OR "food industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '30'), 'google_news', '"grocery industry" OR "consumer goods" sector'),
    ((SELECT id FROM sectors WHERE gics_code = '15'), 'google_news', '"materials sector" OR "mining industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '15'), 'google_news', '"commodity prices" OR "steel industry" OR "chemicals sector"'),
    ((SELECT id FROM sectors WHERE gics_code = '60'), 'google_news', '"real estate sector" OR "REIT industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '60'), 'google_news', '"commercial real estate" OR "housing market" rates'),
    ((SELECT id FROM sectors WHERE gics_code = '50'), 'google_news', '"media industry" OR "telecom sector"'),
    ((SELECT id FROM sectors WHERE gics_code = '50'), 'google_news', '"streaming industry" OR "social media regulation"'),
    ((SELECT id FROM sectors WHERE gics_code = '55'), 'google_news', '"utilities sector" OR "power industry"'),
    ((SELECT id FROM sectors WHERE gics_code = '55'), 'google_news', '"renewable energy" utility OR "grid infrastructure"');

-- Initialize empty financials rows for each sector (will be populated by pipeline)
INSERT INTO sector_financials (sector_id)
SELECT id FROM sectors;
