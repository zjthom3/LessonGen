import { Suspense } from "react";
import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import AppLayout from "../components/AppLayout";
import { useAuth } from "../context/AuthContext";
import DashboardPage from "../pages/DashboardPage";
import LessonsPage from "../pages/LessonsPage";
import LoginPage from "../pages/LoginPage";
import ProfilePage from "../pages/ProfilePage";
import LessonDetailPage from "../pages/LessonDetailPage";

const RequireAuth = () => {
  const { status, user } = useAuth();

  if (status === "loading") {
    return <div className="p-8 text-gray-600">Verifying session…</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

const App = () => {
  const { status, user } = useAuth();

  if (status === "loading") {
    return <div className="p-8 text-gray-600">Checking your session…</div>;
  }

  return (
    <Suspense fallback={<div className="p-8 text-gray-600">Loading…</div>}>
      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/lessons" element={<LessonsPage />} />
            <Route path="/lessons/:lessonId" element={<LessonDetailPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<div className="p-8">Page not found.</div>} />
      </Routes>
    </Suspense>
  );
};

export default App;
