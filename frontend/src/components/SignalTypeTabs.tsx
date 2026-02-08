import type { SignalType } from "../types";
import { SIGNAL_TYPE_LABELS } from "../types";

interface Props {
  countsByType: Record<string, number>;
  activeType: SignalType | "all";
  onTypeChange: (type: SignalType | "all") => void;
}

export default function SignalTypeTabs({
  countsByType,
  activeType,
  onTypeChange,
}: Props) {
  const totalCount = Object.values(countsByType).reduce((a, b) => a + b, 0);

  const tabs: { key: SignalType | "all"; label: string; count: number }[] = [
    { key: "all", label: "All", count: totalCount },
  ];

  for (const [type, count] of Object.entries(countsByType)) {
    if (count > 0) {
      tabs.push({
        key: type as SignalType,
        label: SIGNAL_TYPE_LABELS[type as SignalType] ?? type,
        count,
      });
    }
  }

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1 border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => onTypeChange(tab.key)}
            className={`whitespace-nowrap px-3 py-2 text-sm font-medium transition-colors ${
              activeType === tab.key
                ? "border-b-2 border-blue-700 text-blue-700"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
            <span className="ml-1.5 text-xs text-gray-400">{tab.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
