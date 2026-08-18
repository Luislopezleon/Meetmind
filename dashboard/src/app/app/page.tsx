"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getMeetings } from "@/lib/api";
import type { Meeting } from "@/types";

export default function HomePage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMeetings().then(setMeetings).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {/* Hero */}
      <div className="reveal mb-16">
        <h1 className="text-5xl font-bold tracking-tight leading-tight">
          Meeting intelligence,<br />
          <span className="text-[var(--text-muted)]">automated.</span>
        </h1>
        <p className="text-[var(--text-secondary)] mt-4 text-lg max-w-xl">
          Send a bot to any meeting. Get transcripts, action items, decisions, and risks — extracted by AI in real time.
        </p>
        <div className="mt-8 flex items-center gap-4">
          <Link href="/app/meetings/new" className="btn-primary">New meeting</Link>
          <Link href="/app/settings" className="btn-secondary">Settings</Link>
        </div>
      </div>

      {/* Meetings */}
      <div className="reveal reveal-delay-2">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-sm font-medium text-[var(--text-muted)] uppercase tracking-wider">Recent meetings</h2>
          {meetings.length > 0 && (
            <span className="text-xs text-[var(--text-muted)]">{meetings.length} total</span>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card p-6 h-40 animate-pulse">
                <div className="h-4 bg-[#1a1a1a] rounded w-2/3 mb-3" />
                <div className="h-3 bg-[#1a1a1a] rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : meetings.length === 0 ? (
          <div className="card gradient-border p-16 text-center">
            <p className="text-[var(--text-secondary)] text-lg mb-2">No meetings yet</p>
            <p className="text-[var(--text-muted)] text-sm mb-8">
              Create your first meeting to see AI-powered insights.
            </p>
            <Link href="/app/meetings/new" className="btn-primary">Create meeting</Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {meetings.map((meeting, i) => {
              const glows = ["card-glow-blue", "card-glow-green", "card-glow-purple", "card-glow-amber", "card-glow-pink"];
              const glow = glows[i % glows.length];

              return (
                <Link
                  key={meeting.id}
                  href={`/app/meetings/${meeting.id}`}
                  className={`card ${glow} p-6 block reveal reveal-delay-${Math.min(i + 1, 5)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-sm font-medium text-[var(--text)] leading-snug">
                      {meeting.title}
                    </h3>
                    <StatusDot status={meeting.status} />
                  </div>
                  <p className="text-xs text-[var(--text-muted)]">
                    {meeting.platform.replace(/_/g, " ")}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    {new Date(meeting.scheduled_at).toLocaleDateString("es-ES", {
                      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
                    })}
                  </p>
                  {meeting.participants.length > 0 && (
                    <div className="flex items-center gap-1 mt-3">
                      {meeting.participants.slice(0, 3).map((p, j) => (
                        <div key={j} className="w-5 h-5 rounded-full bg-[#222] flex items-center justify-center">
                          <span className="text-[9px] text-[var(--text-muted)]">{p.charAt(0)}</span>
                        </div>
                      ))}
                      {meeting.participants.length > 3 && (
                        <span className="text-[10px] text-[var(--text-muted)] ml-1">+{meeting.participants.length - 3}</span>
                      )}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    in_progress: "bg-green-500",
    completed: "bg-blue-500",
    failed: "bg-red-500",
    connecting: "bg-yellow-500",
  };
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-2 h-2 rounded-full ${colors[status] || "bg-[#333]"} ${status === "in_progress" ? "animate-pulse" : ""}`} />
      <span className="text-[10px] text-[var(--text-muted)]">{status.replace(/_/g, " ")}</span>
    </div>
  );
}
