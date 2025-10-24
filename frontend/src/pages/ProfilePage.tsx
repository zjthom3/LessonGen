import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateProfile } from "../api/profile";
import { useAuth } from "../context/AuthContext";
import type { UpdateProfilePayload, User } from "../types/api";

const toInputString = (values: string[]) => values.join(", ");

const parseList = (value: string): string[] =>
  value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

const ProfilePage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [subjectsInput, setSubjectsInput] = useState(toInputString(user?.preferred_subjects ?? []));
  const [gradesInput, setGradesInput] = useState(
    toInputString(user?.preferred_grade_levels ?? [])
  );
  const [feedback, setFeedback] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: UpdateProfilePayload) => updateProfile(payload),
    onSuccess: (updated: User) => {
      queryClient.setQueryData(["auth", "session"], updated);
      setFeedback("Profile updated successfully.");
    },
    onError: () => {
      setFeedback("Failed to update your profile. Please try again.");
    }
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFeedback(null);

    const payload: UpdateProfilePayload = {
      full_name: fullName || null,
      preferred_subjects: parseList(subjectsInput),
      preferred_grade_levels: parseList(gradesInput),
      locale: user?.locale ?? "en-US"
    };

    mutation.mutate(payload);
  };

  const currentRole = useMemo(() => user?.roles?.[0]?.role ?? "teacher", [user]);

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Your Profile</h1>
        <p className="text-slate-600">
          Update your preferences so LessonGen can personalise lesson suggestions.
        </p>
      </header>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Full name
              <input
                type="text"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
                placeholder="Taylor Teacher"
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm font-medium text-slate-700">
              Preferred subjects
              <input
                type="text"
                value={subjectsInput}
                onChange={(event) => setSubjectsInput(event.target.value)}
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
                placeholder="Science, Math"
              />
              <span className="mt-1 block text-xs text-slate-500">
                Comma-separated list (e.g., Science, Math)
              </span>
            </label>

            <label className="block text-sm font-medium text-slate-700">
              Preferred grades
              <input
                type="text"
                value={gradesInput}
                onChange={(event) => setGradesInput(event.target.value)}
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
                placeholder="5, 6"
              />
              <span className="mt-1 block text-xs text-slate-500">
                Comma-separated grade levels (e.g., 4, 5, 6)
              </span>
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Email</p>
              <p className="mt-1 text-sm text-slate-700">{user?.email}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Role</p>
              <p className="mt-1 text-sm capitalize text-slate-700">{currentRole}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Locale
              </p>
              <p className="mt-1 text-sm text-slate-700">{user?.locale ?? "en-US"}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded bg-brand px-4 py-2 font-semibold text-white shadow transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-70"
            >
              {mutation.isPending ? "Saving…" : "Save changes"}
            </button>
            {feedback && <p className="text-sm text-slate-600">{feedback}</p>}
          </div>
        </form>
      </div>
    </section>
  );
};

export default ProfilePage;
