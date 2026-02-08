import { useMemo } from "react";
import type { SectorWithMetrics } from "../types";
import SectorCard from "./SectorCard";

export default function SectorGrid({
  sectors,
}: {
  sectors: SectorWithMetrics[];
}) {
  const sorted = useMemo(
    () => [...sectors].sort((a, b) => b.signal_count - a.signal_count),
    [sectors]
  );

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {sorted.map((s) => (
        <SectorCard key={s.id} sector={s} />
      ))}
    </div>
  );
}
