"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface Integration {
  integration_type: string;
  enabled: boolean;
  status: string;
  config_summary: Record<string, string> | null;
}

export default function SettingsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeForm, setActiveForm] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/api/v1/integrations/`)
      .then((r) => r.json())
      .then(setIntegrations)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const refresh = () => {
    fetch(`${API}/api/v1/integrations/`).then((r) => r.json()).then(setIntegrations);
  };

  return (
    <div className="max-w-2xl reveal">
      <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
      <p className="text-sm text-[var(--text-muted)] mb-12">Connect your tools to automate workflows.</p>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-5 animate-pulse h-20" />
          ))}
        </div>
      ) : (
        <div className="space-y-10">
          {/* Infrastructure (always connected) */}
          <section className="reveal reveal-delay-1">
            <h2 className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-4">Infrastructure</h2>
            <div className="space-y-3">
              <Row name="Recall.ai" detail="Meeting bot · eu-central-1" status="connected" />
              <Row name="Google Gemini" detail="AI engine · gemini-3.5-flash" status="connected" />
            </div>
          </section>

          {/* Integrations */}
          <section className="reveal reveal-delay-2">
            <h2 className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-4">Integrations</h2>
            <div className="space-y-3">
              {/* Jira */}
              <IntegrationRow
                name="Jira"
                description="Auto-create issues from action items"
                integration={integrations.find((i) => i.integration_type === "jira")}
                onConnect={() => setActiveForm("jira")}
                onDisconnect={async () => {
                  await fetch(`${API}/api/v1/integrations/jira/disconnect`, { method: "POST" });
                  refresh();
                }}
              />

              {/* Notion */}
              <IntegrationRow
                name="Notion"
                description="Publish meeting summaries as pages"
                integration={integrations.find((i) => i.integration_type === "notion")}
                onConnect={() => setActiveForm("notion")}
                onDisconnect={async () => {
                  await fetch(`${API}/api/v1/integrations/notion/disconnect`, { method: "POST" });
                  refresh();
                }}
              />

              {/* Google Calendar */}
              <IntegrationRow
                name="Google Calendar"
                description="Auto-join scheduled meetings"
                integration={integrations.find((i) => i.integration_type === "google_calendar")}
                onConnect={() => setActiveForm("google_calendar")}
                onDisconnect={async () => {
                  await fetch(`${API}/api/v1/integrations/google_calendar/disconnect`, { method: "POST" });
                  refresh();
                }}
              />
            </div>
          </section>
        </div>
      )}

      {/* Connection Forms (modals) */}
      {activeForm === "jira" && (
        <ConnectModal
          title="Connect Jira"
          onClose={() => setActiveForm(null)}
          onSuccess={() => { setActiveForm(null); refresh(); }}
          fields={[
            { name: "url", label: "Jira URL", placeholder: "https://your-domain.atlassian.net", type: "url" },
            { name: "email", label: "Email", placeholder: "you@company.com", type: "email" },
            { name: "api_token", label: "API Token", placeholder: "Paste your Jira API token", type: "password" },
            { name: "project_key", label: "Project Key", placeholder: "PROJ", type: "text" },
          ]}
          endpoint={`${API}/api/v1/integrations/jira/connect`}
        />
      )}

      {activeForm === "notion" && (
        <ConnectModal
          title="Connect Notion"
          onClose={() => setActiveForm(null)}
          onSuccess={() => { setActiveForm(null); refresh(); }}
          fields={[
            { name: "api_key", label: "Integration Token", placeholder: "ntn_...", type: "password" },
            { name: "parent_page_id", label: "Parent Page ID", placeholder: "Page ID where summaries will be created", type: "text" },
          ]}
          endpoint={`${API}/api/v1/integrations/notion/connect`}
        />
      )}

      {activeForm === "google_calendar" && (
        <ConnectModal
          title="Connect Google Calendar"
          onClose={() => setActiveForm(null)}
          onSuccess={() => { setActiveForm(null); refresh(); }}
          fields={[
            { name: "access_token", label: "Access Token", placeholder: "OAuth access token", type: "password" },
            { name: "calendar_id", label: "Calendar ID", placeholder: "primary", type: "text" },
          ]}
          endpoint={`${API}/api/v1/integrations/google_calendar/connect`}
        />
      )}
    </div>
  );
}

function Row({ name, detail, status }: { name: string; detail: string; status: string }) {
  return (
    <div className="card p-5 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-[var(--text)]">{name}</p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">{detail}</p>
      </div>
      <span className="text-[11px] font-medium text-green-400 bg-green-400/10 px-3 py-1 rounded-full">{status}</span>
    </div>
  );
}

function IntegrationRow({
  name,
  description,
  integration,
  onConnect,
  onDisconnect,
}: {
  name: string;
  description: string;
  integration?: Integration;
  onConnect: () => void;
  onDisconnect: () => void;
}) {
  const connected = integration?.enabled && integration.status === "connected";

  return (
    <div className="card card-glow-blue p-5 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-[var(--text)]">{name}</p>
        <p className="text-xs text-[var(--text-muted)] mt-0.5">{description}</p>
        {connected && integration?.config_summary && (
          <p className="text-[10px] text-[var(--text-muted)] mt-1">
            {Object.entries(integration.config_summary).map(([k, v]) => `${k}: ${v}`).join(" · ")}
          </p>
        )}
      </div>
      {connected ? (
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-medium text-green-400 bg-green-400/10 px-3 py-1 rounded-full">Connected</span>
          <button onClick={onDisconnect} className="text-[10px] text-[var(--text-muted)] hover:text-red-400 transition-colors">
            Disconnect
          </button>
        </div>
      ) : (
        <button onClick={onConnect} className="text-[11px] font-medium text-[var(--text-muted)] border border-[var(--border)] px-3 py-1.5 rounded-full hover:border-[var(--border-hover)] hover:text-[var(--text)] transition-all duration-200">
          Connect
        </button>
      )}
    </div>
  );
}

function ConnectModal({
  title,
  onClose,
  onSuccess,
  fields,
  endpoint,
}: {
  title: string;
  onClose: () => void;
  onSuccess: () => void;
  fields: { name: string; label: string; placeholder: string; type: string }[];
  endpoint: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const body: Record<string, string> = {};
    for (const field of fields) {
      body[field.name] = formData.get(field.name) as string;
    }

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Connection failed (${res.status})`);
      }

      onSuccess();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="card p-8 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold mb-6">{title}</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map((field) => (
            <div key={field.name}>
              <label className="block text-xs text-[var(--text-muted)] mb-1.5 uppercase tracking-wider">
                {field.label}
              </label>
              <input
                name={field.name}
                type={field.type}
                required
                placeholder={field.placeholder}
                className="input-field"
              />
            </div>
          ))}

          {error && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={loading} className="btn-primary flex-1 disabled:opacity-50">
              {loading ? "Connecting..." : "Connect"}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>

        <p className="text-[10px] text-[var(--text-muted)] mt-4">
          Your credentials are stored securely and only used to sync meeting data.
        </p>
      </div>
    </div>
  );
}
