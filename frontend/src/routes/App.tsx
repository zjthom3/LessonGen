import { Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "../components/AppLayout";
import DashboardPage from "../pages/DashboardPage";
import LessonsPage from "../pages/LessonsPage";
import LoginPage from "../pages/LoginPage";

const App = () => {
  return (
    <Suspense fallback={<div className="p-8 text-gray-600">Loading…</div>}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/lessons" element={<LessonsPage />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<div className="p-8">Page not found.</div>} />
      </Routes>
    </Suspense>
  );
};

export default App;
