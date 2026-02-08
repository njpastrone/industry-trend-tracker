import type { Signal } from "../types";
import SignalCard from "./SignalCard";

interface Props {
  signals: Signal[];
}

export default function SignalFeed({ signals }: Props) {
  if (signals.length === 0) {
    return (
      <div className="rounded-lg border border-blue-100 bg-white p-8 text-center text-sm text-gray-500">
        No signals found for the selected filters.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {signals.map((signal) => (
        <SignalCard key={signal.id} signal={signal} />
      ))}
    </div>
  );
}
