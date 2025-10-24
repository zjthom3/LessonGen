import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  useCreateLessonVersion,
  useCreateLessonShare,
  useDifferentiateLesson,
  useLesson,
  useRestoreLessonVersion
} from "../hooks/useLessons";
import { useConnectGoogleClassroom, usePushGoogleClassroom } from "../hooks/useGoogleClassroom";
import { downloadLessonExport, fetchGDocExport } from "../api/lessons";
import type { DifferentiationAudience, ShareCreateResponse } from "../types/api";

interface VersionFormState {
  objective: string;
  teacher_script_md: string;
  status: string;
}

const defaultVersionForm: VersionFormState = {
  objective: "",
  teacher_script_md: "",
  status: "draft"
};

const LessonDetailPage = () => {
  const { lessonId = "" } = useParams();
  const navigate = useNavigate();
  const { data: lesson, isLoading, isError } = useLesson(lessonId);
  const createVersion = useCreateLessonVersion(lessonId);
  const restoreVersion = useRestoreLessonVersion(lessonId);
  const differentiateLesson = useDifferentiateLesson(lessonId);
  const createShare = useCreateLessonShare(lessonId);
  const connectClassroom = useConnectGoogleClassroom();
  const pushClassroom = usePushGoogleClassroom(lessonId);
  const [formState, setFormState] = useState<VersionFormState>(defaultVersionForm);
  const [exporting, setExporting] = useState<"pdf" | "docx" | "gdoc" | null>(null);
  const [pushForm, setPushForm] = useState({ courseId: "", topicId: "", dueDate: "" });
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  const [diffForm, setDiffForm] = useState<{ audience: DifferentiationAudience; notes: string }>({
    audience: "ELL",
    notes: ""
  });
  const [diffNotice, setDiffNotice] = useState<{ type: "success" | "error"; message: string } | null>(
    null
  );
  const [shareForm, setShareForm] = useState<{ expiresInHours: string }>({
    expiresInHours: "72"
  });
  const [shareResult, setShareResult] = useState<ShareCreateResponse | null>(null);
  const [shareError, setShareError] = useState<string | null>(null);

  const currentVersionId = lesson?.current_version_id ?? null;

  const sortedVersions = useMemo(() => {
    if (!lesson) {
      return [];
    }
    return [...lesson.versions].sort((a, b) => b.version_no - a.version_no);
  }, [lesson]);

  const handleVersionSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await createVersion.mutateAsync({
      objective: formState.objective || undefined,
      teacher_script_md: formState.teacher_script_md || undefined,
      status: formState.status || undefined
    });
    setFormState(defaultVersionForm);
  };

  const handleDifferentiateSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setDiffNotice(null);
    try {
      await differentiateLesson.mutateAsync({
        audience: diffForm.audience,
        notes: diffForm.notes.trim() ? diffForm.notes.trim() : undefined
      });
      setDiffNotice({
        type: "success",
        message: `Created ${diffForm.audience} differentiated version.`
      });
      setDiffForm((previous) => ({ ...previous, notes: "" }));
    } catch (error) {
      console.error(error);
      setDiffNotice({
        type: "error",
        message: "Unable to create a differentiated version. Please try again."
      });
    }
  };

  const handleRestore = async (versionNo: number) => {
    await restoreVersion.mutateAsync(versionNo);
  };

  const handleExport = async (format: "pdf" | "docx" | "gdoc") => {
    if (!lessonId) return;
    try {
      setExporting(format);
      setExportMessage(null);
      if (format === "gdoc") {
        const data = await fetchGDocExport(lessonId);
        setExportMessage(`GDoc export ready: ${data.title}`);
      } else {
        const blob = await downloadLessonExport(lessonId, format);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${lesson?.title ?? "lesson"}.${format}`;
        link.click();
        window.URL.revokeObjectURL(url);
        setExportMessage(`Downloaded ${format.toUpperCase()} export.`);
      }
    } catch (error) {
      console.error(error);
      setExportMessage("Export failed. Please try again.");
    } finally {
      setExporting(null);
    }
  };

  const handleConnectClassroom = async () => {
    await connectClassroom.mutateAsync();
  };

  const handlePushClassroom = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await pushClassroom.mutateAsync({
      courseId: pushForm.courseId,
      topicId: pushForm.topicId || undefined,
      dueDate: pushForm.dueDate || undefined
    });
    setPushForm({ courseId: "", topicId: "", dueDate: "" });
  };

  const handleShareSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setShareError(null);
    try {
      const expiresInput = shareForm.expiresInHours.trim();
      const expiresIn = expiresInput === "" ? undefined : Number(expiresInput);
      if (typeof expiresIn === "number" && (!Number.isFinite(expiresIn) || expiresIn < 1)) {
        setShareError("Expiration must be a positive number of hours or left blank.");
        return;
      }
      const result = await createShare.mutateAsync({ expires_in_hours: expiresIn });
      setShareResult(result);
      setShareError(null);
    } catch (error) {
      console.error(error);
      setShareResult(null);
      setShareError("Unable to generate share link. Please try again.");
    }
  };

  if (isLoading) {
    return <div className="p-6 text-sm text-slate-500">Loading lesson…</div>;
  }

  if (isError || !lesson) {
    return (
      <div className="space-y-4 p-6 text-sm text-slate-500">
        <p>Unable to load this lesson.</p>
        <button
          type="button"
          className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark"
          onClick={() => navigate(-1)}
        >
          Go back
        </button>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <Link to="/lessons" className="text-sm font-medium text-brand hover:text-brand-dark">
          ← Back to lessons
        </Link>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-slate-900">{lesson.title}</h1>
            <p className="text-slate-600">
              Grade {lesson.grade_level} · {lesson.subject}
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
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
      </header>

      <form
        onSubmit={handleVersionSubmit}
        className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold text-slate-900">Create new version</h2>
        <label className="text-sm font-medium text-slate-700">
          Objective
          <textarea
            value={formState.objective}
            onChange={(event) => setFormState((prev) => ({ ...prev, objective: event.target.value }))}
            rows={3}
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
            placeholder="Students will..."
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Teacher notes (Markdown)
          <textarea
            value={formState.teacher_script_md}
            onChange={(event) =>
              setFormState((prev) => ({ ...prev, teacher_script_md: event.target.value }))
            }
            rows={6}
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 font-mono text-sm focus:border-brand focus:outline-none"
            placeholder="### Introduction\nShare the warm-up prompt..."
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Status
          <select
            value={formState.status}
            onChange={(event) => setFormState((prev) => ({ ...prev, status: event.target.value }))}
            className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </label>
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={createVersion.isPending}
            className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-70"
          >
            {createVersion.isPending ? "Saving…" : "Save version"}
          </button>
          {createVersion.isError && (
            <span className="text-sm text-red-600">Failed to save version. Try again.</span>
          )}
        </div>
      </form>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Differentiate lesson</h2>
        <form className="space-y-3" onSubmit={handleDifferentiateSubmit}>
          <label className="text-sm font-medium text-slate-700">
            Audience
            <select
              value={diffForm.audience}
              onChange={(event) =>
                setDiffForm((previous) => ({
                  ...previous,
                  audience: event.target.value as DifferentiationAudience
                }))
              }
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            >
              <option value="ELL">English language learners</option>
              <option value="IEP">Students with IEPs</option>
              <option value="GIFTED">Advanced/Gifted students</option>
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700">
            Notes (optional)
            <textarea
              value={diffForm.notes}
              onChange={(event) =>
                setDiffForm((previous) => ({ ...previous, notes: event.target.value }))
              }
              rows={3}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
              placeholder="Add context about the student's needs or focus areas."
            />
          </label>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={differentiateLesson.isPending}
              className="rounded bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {differentiateLesson.isPending ? "Creating…" : "Create differentiated version"}
            </button>
            {diffNotice && (
              <span
                className={`text-sm ${diffNotice.type === "success" ? "text-green-600" : "text-red-600"}`}
              >
                {diffNotice.message}
              </span>
            )}
          </div>
        </form>
      </section>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Share lesson</h2>
        <p className="text-sm text-slate-600">
          Generate a read-only link to share the latest version with colleagues or administrators.
        </p>
        <form className="flex flex-col gap-3 md:flex-row md:items-end" onSubmit={handleShareSubmit}>
          <label className="flex flex-1 flex-col text-sm font-medium text-slate-700">
            Expires in (hours)
            <input
              type="number"
              min={1}
              placeholder="72"
              value={shareForm.expiresInHours}
              onChange={(event) => setShareForm({ expiresInHours: event.target.value })}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            />
            <span className="mt-1 text-xs text-slate-500">Leave blank for no expiration.</span>
          </label>
          <button
            type="submit"
            disabled={createShare.isPending}
            className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60"
          >
            {createShare.isPending ? "Generating…" : "Generate link"}
          </button>
        </form>
        {shareError && <p className="text-sm text-red-600">{shareError}</p>}
        {shareResult && (
          <div className="rounded border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            <p className="break-words">
              <span className="font-medium text-slate-800">Share URL:</span>
              <a
                href={shareResult.url}
                target="_blank"
                rel="noreferrer"
                className="ml-2 break-words text-brand hover:text-brand-dark"
              >
                {shareResult.url}
              </a>
            </p>
            {shareResult.expires_at && (
              <p className="mt-2 text-xs text-slate-500">
                Expires {new Date(shareResult.expires_at).toLocaleString()}
              </p>
            )}
          </div>
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Version history</h2>
        <div className="space-y-3">
          {sortedVersions.map((version) => {
            const isCurrent = currentVersionId === version.id;
            return (
              <article
                key={version.id}
                className={`rounded-lg border p-4 shadow-sm ${
                  isCurrent ? "border-brand-light bg-brand-light/20" : "border-slate-200 bg-white"
                }`}
              >
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900">Version {version.version_no}</h3>
                    <p className="text-xs text-slate-500">
                      Created {new Date(version.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {isCurrent ? (
                      <span className="rounded bg-brand px-2 py-1 text-xs font-semibold text-white">
                        Current
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleRestore(version.version_no)}
                        className="rounded border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                        disabled={restoreVersion.isPending}
                      >
                        Restore
                      </button>
                    )}
                  </div>
                </div>
                {version.objective && (
                  <p className="mt-3 text-sm text-slate-600">{version.objective}</p>
                )}
                {version.teacher_script_md && (
                  <pre className="mt-3 overflow-x-auto rounded bg-slate-50 p-3 text-sm text-slate-700">
                    {version.teacher_script_md}
                  </pre>
                )}
              </article>
            );
          })}
        </div>
      </section>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Export Lesson</h2>
        <div className="flex flex-wrap gap-2">
          {(["pdf", "docx", "gdoc"] as const).map((format) => (
            <button
              key={format}
              type="button"
              onClick={() => handleExport(format)}
              disabled={exporting === format}
              className="rounded border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-60"
            >
              {exporting === format ? `Exporting ${format.toUpperCase()}…` : format.toUpperCase()}
            </button>
          ))}
        </div>
        {exportMessage && <p className="text-sm text-slate-600">{exportMessage}</p>}
      </section>

      <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Google Classroom</h2>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleConnectClassroom}
            disabled={connectClassroom.isPending}
            className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark disabled:opacity-60"
          >
            {connectClassroom.isPending ? "Connecting…" : "Connect Classroom"}
          </button>
          {connectClassroom.isSuccess && (
            <span className="text-xs font-medium text-green-600">Connected!</span>
          )}
        </div>

        <form className="grid gap-3 md:grid-cols-3" onSubmit={handlePushClassroom}>
          <label className="text-sm font-medium text-slate-700">
            Course ID
            <input
              value={pushForm.courseId}
              onChange={(event) => setPushForm((prev) => ({ ...prev, courseId: event.target.value }))}
              required
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Topic ID
            <input
              value={pushForm.topicId}
              onChange={(event) => setPushForm((prev) => ({ ...prev, topicId: event.target.value }))}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Due Date
            <input
              type="datetime-local"
              value={pushForm.dueDate}
              onChange={(event) => setPushForm((prev) => ({ ...prev, dueDate: event.target.value }))}
              className="mt-1 w-full rounded border border-slate-200 px-3 py-2 focus:border-brand focus:outline-none"
            />
          </label>
          <div className="md:col-span-3 flex items-center gap-3">
            <button
              type="submit"
              disabled={pushClassroom.isPending}
              className="rounded bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-900 disabled:opacity-60"
            >
              {pushClassroom.isPending ? "Posting…" : "Post Assignment"}
            </button>
            {pushClassroom.isSuccess && (
              <span className="text-xs font-medium text-green-600">Assignment posted.</span>
            )}
          </div>
        </form>
      </section>
    </section>
  );
};

export default LessonDetailPage;
