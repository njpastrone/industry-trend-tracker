// --- API Response Types (matching backend/main.py shapes) ---

export interface Sector {
  id: string;
  name: string;
  gics_code: string;
  etf_ticker: string;
  description: string | null;
  created_at: string;
}

export interface SectorFinancials {
  sector_id: string;
  etf_price: number | null;
  price_change_7d: number | null;
  price_change_30d: number | null;
  price_change_ytd: number | null;
  vs_spy_7d: number | null;
  vs_spy_30d: number | null;
  volume_avg_30d: number | null;
  updated_at: string | null;
}

export interface SectorNarrative {
  id: string;
  sector_id: string;
  summary_short: string | null;
  summary_full: string | null;
  key_themes: string[] | null;
  sentiment: string | null;
  signal_count: number | null;
  created_at: string;
}

export interface SectorNarrativeSummary {
  summary_short: string | null;
  sentiment: string | null;
  key_themes: string[] | null;
}

export interface SectorWithMetrics {
  id: string;
  name: string;
  gics_code: string;
  etf_ticker: string;
  financials: SectorFinancials | null;
  signal_count: number;
  narrative: SectorNarrativeSummary | null;
}

export interface SignalArticle {
  title: string;
  url: string;
  source: string | null;
  published_at: string | null;
}

export interface Signal {
  id: string;
  sector_id: string;
  article_id: string;
  signal_type: SignalType;
  sentiment: Sentiment;
  summary: string | null;
  ir_relevance: number;
  created_at: string;
  sector_articles: SignalArticle | null;
}

export interface SectorDetailResponse {
  sector: Sector;
  financials: SectorFinancials | null;
  narrative: SectorNarrative | null;
  signals: Signal[];
  signal_counts_by_type: Record<string, number>;
}

export interface InitData {
  sectors: SectorWithMetrics[];
  last_pipeline_run: string | null;
}

export interface PipelineRunResult {
  status: string;
  elapsed_seconds: number;
  sectors_processed: number;
  total_new_articles: number;
  total_signals: number;
  financials_updated: number;
  narratives_generated: number;
}

// --- Signal & Sentiment Types ---

export type SignalType =
  | "regulatory"
  | "analyst_sentiment"
  | "earnings_trend"
  | "m_and_a"
  | "competitive"
  | "macro_economic"
  | "esg"
  | "neutral";

export type Sentiment = "positive" | "negative" | "neutral" | "mixed";

// --- Display Constants ---

export const SIGNAL_TYPE_LABELS: Record<SignalType, string> = {
  regulatory: "Regulatory",
  analyst_sentiment: "Analyst Sentiment",
  earnings_trend: "Earnings Trend",
  m_and_a: "M&A",
  competitive: "Competitive",
  macro_economic: "Macro Economic",
  esg: "ESG",
  neutral: "Neutral",
};

export const SENTIMENT_CONFIG: Record<
  Sentiment,
  { dotColor: string; textColor: string; label: string }
> = {
  positive: {
    dotColor: "bg-green-500",
    textColor: "text-green-700",
    label: "Positive",
  },
  negative: {
    dotColor: "bg-red-500",
    textColor: "text-red-700",
    label: "Negative",
  },
  neutral: {
    dotColor: "bg-gray-400",
    textColor: "text-gray-600",
    label: "Neutral",
  },
  mixed: {
    dotColor: "bg-amber-500",
    textColor: "text-amber-700",
    label: "Mixed",
  },
};

export const TIME_WINDOW_OPTIONS = [7, 14, 30] as const;
export type TimeWindow = (typeof TIME_WINDOW_OPTIONS)[number];
export type ViewType = "grid" | "list";
