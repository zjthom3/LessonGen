import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { vi } from "vitest";

import DashboardPage from "../pages/DashboardPage";
import type { AnalyticsSummary } from "../types/api";

vi.mock("../hooks/useAnalytics", () => ({
  useAnalyticsSummary: vi.fn()
}));

const { useAnalyticsSummary } = await import("../hooks/useAnalytics");

const renderDashboard = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>
  );
};

describe("DashboardPage", () => {
  it("renders analytics metrics when data is available", () => {
    const summary: AnalyticsSummary = {
      lessons_created: 8,
      lessons_generated: 5,
      lessons_differentiated: 3,
      exports: 2,
      lms_pushes: 1,
      total_lessons: 12,
      estimated_time_saved_minutes: 150
    };

    (useAnalyticsSummary as unknown as vi.Mock).mockReturnValue({
      data: summary,
      isLoading: false,
      isError: false
    });

    renderDashboard();

    expect(screen.getByText(/Lessons created/)).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText(/Time saved/)).toBeInTheDocument();
  });

  it("shows loading skeleton while fetching data", () => {
    (useAnalyticsSummary as unknown as vi.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false
    });

    const { container } = renderDashboard();
    expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });
});
