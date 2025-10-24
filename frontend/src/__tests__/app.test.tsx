import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import App from "../routes/App";

describe("App routing", () => {
  it("renders dashboard by default", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/Welcome back/i)).toBeInTheDocument();
  });

  it("navigates to lessons page", () => {
    render(
      <MemoryRouter initialEntries={["/lessons"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/Lessons/i)).toBeInTheDocument();
  });
});
