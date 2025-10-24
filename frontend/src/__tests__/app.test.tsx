import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import { AuthContext } from "../context/AuthContext";
import App from "../routes/App";
import type { User } from "../types/api";

const demoUser: User = {
  id: "123",
  email: "teacher@example.edu",
  full_name: "Taylor Teacher",
  avatar_url: null,
  locale: "en-US",
  preferred_subjects: ["Science"],
  preferred_grade_levels: ["5"],
  is_active: true,
  is_superuser: false,
  roles: [{ role: "teacher", scope: {} }]
};

const renderWithProviders = (route: string, authState: { status: "loading" | "authenticated" | "unauthenticated"; user: User | null }) => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          ...authState,
          refresh: vi.fn().mockResolvedValue(undefined),
          logout: vi.fn().mockResolvedValue(undefined)
        }}
      >
        <MemoryRouter initialEntries={[route]}>
          <App />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
};

describe("App routing", () => {
  it("renders dashboard when authenticated", () => {
    renderWithProviders("/", { status: "authenticated", user: demoUser });

    expect(screen.getByText(/LessonGen activity/i)).toBeInTheDocument();
  });

  it("redirects unauthenticated users to the login page", () => {
    renderWithProviders("/dashboard", { status: "unauthenticated", user: null });

    expect(screen.getByText(/Continue with Google/i)).toBeInTheDocument();
  });

  it("shows lessons page when authenticated", () => {
    renderWithProviders("/lessons", { status: "authenticated", user: demoUser });

    expect(screen.getByRole("heading", { name: /Lessons/i })).toBeInTheDocument();
  });
});
