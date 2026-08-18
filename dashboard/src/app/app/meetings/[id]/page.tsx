"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { getMeeting, getMeetingTranscript, getMeetingInsights } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { Meeting } from "@/types";

interface TranscriptEntry { text: string; speaker: string; }
interface Insight { type: string; data: Record<string, unknown>; }

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
      } catch { /* */ } finally { setLoading(false); }
    }
    load();
  }, [meetingId]);

  const onChunk = useCallback((d: Record<string, unknown>) => {
    setTranscript((p) => [...p, { text: d.text as string, speaker: d.speaker as string }]);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }, []);
  const onInsight = useCallback((d: Record<string, unknown>) => {
    setInsights((p) => [...p, { type: d.insight_type as string, data: (d.data || d) as Record<string, unknown> }]);
  }, []);
  const onStatus = useCallback((d: Record<string, unknown>) => {
    setMeeting((p) => p ? { ...p, status: d.status as string } : p);
  }, []);

  const { isConnected } = useWebSocket({ meetingId, onTranscriptChunk: onChunk, onInsightDetected: onInsight, onStatusUpdate: onStatus });

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /></div>;
  if (!meeting) return <div className="text-center py-20 text-[var(--text-muted)]">Meeting not found</div>;

  return (
    <div className="reveal">
      <button onClick={() => router.push("/app")} className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors mb-8 block">
        &larr; Back
      </button>

      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold tracking-tight">{meeting.title}</h1>
          {isConnected && meeting.status === "in_progress" && (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-green-500/10 border border-green-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] text-green-400 font-medium">Live</span>
            </div>
          )}
        </div>
        <p className="text-sm text-[var(--text-muted)]">
          {meeting.platform.replace(/_/g, " ")}
          {meeting.participants.length > 0 && ` · ${meeting.participants.join(", ")}`}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-8 border-b border-[var(--border)] mb-8">
        {(["transcript", "insights", "summary"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`pb-3 text-sm font-medium capitalize transition-all duration-200 ${tab === t ? "tab-active" : "tab-inactive"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      <div key={tab} className="reveal">
        {tab === "transcript" && <TranscriptView entries={transcript} endRef={endRef} />}
        {tab === "insights" && <InsightsView insights={insights} />}
        {tab === "summary" && <SummaryView text={summary} />}
      </div>
    </div>
  );
}

function TranscriptView({ entries, endRef }: { entries: TranscriptEntry[]; endRef: React.RefObject<HTMLDivElement | null> }) {
  if (!entries.length) return <Empty text="No transcript yet" />;

  const grouped: { speaker: string; text: string }[] = [];
  for (const e of entries) {
    const last = grouped[grouped.length - 1];
    if (last && last.speaker === e.speaker) last.text += " " + e.text;
    else grouped.push({ ...e });
  }

  return (
    <div className="space-y-6 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
      {grouped.map((g, i) => (
        <div key={i} className={`reveal reveal-delay-${Math.min(i + 1, 3)}`}>
          <p className="text-xs font-medium text-[var(--text-secondary)] mb-1.5">{g.speaker}</p>
          <p className="text-sm text-[var(--text-muted)] leading-relaxed">{g.text}</p>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

function InsightsView({ insights }: { insights: Insight[] }) {
  if (!insights.length) return <Empty text="No insights detected yet" />;

  const groups = [
    { type: "action_item", label: "Action Items", glow: "card-glow-green" },
    { type: "decision", label: "Decisions", glow: "card-glow-blue" },
    { type: "risk", label: "Risks", glow: "card-glow-amber" },
    { type: "question", label: "Open Questions", glow: "card-glow-purple" },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {groups.map(({ type, label, glow }) => {
        const items = insights.filter((i) => i.type === type);
        if (!items.length) return null;

        return (
          <div key={type} className={`card ${glow} p-6 reveal`}>
            <h3 className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-4">{label}</h3>
            <div className="space-y-3">
              {items.map((item, i) => (
                <div key={i} className="border-b border-[var(--border)] last:border-0 pb-3 last:pb-0">
                  <p className="text-sm text-[var(--text)]">
                    {String(item.data.task || item.data.decision || item.data.description || item.data.question || "")}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    {item.data.assignee ? <span className="text-xs text-blue-400">@{String(item.data.assignee)}</span> : null}
                    {item.data.deadline ? <span className="text-xs text-[var(--text-muted)]">{String(item.data.deadline)}</span> : null}
                    {item.data.decision_maker ? <span className="text-xs text-[var(--text-muted)]">by {String(item.data.decision_maker)}</span> : null}
                    {item.data.severity ? <span className="text-xs text-amber-400">{String(item.data.severity)}</span> : null}
                    {item.data.asked_by ? <span className="text-xs text-[var(--text-muted)]">by {String(item.data.asked_by)}</span> : null}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function SummaryView({ text }: { text: string | null }) {
  if (!text) return <Empty text="Summary will appear after the meeting ends" />;

  const clean = text.replace(/^#{1,4}\s*/gm, "").replace(/\*\*(.*?)\*\*/g, "$1").replace(/^\*\s/gm, "• ").replace(/^-\s/gm, "• ");
  const paragraphs = clean.split("\n").filter((l) => l.trim());

  return (
    <div className="max-w-2xl space-y-3">
      {paragraphs.map((p, i) => (
        <p key={i} className={`text-sm leading-relaxed ${p.startsWith("•") ? "text-[var(--text-muted)] pl-4" : "text-[var(--text-secondary)]"}`}>
          {p}
        </p>
      ))}
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div className="text-center py-20">
      <p className="text-sm text-[var(--text-muted)]">{text}</p>
    </div>
  );
}
