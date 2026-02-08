import type { Sector, SectorFinancials } from "../types";
import { formatPerformance } from "../utils/format";

interface Props {
  sector: Sector;
  financials: SectorFinancials | null;
}

export default function SectorHeader({ sector, financials }: Props) {
  const stats = [
    { label: "7D Change", value: financials?.price_change_7d },
    { label: "30D Change", value: financials?.price_change_30d },
    { label: "YTD", value: financials?.price_change_ytd },
    { label: "vs S&P 500", value: financials?.vs_spy_7d },
  ];

  return (
    <div className="rounded-lg border border-blue-100 bg-white p-5">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{sector.name}</h2>
        <span className="text-sm text-gray-400">{sector.etf_ticker}</span>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((stat) => {
          const perf = formatPerformance(stat.value);
          return (
            <div key={stat.label}>
              <p className="text-xs text-gray-500">{stat.label}</p>
              <p className={`text-lg font-semibold ${perf.color}`}>
                {perf.text}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
