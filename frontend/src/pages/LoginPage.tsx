import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-light to-brand-dark">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-2xl font-semibold text-slate-900">Sign in to LessonGen</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            Email address
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              placeholder="you@example.com"
              required
            />
          </label>
          <button
            type="submit"
            className="w-full rounded bg-brand px-4 py-2 font-semibold text-white shadow hover:bg-brand-dark"
          >
            Continue with Email
          </button>
          <p className="text-xs text-slate-500">
            Google OAuth will arrive in Sprint 2. For now this placeholder demonstrates routing.
          </p>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
