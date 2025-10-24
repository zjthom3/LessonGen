import { apiClient } from "./client";
import type { AnalyticsSummary } from "../types/api";

export const fetchAnalyticsSummary = async (days = 30): Promise<AnalyticsSummary> => {
  const { data } = await apiClient.get<AnalyticsSummary>("/analytics/summary", {
    params: { days }
  });
  return data;
};
