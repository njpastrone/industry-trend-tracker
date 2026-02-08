import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { SectorWithMetrics, Sentiment } from "../types";
import { SENTIMENT_CONFIG } from "../types";
import { formatPerformance } from "../utils/format";

export default function SectorList({
  sectors,
}: {
  sectors: SectorWithMetrics[];
}) {
  const navigate = useNavigate();

  const sorted = useMemo(
    () => [...sectors].sort((a, b) => b.signal_count - a.signal_count),
    [sectors]
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-blue-100 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
            <th className="px-4 py-3">Sector</th>
            <th className="px-4 py-3">Sentiment</th>
            <th className="px-4 py-3 text-right">7D</th>
            <th className="hidden px-4 py-3 text-right md:table-cell">30D</th>
            <th className="hidden px-4 py-3 text-right md:table-cell">YTD</th>
            <th className="hidden px-4 py-3 text-right md:table-cell">vs SPY</th>
            <th className="px-4 py-3 text-right">Signals</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((s) => {
            const perf7d = formatPerformance(s.financials?.price_change_7d);
            const perf30d = formatPerformance(s.financials?.price_change_30d);
            const perfYtd = formatPerformance(s.financials?.price_change_ytd);
            const perfSpy = formatPerformance(s.financials?.vs_spy_7d);
            const sentiment = (s.narrative?.sentiment ?? "neutral") as Sentiment;
            const cfg = SENTIMENT_CONFIG[sentiment] ?? SENTIMENT_CONFIG.neutral;

            return (
              <tr
                key={s.id}
                onClick={() => navigate(`/sector/${s.id}`)}
                className="cursor-pointer border-b border-gray-100 last:border-b-0 hover:bg-blue-50"
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{s.name}</div>
                  <div className="text-xs text-gray-400">{s.etf_ticker}</div>
                </td>
                <td className="px-4 py-3">
                  <span className="flex items-center gap-1.5">
                    <span
                      className={`inline-block h-2.5 w-2.5 rounded-full ${cfg.dotColor}`}
                    />
                    <span className={`text-xs font-medium ${cfg.textColor}`}>
                      {cfg.label}
                    </span>
                  </span>
                </td>
                <td className={`px-4 py-3 text-right font-medium ${perf7d.color}`}>
                  {perf7d.text}
                </td>
                <td className={`hidden px-4 py-3 text-right font-medium md:table-cell ${perf30d.color}`}>
                  {perf30d.text}
                </td>
                <td className={`hidden px-4 py-3 text-right font-medium md:table-cell ${perfYtd.color}`}>
                  {perfYtd.text}
                </td>
                <td className={`hidden px-4 py-3 text-right font-medium md:table-cell ${perfSpy.color}`}>
                  {perfSpy.text}
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                    {s.signal_count}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
