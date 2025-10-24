import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useCreateLesson, useLessons } from "../hooks/useLessons";
import type { LessonSummary } from "../types/api";

interface FilterState {
  subject: string;
  grade_level: string;
  tags: string;
}

interface LessonFormState {
  title: string;
  subject: string;
  grade_level: string;
  language: string;
  tags: string;
  objective: string;
}

const defaultFilters: FilterState = {
  subject: "",
  grade_level: "",
  tags: ""
};

const defaultForm: LessonFormState = {
  title: "",
  subject: "",
  grade_level: "",
  language: "en",
  tags: "",
  objective: ""
};

const LessonsPage = () => {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [formState, setFormState] = useState<LessonFormState>(defaultForm);
  const [showForm, setShowForm] = useState(false);

  const lessonFilters = useMemo(() => {
    return {
      subject: filters.subject || undefined,
      grade_level: filters.grade_level || undefined,
      tags: filters.tags
        ? filters.tags
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean)
        : undefined
    };
  }, [filters]);

  const { data: lessons = [], isLoading } = useLessons(lessonFilters);
  const createLessonMutation = useCreateLesson();

  const handleFilterSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setFilters({
      subject: (formData.get("subject") as string) ?? "",
      grade_level: (formData.get("grade_level") as string) ?? "",
      tags: (formData.get("tags") as string) ?? ""
    });
  };

  const handleLessonSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await createLessonMutation.mutateAsync({
      title: formState.title,
      subject: formState.subject,
      grade_level: formState.grade_level,
      language: formState.language,
      tags: formState.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      objective: formState.objective
    });
    setShowForm(false);
    setFormState(defaultForm);
  };

  const handleFormChange = (field: keyof LessonFormState, value: string) => {
    setFormState((previous) => ({ ...previous, [field]: value }));
  };

  const renderLessonCard = (lesson: LessonSummary) => {
    return (
      <article
        key={lesson.id}
        className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{lesson.title}</h2>
            <p className="text-sm text-slate-600">
              Grade {lesson.grade_level} · {lesson.subject}
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
            {lesson.status}
          </span>
        </div>
        {lesson.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 text-xs text-slate-500">
            {lesson.tags.map((tag) => (
              <span key={`${lesson.id}-${tag}`} className="rounded bg-slate-100 px-2 py-1">
                {tag}
              </span>
            ))}
          </div>
        )}
        <div className="mt-auto flex items-center justify-between text-sm text-slate-500">
          <span>Updated {new Date(lesson.updated_at).toLocaleDateString()}</span>
          <Link
            to={`/lessons/${lesson.id}`}
            className="text-sm font-medium text-brand hover:text-brand-dark"
          >
            View
          </Link>
        </div>
      </article>
    );
  };

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">Lessons</h1>
          <p className="text-slate-600">
            Browse your saved lessons, filter by subject or grade, and jump back into editing.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowForm((visible) => !visible)}
          className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark"
        >
          {showForm ? "Cancel" : "Create lesson"}
        </button>
      </header>

      <form
        onSubmit={handleFilterSubmit}
        className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-end"
      >
        <label className="flex flex-col text-sm font-medium text-slate-700">
          Subject
          <input
            name="subject"
            defaultValue={filters.subject}
            className="mt-1 rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            placeholder="e.g. Science"
          />
        </label>
        <label className="flex flex-col text-sm font-medium text-slate-700">
          Grade level
          <input
            name="grade_level"
            defaultValue={filters.grade_level}
            className="mt-1 rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            placeholder="e.g. 5"
          />
        </label>
        <label className="flex flex-col text-sm font-medium text-slate-700">
          Tags
          <input
            name="tags"
            defaultValue={filters.tags}
            className="mt-1 rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            placeholder="comma separated"
          />
        </label>
        <button
          type="submit"
          className="rounded bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-900"
        >
          Apply
        </button>
      </form>

      {showForm && (
        <form
          onSubmit={handleLessonSubmit}
          className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm font-medium text-slate-700">
              Title
              <input
                value={formState.title}
                onChange={(event) => handleFormChange("title", event.target.value)}
                required
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              />
            </label>
            <label className="text-sm font-medium text-slate-700">
              Subject
              <input
                value={formState.subject}
                onChange={(event) => handleFormChange("subject", event.target.value)}
                required
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              />
            </label>
            <label className="text-sm font-medium text-slate-700">
              Grade level
              <input
                value={formState.grade_level}
                onChange={(event) => handleFormChange("grade_level", event.target.value)}
                required
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              />
            </label>
            <label className="text-sm font-medium text-slate-700">
              Tags
              <input
                value={formState.tags}
                onChange={(event) => handleFormChange("tags", event.target.value)}
                placeholder="project-based, inquiry"
                className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              />
            </label>
          </div>
          <label className="text-sm font-medium text-slate-700">
            Objective
            <textarea
              value={formState.objective}
              onChange={(event) => handleFormChange("objective", event.target.value)}
              rows={3}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
              placeholder="Students will..."
            />
          </label>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={createLessonMutation.isPending}
              className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-70"
            >
              {createLessonMutation.isPending ? "Creating..." : "Save lesson"}
            </button>
            {createLessonMutation.isError && (
              <span className="text-sm text-red-600">Unable to create lesson. Try again.</span>
            )}
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500">
          Loading lessons…
        </div>
      ) : lessons.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500">
          No lessons found. Try adjusting your filters or create a new lesson.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">{lessons.map(renderLessonCard)}</div>
      )}
    </section>
  );
};

export default LessonsPage;
