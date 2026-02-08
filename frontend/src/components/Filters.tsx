import {
  TIME_WINDOW_OPTIONS,
  SIGNAL_TYPE_LABELS,
  type TimeWindow,
  type SignalType,
  type ViewType,
} from "../types";

const FILTERABLE_TYPES = Object.entries(SIGNAL_TYPE_LABELS).filter(
  ([key]) => key !== "neutral"
) as [SignalType, string][];

interface FiltersProps {
  timeWindow: TimeWindow;
  onTimeWindowChange: (tw: TimeWindow) => void;
  signalType: SignalType | "all";
  onSignalTypeChange: (st: SignalType | "all") => void;
  viewType: ViewType;
  onViewTypeChange: (vt: ViewType) => void;
}

export default function Filters({
  timeWindow,
  onTimeWindowChange,
  signalType,
  onSignalTypeChange,
  viewType,
  onViewTypeChange,
}: FiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <select
        value={timeWindow}
        onChange={(e) => onTimeWindowChange(Number(e.target.value) as TimeWindow)}
        className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none"
      >
        {TIME_WINDOW_OPTIONS.map((tw) => (
          <option key={tw} value={tw}>
            Last {tw} days
          </option>
        ))}
      </select>

      <select
        value={signalType}
        onChange={(e) =>
          onSignalTypeChange(e.target.value as SignalType | "all")
        }
        className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none"
      >
        <option value="all">All Signal Types</option>
        {FILTERABLE_TYPES.map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>

      <div className="ml-auto flex rounded-md border border-gray-300">
        <button
          onClick={() => onViewTypeChange("grid")}
          className={`px-2.5 py-1.5 ${
            viewType === "grid"
              ? "bg-blue-100 text-blue-700"
              : "bg-white text-gray-400 hover:text-gray-600"
          }`}
          title="Grid view"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="1" y="1" width="6" height="6" rx="1" />
            <rect x="9" y="1" width="6" height="6" rx="1" />
            <rect x="1" y="9" width="6" height="6" rx="1" />
            <rect x="9" y="9" width="6" height="6" rx="1" />
          </svg>
        </button>
        <button
          onClick={() => onViewTypeChange("list")}
          className={`border-l border-gray-300 px-2.5 py-1.5 ${
            viewType === "list"
              ? "bg-blue-100 text-blue-700"
              : "bg-white text-gray-400 hover:text-gray-600"
          }`}
          title="List view"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="1" y="2" width="14" height="2.5" rx="0.5" />
            <rect x="1" y="6.75" width="14" height="2.5" rx="0.5" />
            <rect x="1" y="11.5" width="14" height="2.5" rx="0.5" />
          </svg>
        </button>
      </div>
    </div>
  );
}
