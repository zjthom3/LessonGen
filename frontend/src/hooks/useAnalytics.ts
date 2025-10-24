import { useQuery } from "@tanstack/react-query";

import { fetchAnalyticsSummary } from "../api/analytics";

const analyticsSummaryKey = (days: number) => ["analytics", "summary", days];

export const useAnalyticsSummary = (days = 30) => {
  return useQuery({
    queryKey: analyticsSummaryKey(days),
    queryFn: () => fetchAnalyticsSummary(days),
    staleTime: 1000 * 60, // 1 minute cache to avoid spamming the API
  });
};
