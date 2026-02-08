import {
  TIME_WINDOW_OPTIONS,
  SIGNAL_TYPE_LABELS,
  type TimeWindow,
  type SignalType,
} from "../types";

const FILTERABLE_TYPES = Object.entries(SIGNAL_TYPE_LABELS).filter(
  ([key]) => key !== "neutral"
) as [SignalType, string][];

interface FiltersProps {
  timeWindow: TimeWindow;
  onTimeWindowChange: (tw: TimeWindow) => void;
  signalType: SignalType | "all";
  onSignalTypeChange: (st: SignalType | "all") => void;
}

export default function Filters({
  timeWindow,
  onTimeWindowChange,
  signalType,
  onSignalTypeChange,
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
    </div>
  );
}
