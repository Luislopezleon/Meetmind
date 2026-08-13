"use client";

export default function SettingsPage() {
  return (
    <div className="max-w-2xl reveal">
      <div className="mb-10">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)] tracking-tight">Settings</h1>
        <p className="text-sm text-[var(--text-muted)] mt-2">Manage your connections and preferences.</p>
      </div>

      <div className="space-y-6">
        {/* Connected services */}
        <div className="reveal reveal-delay-1">
          <h2 className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-4">Connected Services</h2>
          <div className="space-y-3">
            <ServiceRow name="Recall.ai" description="Meeting bot infrastructure" status="connected" detail="eu-central-1" />
            <ServiceRow name="Google Gemini" description="AI analysis engine" status="connected" detail="gemini-3.5-flash · free tier" />
          </div>
        </div>

        {/* Available integrations */}
        <div className="reveal reveal-delay-2">
          <h2 className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-4">Integrations</h2>
          <div className="space-y-3">
            <ServiceRow name="Jira" description="Sync action items as issues" status="available" />
            <ServiceRow name="Notion" description="Publish summaries as pages" status="available" />
            <ServiceRow name="Google Calendar" description="Auto-join scheduled meetings" status="available" />
            <ServiceRow name="Slack" description="Send insights to channels" status="available" />
          </div>
        </div>
      </div>
    </div>
  );
}

function ServiceRow({ name, description, status, detail }: { name: string; description: string; status: "connected" | "available"; detail?: string }) {
  return (
    <div className="flex items-center justify-between py-4 px-5 rounded-xl border border-[var(--border)] hover:border-[var(--border-glow)] transition-all duration-300">
      <div>
        <p className="text-sm font-medium text-[var(--text-primary)]">{name}</p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">{description}</p>
        {detail && <p className="text-[11px] text-[var(--text-muted)] mt-1">{detail}</p>}
      </div>
      {status === "connected" ? (
        <span className="text-[11px] font-medium text-[var(--success)] bg-[var(--success-dim)] px-2.5 py-1 rounded-full">Connected</span>
      ) : (
        <button className="text-[11px] font-medium text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-3 py-1.5 rounded-lg border border-[var(--border)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all duration-200">
          Connect
        </button>
      )}
    </div>
  );
}
