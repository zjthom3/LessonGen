import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import LessonsPage from "../pages/LessonsPage";
import type { LessonSummary } from "../types/api";

vi.mock("../hooks/useLessons", () => {
  return {
    useLessons: vi.fn(),
    useCreateLesson: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false, isError: false }))
  };
});

const { useLessons } = await import("../hooks/useLessons");

const renderLessonsPage = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <LessonsPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("LessonsPage", () => {
  it("renders lessons from the API", () => {
    const mockLessons: LessonSummary[] = [
      {
        id: "1",
        title: "Solar System",
        subject: "Science",
        grade_level: "5",
        language: "en",
        status: "draft",
        tags: ["space"],
        visibility: "private",
        current_version_id: "v1",
        updated_at: new Date().toISOString()
      }
    ];

    (useLessons as unknown as vi.Mock).mockReturnValue({ data: mockLessons, isLoading: false });

    renderLessonsPage();

    expect(screen.getByText(/Solar System/)).toBeInTheDocument();
    expect(screen.getByText(/Grade 5/)).toBeInTheDocument();
  });

  it("toggles the create lesson form", () => {
    (useLessons as unknown as vi.Mock).mockReturnValue({ data: [], isLoading: false });

    renderLessonsPage();

    const toggleButton = screen.getByRole("button", { name: /Create lesson/i });
    fireEvent.click(toggleButton);
    expect(screen.getByText(/Save lesson/i)).toBeInTheDocument();
  });
});
