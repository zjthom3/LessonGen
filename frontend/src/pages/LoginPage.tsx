import { useState } from "react";

import { requestLoginUrl } from "../api/auth";
import { useAuth } from "../context/AuthContext";

const LoginPage = () => {
  const { status } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleSignIn = async () => {
    try {
      setError(null);
      setIsRedirecting(true);
      const url = await requestLoginUrl();
      window.location.href = url;
    } catch (err) {
      console.error(err);
      setError("Unable to start Google sign-in. Please try again.");
      setIsRedirecting(false);
    }
  };

  const isLoading = status === "loading" || isRedirecting;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-light to-brand-dark">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-2xl font-semibold text-slate-900">Sign in to LessonGen</h1>
        <p className="mb-4 text-sm text-slate-600">
          Use your district Google account to access LessonGen&apos;s lesson generation tools.
        </p>
        <button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={isLoading}
          className="flex w-full items-center justify-center gap-2 rounded bg-brand px-4 py-2 font-semibold text-white shadow transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-70"
        >
          <span className="inline-block">
            {isLoading ? "Redirecting to Google…" : "Continue with Google"}
          </span>
        </button>
        {error && <p className="mt-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
        <p className="mt-6 text-xs text-slate-500">
          We use OAuth 2.0 for secure sign-in. By continuing, you agree to our acceptable use policy.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
