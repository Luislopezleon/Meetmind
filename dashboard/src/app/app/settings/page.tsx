"use client";

export default function SettingsPage() {
  return (
    <div className="max-w-2xl reveal">
      <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
      <p className="text-sm text-[var(--text-muted)] mb-12">Manage connections and integrations.</p>

      {/* Connected */}
      <section className="mb-12 reveal reveal-delay-1">
        <h2 className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-5">Connected</h2>
        <div className="space-y-3">
          <ServiceRow name="Recall.ai" detail="Meeting bot · eu-central-1" connected />
          <ServiceRow name="Google Gemini" detail="AI engine · gemini-3.5-flash · free" connected />
        </div>
      </section>

      {/* Available */}
      <section className="reveal reveal-delay-2">
        <h2 className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-5">Available integrations</h2>
        <div className="space-y-3">
          <ServiceRow name="Jira" detail="Sync action items as issues" />
          <ServiceRow name="Notion" detail="Publish summaries as pages" />
          <ServiceRow name="Google Calendar" detail="Auto-join scheduled meetings" />
          <ServiceRow name="Slack" detail="Post insights to channels" />
        </div>
      </section>
    </div>
  );
}

function ServiceRow({ name, detail, connected }: { name: string; detail: string; connected?: boolean }) {
  return (
    <div className="card card-glow-blue p-5 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-[var(--text)]">{name}</p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">{detail}</p>
      </div>
      {connected ? (
        <span className="text-[11px] font-medium text-green-400 bg-green-400/10 px-3 py-1 rounded-full">Connected</span>
      ) : (
        <button className="text-[11px] font-medium text-[var(--text-muted)] border border-[var(--border)] px-3 py-1.5 rounded-full hover:border-[var(--border-hover)] hover:text-[var(--text-secondary)] transition-all duration-200">
          Connect
        </button>
      )}
    </div>
  );
}
