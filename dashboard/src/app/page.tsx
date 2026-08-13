"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getMeetings } from "@/lib/api";
import type { Meeting } from "@/types";

export default function HomePage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMeetings()
      .then(setMeetings)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="reveal">
      {/* Page header */}
      <div className="flex items-end justify-between mb-10">
        <div>
          <h1 className="text-3xl font-semibold text-[var(--text-primary)] tracking-tight">
            Meetings
          </h1>
          <p className="text-[var(--text-muted)] mt-2 text-sm">
            Record, transcribe, and extract insights from any meeting.
          </p>
        </div>
        <Link href="/meetings/new" className="btn-primary">
          New meeting
        </Link>
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card-static p-6 animate-pulse">
              <div className="h-4 bg-[var(--bg-tertiary)] rounded w-1/4 mb-3" />
              <div className="h-3 bg-[var(--bg-tertiary)] rounded w-2/5" />
            </div>
          ))}
        </div>
      ) : meetings.length === 0 ? (
        <div className="card-static p-20 text-center reveal reveal-delay-1">
          <div className="w-14 h-14 mx-auto mb-6 rounded-2xl bg-[var(--accent-dim)] flex items-center justify-center pulse-glow">
            <span className="text-[var(--accent)] text-lg">◉</span>
          </div>
          <h2 className="text-lg font-medium text-[var(--text-primary)] mb-2">
            No meetings yet
          </h2>
          <p className="text-sm text-[var(--text-muted)] max-w-sm mx-auto mb-8">
            Create a meeting to send an AI bot that joins, transcribes, and analyzes the conversation automatically.
          </p>
          <Link href="/meetings/new" className="btn-primary">
            Create your first meeting
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {meetings.map((meeting, i) => (
            <Link
              key={meeting.id}
              href={`/meetings/${meeting.id}`}
              className={`block group reveal reveal-delay-${Math.min(i + 1, 5)}`}
            >
              <div className="flex items-center justify-between py-4 px-5 rounded-xl border border-transparent hover:border-[var(--border)] hover:bg-[var(--bg-card)] transition-all duration-300">
                <div className="flex items-center gap-4">
                  <div className="w-9 h-9 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center group-hover:bg-[var(--accent-dim)] transition-colors duration-300">
                    <span className="text-xs text-[var(--text-muted)] group-hover:text-[var(--accent)] transition-colors duration-300">
                      {meeting.title.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-[var(--text-primary)]">{meeting.title}</h3>
                    <p className="text-xs text-[var(--text-muted)] mt-0.5">
                      {new Date(meeting.scheduled_at).toLocaleDateString("es-ES", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                      {meeting.participants.length > 0 && ` · ${meeting.participants.join(", ")}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-[var(--text-muted)]">{meeting.platform.replace(/_/g, " ")}</span>
                  <StatusPill status={meeting.status} />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; dot?: boolean }> = {
    scheduled: { bg: "var(--bg-tertiary)", text: "var(--text-muted)" },
    bot_created: { bg: "var(--info-dim)", text: "var(--info)" },
    connecting: { bg: "var(--warning-dim)", text: "var(--warning)", dot: true },
    in_progress: { bg: "var(--success-dim)", text: "var(--success)", dot: true },
    completed: { bg: "var(--accent-dim)", text: "var(--accent)" },
    failed: { bg: "var(--danger-dim)", text: "var(--danger)" },
  };
  const c = config[status] || config.scheduled;

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium" style={{ background: c.bg, color: c.text }}>
      {c.dot && <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: c.text }} />}
      {status.replace(/_/g, " ")}
    </span>
  );
}
