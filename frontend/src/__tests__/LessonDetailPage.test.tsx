import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi, type Mock } from "vitest";

import LessonDetailPage from "../pages/LessonDetailPage";
import type { LessonDetail } from "../types/api";

vi.mock("../hooks/useLessons", () => {
  return {
    useLesson: vi.fn(),
    useCreateLessonVersion: vi.fn(() => ({
      mutateAsync: vi.fn(),
      isPending: false,
      isError: false
    })),
    useRestoreLessonVersion: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
    useDifferentiateLesson: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false })),
    useCreateLessonShare: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false }))
  };
});

vi.mock("../hooks/useGoogleClassroom", () => {
  return {
    useConnectGoogleClassroom: vi.fn(() => ({
      mutateAsync: vi.fn(),
      isPending: false,
      isSuccess: false
    })),
    usePushGoogleClassroom: vi.fn(() => ({
      mutateAsync: vi.fn(),
      isPending: false,
      isSuccess: false
    }))
  };
});

vi.mock("../api/lessons", () => {
  return {
    downloadLessonExport: vi.fn(async () => new Blob(["mock"], { type: "application/pdf" })),
    fetchGDocExport: vi.fn(async () => ({ status: "ready", title: "Mock" }))
  };
});

const { useLesson, useDifferentiateLesson, useCreateLessonShare } = await import("../hooks/useLessons");
const { downloadLessonExport, fetchGDocExport } = await import("../api/lessons");

URL.createObjectURL = vi.fn(() => "blob:mock");
URL.revokeObjectURL = vi.fn();
HTMLAnchorElement.prototype.click = vi.fn();

type MutationMock = { mutateAsync: Mock; isPending: boolean };
type RenderOverrides = { differentiate?: MutationMock; share?: MutationMock };

const renderLessonDetail = (lesson: LessonDetail | null, overrides: RenderOverrides = {}) => {
  (useLesson as unknown as vi.Mock).mockReturnValue({ data: lesson, isLoading: false, isError: !lesson });

  const differentiateMutation: MutationMock =
    overrides.differentiate ?? {
      mutateAsync: vi.fn().mockResolvedValue({}) as unknown as Mock,
      isPending: false
    };
  const shareMutation: MutationMock =
    overrides.share ?? {
      mutateAsync: vi.fn().mockResolvedValue({}) as unknown as Mock,
      isPending: false
    };

  (useDifferentiateLesson as unknown as vi.Mock).mockReturnValue(differentiateMutation);
  (useCreateLessonShare as unknown as vi.Mock).mockReturnValue(shareMutation);

  const queryClient = new QueryClient();
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );

  return { ...utils, differentiateMutation, shareMutation };
};

describe("LessonDetailPage", () => {
  const baseLesson: LessonDetail = {
    id: "1",
    title: "Solar System",
    subject: "Science",
    grade_level: "5",
    language: "en",
    status: "draft",
    tags: ["space"],
    visibility: "private",
    current_version_id: "v2",
    updated_at: new Date().toISOString(),
    owner_user_id: "user-1",
    versions: [
      {
        id: "v2",
        lesson_id: "1",
        version_no: 2,
        objective: "Refine planet comparison",
        duration_minutes: 45,
        teacher_script_md: "### Script",
        materials: [],
        flow: [],
        differentiation: [],
        assessments: [],
        accommodations: [],
        source: {},
        created_at: new Date().toISOString(),
        created_by_user_id: "user-1"
      },
      {
        id: "v1",
        lesson_id: "1",
        version_no: 1,
        objective: "Introduce planets",
        duration_minutes: 40,
        teacher_script_md: "",
        materials: [],
        flow: [],
        differentiation: [],
        assessments: [],
        accommodations: [],
        source: {},
        created_at: new Date().toISOString(),
        created_by_user_id: "user-1"
      }
    ]
  };

  it("displays lesson details and versions", () => {
    renderLessonDetail(baseLesson);

    expect(screen.getByText(/Solar System/)).toBeInTheDocument();
    expect(screen.getByText(/Version 2/)).toBeInTheDocument();
    expect(screen.getByText(/Version 1/)).toBeInTheDocument();
  });

  it("shows a restore button for non-current versions", () => {
    renderLessonDetail(baseLesson);
    expect(screen.getByRole("button", { name: /Restore/i })).toBeInTheDocument();
  });

  it("renders error state when lesson is missing", () => {
    renderLessonDetail(null);
    expect(screen.getByText(/Unable to load this lesson/i)).toBeInTheDocument();
  });

  it("triggers export when export button clicked", async () => {
    renderLessonDetail(baseLesson);

    const exportButton = screen.getByRole("button", { name: /PDF/i });
    fireEvent.click(exportButton);

    await waitFor(() => expect(downloadLessonExport).toHaveBeenCalled());
  });

  it("submits a differentiation request", async () => {
    const differentiateMock: MutationMock = {
      mutateAsync: vi.fn().mockResolvedValue({}) as unknown as Mock,
      isPending: false
    };

    renderLessonDetail(baseLesson, { differentiate: differentiateMock });

    const notesField = screen.getByLabelText(/Notes \(optional\)/i);
    fireEvent.change(notesField, { target: { value: "Focus on vocabulary scaffolds." } });

    const submitButton = screen.getByRole("button", { name: /Create differentiated version/i });
    fireEvent.click(submitButton);

    await waitFor(() =>
      expect(differentiateMock.mutateAsync).toHaveBeenCalledWith({
        audience: "ELL",
        notes: "Focus on vocabulary scaffolds."
      })
    );

    await waitFor(() =>
      expect(screen.getByText(/Created ELL differentiated version/i)).toBeInTheDocument()
    );
  });

  it("generates and displays a share link", async () => {
    const expiresAt = new Date().toISOString();
    const shareMock: MutationMock = {
      mutateAsync: vi
        .fn()
        .mockResolvedValue({ token: "abc123", url: "https://example.com/share/abc123", expires_at: expiresAt }) as unknown as Mock,
      isPending: false
    };

    renderLessonDetail(baseLesson, { share: shareMock });

    const generateButton = screen.getByRole("button", { name: /Generate link/i });
    fireEvent.click(generateButton);

    await waitFor(() =>
      expect(shareMock.mutateAsync).toHaveBeenCalledWith({ expires_in_hours: 72 })
    );

    await waitFor(() =>
      expect(screen.getByText(/https:\/\/example.com\/share\/abc123/)).toBeInTheDocument()
    );
  });
});
