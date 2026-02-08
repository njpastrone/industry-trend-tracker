import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getInitData, runPipeline } from "../api/client";
import type { TimeWindow, SignalType } from "../types";
import SectorGrid from "../components/SectorGrid";
import Filters from "../components/Filters";
import { formatRelativeTime } from "../utils/format";

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 11 }).map((_, i) => (
        <div
          key={i}
          className="animate-pulse rounded-lg border border-blue-100 bg-white p-5"
        >
          <div className="mb-3 flex items-start justify-between">
            <div>
              <div className="mb-1 h-5 w-32 rounded bg-gray-200" />
              <div className="h-4 w-12 rounded bg-gray-100" />
            </div>
            <div className="h-6 w-16 rounded bg-gray-200" />
          </div>
          <div className="mb-3 flex gap-3">
            <div className="h-5 w-20 rounded-full bg-blue-50" />
            <div className="h-5 w-16 rounded bg-gray-100" />
          </div>
          <div className="h-4 w-full rounded bg-gray-100" />
          <div className="mt-1 h-4 w-3/4 rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const queryClient = useQueryClient();

  const [timeWindow, setTimeWindow] = useState<TimeWindow>(() => {
    const stored = localStorage.getItem("timeWindow");
    const parsed = stored ? Number(stored) : 7;
    return parsed === 7 || parsed === 14 || parsed === 30 ? parsed : 7;
  });

  const [signalType, setSignalType] = useState<SignalType | "all">(() => {
    return (localStorage.getItem("signalType") as SignalType | "all") || "all";
  });

  useEffect(() => {
    localStorage.setItem("timeWindow", String(timeWindow));
  }, [timeWindow]);

  useEffect(() => {
    localStorage.setItem("signalType", signalType);
  }, [signalType]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["initData", timeWindow],
    queryFn: () => getInitData(timeWindow),
    staleTime: 5 * 60 * 1000,
  });

  const pipelineMutation = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: ["initData"] });
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-700 px-6 py-5 text-white">
        <div className="mx-auto max-w-7xl">
          <h1 className="text-2xl font-bold">Industry Intelligence Tracker</h1>
          <p className="mt-1 text-sm text-blue-200">
            Macro sector trends for IR professionals
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <span className="text-sm text-blue-200">
              Last updated: {formatRelativeTime(data?.last_pipeline_run ?? null)}
            </span>
            <button
              onClick={() => pipelineMutation.mutate()}
              disabled={pipelineMutation.isPending}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
            >
              {pipelineMutation.isPending ? "Running..." : "Refresh Data"}
            </button>
            {pipelineMutation.isSuccess && (
              <span className="text-sm text-green-300">
                Pipeline completed in{" "}
                {pipelineMutation.data.elapsed_seconds}s
              </span>
            )}
            {pipelineMutation.isError && (
              <span className="text-sm text-red-300">Pipeline failed</span>
            )}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-7xl px-6 py-6">
        <div className="mb-5">
          <Filters
            timeWindow={timeWindow}
            onTimeWindowChange={setTimeWindow}
            signalType={signalType}
            onSignalTypeChange={setSignalType}
          />
        </div>

        {isLoading && <SkeletonGrid />}

        {isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-700">
            Failed to load dashboard data. Is the backend running?
          </div>
        )}

        {data && <SectorGrid sectors={data.sectors} />}
      </main>
    </div>
  );
}
