const DashboardPage = () => {
  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Welcome back!</h1>
        <p className="text-slate-600">
          This dashboard will evolve to show lesson generation activity, queued jobs, and
          actionable insights across your tenant.
        </p>
      </header>
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-slate-500">
        <p className="font-medium">Sprint 1 placeholder</p>
        <p className="text-sm">
          Connect Google OAuth, lesson metrics, and organization switching in upcoming sprints.
        </p>
      </div>
    </section>
  );
};

export default DashboardPage;
