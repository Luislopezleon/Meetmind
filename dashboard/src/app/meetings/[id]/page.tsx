"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { getMeeting, getMeetingTranscript, getMeetingInsights } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { Meeting } from "@/types";

interface TranscriptEntry { text: string; speaker: string; }
interface Insight { type: "action_item" | "decision" | "risk" | "question"; data: Record<string, unknown>; }

export default function MeetingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const meetingId = Number(params.id);

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"transcript" | "insights" | "summary">("transcript");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function load() {
      try {
        const [m, t, ins] = await Promise.all([
          getMeeting(meetingId),
          getMeetingTranscript(meetingId).catch(() => []),
          getMeetingInsights(meetingId).catch(() => null),
        ]);
        setMeeting(m);
        if (t.length) setTranscript(t.map((c) => ({ text: c.text, speaker: c.speaker })));
        if (ins) {
          const all: Insight[] = [];
          ins.action_items.forEach((d) => all.push({ type: "action_item", data: d as unknown as Record<string, unknown> }));
          ins.decisions.forEach((d) => all.push({ type: "decision", data: d as unknown as Record<string, unknown> }));
          ins.risks.forEach((d) => all.push({ type: "risk", data: d as unknown as Record<string, unknown> }));
          ins.questions.forEach((d) => all.push({ type: "question", data: d as unknown as Record<string, unknown> }));
          setInsights(all);
          setSummary(ins.summary);
        }
      } catch { /* */ }
      finally { setLoading(false); }
    }
    load();
  }, [meetingId]);

  // WebSocket
  const onChunk = useCallback((d: Record<string, unknown>) => {
    setTranscript((p) => [...p, { text: d.text as string, speaker: d.speaker as string }]);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }, []);
  const onInsight = useCallback((d: Record<string, unknown>) => {
    setInsights((p) => [...p, { type: d.insight_type as Insight["type"], data: (d.data || d) as Record<string, unknown> }]);
  }, []);
  const onStatus = useCallback((d: Record<string, unknown>) => {
    setMeeting((p) => p ? { ...p, status: d.status as string } : p);
  }, []);

  const { isConnected } = useWebSocket({ meetingId, onTranscriptChunk: onChunk, onInsightDetected: onInsight, onStatusUpdate: onStatus });

  if (loading) return <div className="h-96 flex items-center justify-center"><div className="w-5 h-5 border-2 border-[var(--accent)]/30 border-t-[var(--accent)] rounded-full animate-spin" /></div>;
  if (!meeting) return <div className="text-center py-20 text-[var(--text-muted)]">Meeting not found</div>;

  const actions = insights.filter((i) => i.type === "action_item");
  const decisions = insights.filter((i) => i.type === "decision");
  const risks = insights.filter((i) => i.type === "risk");
  const questions = insights.filter((i) => i.type === "question");

  return (
    <div className="reveal">
      {/* Back + header */}
      <button onClick={() => router.push("/")} className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors mb-6">
        ← Back to meetings
      </button>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-[var(--text-primary)] tracking-tight">{meeting.title}</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            {meeting.platform.replace(/_/g, " ")}
            {meeting.participants.length > 0 && ` · ${meeting.participants.join(", ")}`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isConnected && meeting.status === "in_progress" && (
            <span className="flex items-center gap-1.5 text-xs text-[var(--success)]">
              <span className="w-2 h-2 bg-[var(--success)] rounded-full animate-pulse" />
              Live
            </span>
          )}
          <StatusPill status={meeting.status} />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 border-b border-[var(--border)] mb-8">
        {([
          ["transcript", "Transcript", transcript.length],
          ["insights", "Insights", insights.length],
          ["summary", "Summary", summary ? 1 : 0],
        ] as const).map(([key, label, count]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`pb-3 text-sm font-medium border-b-2 transition-all duration-200 ${
              tab === key
                ? "border-[var(--accent)] text-[var(--text-primary)]"
                : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
            }`}
          >
            {label}{count > 0 && <span className="ml-1.5 text-[var(--text-muted)]">{count}</span>}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="reveal" key={tab}>
        {tab === "transcript" && <Transcript entries={transcript} endRef={endRef} />}
        {tab === "insights" && <Insights actions={actions} decisions={decisions} risks={risks} questions={questions} />}
        {tab === "summary" && <Summary text={summary} />}
      </div>
    </div>
  );
}

function Transcript({ entries, endRef }: { entries: TranscriptEntry[]; endRef: React.RefObject<HTMLDivElement | null> }) {
  if (!entries.length) return <Empty icon="◉" text="No transcript yet" sub="Transcript appears here once the bot starts recording." />;

  const grouped: { speaker: string; text: string }[] = [];
  for (const e of entries) {
    const last = grouped[grouped.length - 1];
    if (last && last.speaker === e.speaker) last.text += " " + e.text;
    else grouped.push({ speaker: e.speaker, text: e.text });
  }

  return (
    <div className="space-y-6 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
      {grouped.map((g, i) => (
        <div key={i} className={`reveal reveal-delay-${Math.min(i + 1, 3)}`}>
          <span className="text-xs font-medium text-[var(--accent)] mb-1 block">{g.speaker}</span>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{g.text}</p>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

function Insights({ actions, decisions, risks, questions }: { actions: Insight[]; decisions: Insight[]; risks: Insight[]; questions: Insight[] }) {
  if (!actions.length && !decisions.length && !risks.length && !questions.length) {
    return <Empty icon="◈" text="No insights detected" sub="The AI agent will extract action items, decisions, and risks from the transcript." />;
  }

  return (
    <div className="space-y-8">
      {actions.length > 0 && (
        <Section title="Action Items" count={actions.length}>
          {actions.map((item, i) => (
            <div key={i} className="flex items-start justify-between py-3 border-b border-[var(--border-subtle)] last:border-0">
              <div>
                <p className="text-sm text-[var(--text-primary)]">{item.data.task as string}</p>
                <div className="flex items-center gap-2 mt-1">
                  {item.data.assignee && <span className="text-xs text-[var(--accent)]">@{item.data.assignee as string}</span>}
                  {item.data.deadline && <span className="text-xs text-[var(--text-muted)]">{item.data.deadline as string}</span>}
                </div>
              </div>
              {item.data.priority === "high" && <span className="badge badge-danger">high</span>}
            </div>
          ))}
        </Section>
      )}

      {decisions.length > 0 && (
        <Section title="Decisions" count={decisions.length}>
          {decisions.map((item, i) => (
            <div key={i} className="py-3 border-b border-[var(--border-subtle)] last:border-0">
              <p className="text-sm text-[var(--text-primary)]">{item.data.decision as string}</p>
              {item.data.decision_maker && <p className="text-xs text-[var(--text-muted)] mt-1">by {item.data.decision_maker as string}</p>}
            </div>
          ))}
        </Section>
      )}

      {risks.length > 0 && (
        <Section title="Risks" count={risks.length}>
          {risks.map((item, i) => (
            <div key={i} className="py-3 border-b border-[var(--border-subtle)] last:border-0">
              <p className="text-sm text-[var(--text-primary)]">{item.data.description as string}</p>
              <div className="flex items-center gap-2 mt-1">
                {item.data.category && <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-2 py-0.5 rounded">{item.data.category as string}</span>}
                {item.data.severity && <span className="text-[10px] text-[var(--warning)] bg-[var(--warning-dim)] px-2 py-0.5 rounded">{item.data.severity as string}</span>}
              </div>
            </div>
          ))}
        </Section>
      )}

      {questions.length > 0 && (
        <Section title="Open Questions" count={questions.length}>
          {questions.map((item, i) => (
            <div key={i} className="py-3 border-b border-[var(--border-subtle)] last:border-0">
              <p className="text-sm text-[var(--text-primary)]">{item.data.question as string}</p>
              {item.data.asked_by && <p className="text-xs text-[var(--text-muted)] mt-1">asked by {item.data.asked_by as string}</p>}
            </div>
          ))}
        </Section>
      )}
    </div>
  );
}

function Summary({ text }: { text: string | null }) {
  if (!text) return <Empty icon="◆" text="No summary yet" sub="A summary is generated after the meeting ends and the AI finishes analyzing." />;

  // Parse into clean text (strip markdown)
  const clean = text
    .replace(/^#{1,4}\s*/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/^\*\s/gm, "• ")
    .replace(/^-\s/gm, "• ");

  const paragraphs = clean.split("\n").filter((l) => l.trim());

  return (
    <div className="space-y-4 max-w-2xl">
      {paragraphs.map((p, i) => (
        <p key={i} className={`text-sm leading-relaxed ${p.startsWith("•") ? "text-[var(--text-secondary)] pl-4" : "text-[var(--text-primary)]"}`}>
          {p}
        </p>
      ))}
    </div>
  );
}

function Section({ title, count, children }: { title: string; count: number; children: React.ReactNode }) {
  return (
    <div className="reveal">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">{title}</h3>
        <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded">{count}</span>
      </div>
      <div>{children}</div>
    </div>
  );
}

function Empty({ icon, text, sub }: { icon: string; text: string; sub: string }) {
  return (
    <div className="text-center py-16">
      <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-[var(--bg-tertiary)] flex items-center justify-center">
        <span className="text-[var(--text-muted)]">{icon}</span>
      </div>
      <p className="text-sm text-[var(--text-secondary)] mb-1">{text}</p>
      <p className="text-xs text-[var(--text-muted)]">{sub}</p>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string }> = {
    scheduled: { bg: "var(--bg-tertiary)", text: "var(--text-muted)" },
    bot_created: { bg: "var(--info-dim)", text: "var(--info)" },
    connecting: { bg: "var(--warning-dim)", text: "var(--warning)" },
    in_progress: { bg: "var(--success-dim)", text: "var(--success)" },
    completed: { bg: "var(--accent-dim)", text: "var(--accent)" },
    failed: { bg: "var(--danger-dim)", text: "var(--danger)" },
  };
  const c = config[status] || config.scheduled;
  return <span className="px-2.5 py-1 rounded-full text-[11px] font-medium" style={{ background: c.bg, color: c.text }}>{status.replace(/_/g, " ")}</span>;
}
