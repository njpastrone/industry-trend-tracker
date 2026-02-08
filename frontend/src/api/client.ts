import axios from "axios";
import type { InitData, PipelineRunResult, SectorDetailResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export async function getInitData(days: number): Promise<InitData> {
  const { data } = await api.get<InitData>("/api/init", { params: { days } });
  return data;
}

export async function getSectorDetail(
  sectorId: string,
  days: number,
  signalType?: string,
): Promise<SectorDetailResponse> {
  const params: Record<string, string | number> = { days };
  if (signalType && signalType !== "all") params.signal_type = signalType;
  const { data } = await api.get<SectorDetailResponse>(
    `/api/sectors/${sectorId}`,
    { params },
  );
  return data;
}

export async function runPipeline(): Promise<PipelineRunResult> {
  const { data } = await api.post<PipelineRunResult>("/api/pipeline/run");
  return data;
}

export async function refreshFinancials(): Promise<{ financials_updated: number }> {
  const { data } = await api.post<{ financials_updated: number }>(
    "/api/pipeline/financials"
  );
  return data;
}

export async function getSignalTypes(): Promise<Record<string, string>> {
  const { data } = await api.get<Record<string, string>>(
    "/api/config/signal-types"
  );
  return data;
}
