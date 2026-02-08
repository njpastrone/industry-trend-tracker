import { useNavigate } from "react-router-dom";
import type { SectorWithMetrics, Sentiment } from "../types";
import { SENTIMENT_CONFIG } from "../types";
import { formatPerformance } from "../utils/format";

export default function SectorCard({ sector }: { sector: SectorWithMetrics }) {
  const navigate = useNavigate();
  const perf = formatPerformance(sector.financials?.price_change_7d);
  const sentiment = (sector.narrative?.sentiment ?? "neutral") as Sentiment;
  const sentimentCfg = SENTIMENT_CONFIG[sentiment] ?? SENTIMENT_CONFIG.neutral;
  const summary =
    sector.narrative?.summary_short || "No narrative available";

  return (
    <div
      onClick={() => navigate(`/sector/${sector.id}`)}
      className="cursor-pointer rounded-lg border border-blue-100 bg-white p-5 transition-shadow hover:shadow-md"
    >
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h3 className="text-base font-semibold text-gray-900">
            {sector.name}
          </h3>
          <span className="text-sm text-gray-400">{sector.etf_ticker}</span>
        </div>
        <span className={`text-lg font-semibold ${perf.color}`}>
          {perf.text}
        </span>
      </div>

      <div className="mb-3 flex items-center gap-3">
        <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
          {sector.signal_count} signals
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className={`inline-block h-2.5 w-2.5 rounded-full ${sentimentCfg.dotColor}`}
          />
          <span className={`text-xs font-medium ${sentimentCfg.textColor}`}>
            {sentimentCfg.label}
          </span>
        </span>
      </div>

      <p className="line-clamp-2 text-sm text-gray-600">{summary}</p>
    </div>
  );
}
