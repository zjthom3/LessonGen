const LessonsPage = () => {
  const placeholderLessons = [
    {
      id: 1,
      title: "Explore the Solar System",
      grade: "5",
      subject: "Science"
    },
    {
      id: 2,
      title: "Fractions in Everyday Life",
      grade: "4",
      subject: "Mathematics"
    }
  ];

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Lessons</h1>
        <p className="text-slate-600">
          Generated lessons and drafts will appear here once the generation service is live.
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        {placeholderLessons.map((lesson) => (
          <article key={lesson.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">{lesson.title}</h2>
            <p className="text-sm text-slate-600">
              Grade {lesson.grade} · {lesson.subject}
            </p>
            <p className="mt-3 text-sm text-slate-500">
              Align standards, versioning, and exports will be wired up in later sprints.
            </p>
          </article>
        ))}
      </div>
    </section>
  );
};

export default LessonsPage;
