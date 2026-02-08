import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { isAxiosError } from "axios";
import { getSectorDetail } from "../api/client";
import type { TimeWindow, SignalType } from "../types";
import { TIME_WINDOW_OPTIONS } from "../types";
import SectorHeader from "../components/SectorHeader";
import NarrativeBlock from "../components/NarrativeBlock";
import SignalTypeTabs from "../components/SignalTypeTabs";
import SignalFeed from "../components/SignalFeed";

function DetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header stats skeleton */}
      <div className="animate-pulse rounded-lg border border-blue-100 bg-white p-5">
        <div className="mb-4">
          <div className="mb-1 h-5 w-40 rounded bg-gray-200" />
          <div className="h-4 w-16 rounded bg-gray-100" />
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i}>
              <div className="mb-1 h-3 w-16 rounded bg-gray-100" />
              <div className="h-6 w-20 rounded bg-gray-200" />
            </div>
          ))}
        </div>
      </div>

      {/* Narrative skeleton */}
      <div className="animate-pulse rounded-lg border border-blue-100 bg-white p-5">
        <div className="mb-3 h-4 w-24 rounded bg-gray-200" />
        <div className="mb-3 flex gap-2">
          <div className="h-5 w-20 rounded-full bg-blue-50" />
          <div className="h-5 w-24 rounded-full bg-blue-50" />
          <div className="h-5 w-16 rounded-full bg-blue-50" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-full rounded bg-gray-100" />
          <div className="h-4 w-full rounded bg-gray-100" />
          <div className="h-4 w-3/4 rounded bg-gray-100" />
        </div>
      </div>

      {/* Signal cards skeleton */}
      {Array.from({ length: 3 }).map((_, i) => (
        <div
          key={i}
          className="animate-pulse rounded-lg border border-blue-100 bg-white p-4"
        >
          <div className="mb-2 h-4 w-3/4 rounded bg-gray-200" />
          <div className="mb-2 flex gap-2">
            <div className="h-4 w-16 rounded bg-gray-100" />
            <div className="h-4 w-12 rounded bg-gray-100" />
            <div className="h-4 w-20 rounded-full bg-gray-100" />
          </div>
          <div className="h-4 w-full rounded bg-gray-100" />
          <div className="mt-1 h-4 w-2/3 rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}

export default function SectorDetail() {
  const { sectorId } = useParams();

  const [timeWindow, setTimeWindow] = useState<TimeWindow>(() => {
    const stored = localStorage.getItem("timeWindow");
    const parsed = stored ? Number(stored) : 7;
    return parsed === 7 || parsed === 14 || parsed === 30 ? parsed : 7;
  });

  const [signalTypeFilter, setSignalTypeFilter] = useState<
    SignalType | "all"
  >("all");

  // Reset filter when time window changes
  useEffect(() => {
    setSignalTypeFilter("all");
  }, [timeWindow]);

  // Persist time window
  useEffect(() => {
    localStorage.setItem("timeWindow", String(timeWindow));
  }, [timeWindow]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["sectorDetail", sectorId, timeWindow, signalTypeFilter],
    queryFn: () => getSectorDetail(sectorId!, timeWindow, signalTypeFilter),
    staleTime: 5 * 60 * 1000,
    enabled: !!sectorId,
    retry: (failureCount, err) => {
      if (isAxiosError(err) && err.response?.status === 404) return false;
      return failureCount < 2;
    },
  });

  const is404 = isError && isAxiosError(error) && error.response?.status === 404;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-700 px-6 py-5 text-white">
        <div className="mx-auto max-w-7xl">
          <Link to="/" className="text-sm text-blue-200 hover:text-white">
            &larr; Back to Dashboard
          </Link>
          <h1 className="mt-2 text-2xl font-bold">
            {data?.sector.name ?? "Sector Detail"}
          </h1>
          {data?.sector.etf_ticker && (
            <span className="text-sm text-blue-200">
              {data.sector.etf_ticker}
            </span>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-6">
        {isLoading && <DetailSkeleton />}

        {isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-700">
            {is404
              ? "Sector not found."
              : "Failed to load sector data. Is the backend running?"}
          </div>
        )}

        {data && (
          <div className="space-y-6">
            <SectorHeader
              sector={data.sector}
              financials={data.financials}
            />

            <NarrativeBlock narrative={data.narrative} />

            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-700">
                Time window
              </label>
              <select
                value={timeWindow}
                onChange={(e) =>
                  setTimeWindow(Number(e.target.value) as TimeWindow)
                }
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
              >
                {TIME_WINDOW_OPTIONS.map((w) => (
                  <option key={w} value={w}>
                    {w} days
                  </option>
                ))}
              </select>
            </div>

            <SignalTypeTabs
              countsByType={data.signal_counts_by_type}
              activeType={signalTypeFilter}
              onTypeChange={setSignalTypeFilter}
            />

            <SignalFeed signals={data.signals} />
          </div>
        )}
      </main>
    </div>
  );
}
