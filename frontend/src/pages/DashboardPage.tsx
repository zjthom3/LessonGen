import { useMemo } from "react";

import { useAnalyticsSummary } from "../hooks/useAnalytics";

const numberFormatter = new Intl.NumberFormat();

const DashboardPage = () => {
  const { data, isLoading, isError } = useAnalyticsSummary();

  const summary = data ?? {
    lessons_created: 0,
    lessons_generated: 0,
    lessons_differentiated: 0,
    exports: 0,
    lms_pushes: 0,
    total_lessons: 0,
    estimated_time_saved_minutes: 0
  };

  const timeSavedHours = useMemo(() => {
    return Math.round(summary.estimated_time_saved_minutes / 60);
  }, [summary.estimated_time_saved_minutes]);

  const metricCards = [
    { label: "Lessons created", value: summary.lessons_created },
    { label: "AI-generated lessons", value: summary.lessons_generated },
    { label: "Differentiated versions", value: summary.lessons_differentiated },
    { label: "Exports", value: summary.exports },
    { label: "LMS pushes", value: summary.lms_pushes },
    { label: "Lessons in library", value: summary.total_lessons }
  ];

  const renderCardValue = (value: number) => numberFormatter.format(value);

  const renderSkeletonCards = () => (
    <div className="grid gap-4 md:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div className="h-5 w-32 animate-pulse rounded bg-slate-200" />
          <div className="mt-4 h-8 w-20 animate-pulse rounded bg-slate-300" />
        </div>
      ))}
    </div>
  );

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Your LessonGen activity</h1>
        <p className="text-slate-600">
          Track creation, AI-powered generation, and sharing trends from the last 30 days.
        </p>
      </header>

      {isError && (
        <div className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Unable to load analytics right now. Please refresh to try again.
        </div>
      )}

      {isLoading && !data ? (
        renderSkeletonCards()
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {metricCards.map((card) => (
            <article
              key={card.label}
              className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            >
              <p className="text-sm font-medium text-slate-500">{card.label}</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">
                {renderCardValue(card.value)}
              </p>
            </article>
          ))}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Time saved</h2>
          <p className="mt-2 text-sm text-slate-600">
            Based on lesson generations, teachers have saved approximately
            <span className="ml-1 font-semibold text-slate-900">
              {numberFormatter.format(summary.estimated_time_saved_minutes)} minutes
            </span>
            {timeSavedHours >= 1 && (
              <span className="ml-1 text-slate-500">(~{numberFormatter.format(timeSavedHours)} hours)</span>
            )}.
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Next steps</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>• Differentiate a recently generated lesson to support a student group.</li>
            <li>• Export a polished plan or push it to Classroom when you are ready.</li>
            <li>• Share a lesson link with your grade team for quick feedback.</li>
          </ul>
        </article>
      </div>
    </section>
  );
};

export default DashboardPage;
