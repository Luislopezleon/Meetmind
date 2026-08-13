"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createMeeting } from "@/lib/api";

export default function NewMeetingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);

    try {
      const meeting = await createMeeting({
        title: formData.get("title") as string,
        meeting_url: formData.get("meeting_url") as string,
        platform: formData.get("platform") as string,
        scheduled_at: new Date().toISOString(),
      });
      router.push(`/meetings/${meeting.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto reveal">
      <div className="text-center mb-10">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)] tracking-tight">
          New meeting
        </h1>
        <p className="text-sm text-[var(--text-muted)] mt-2">
          Paste a meeting link. The AI bot joins automatically.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="reveal reveal-delay-1">
          <label htmlFor="title" className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Title
          </label>
          <input id="title" name="title" type="text" required placeholder="Sprint planning" className="input-field" />
        </div>

        <div className="reveal reveal-delay-2">
          <label htmlFor="meeting_url" className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Meeting URL
          </label>
          <input id="meeting_url" name="meeting_url" type="url" required placeholder="https://meet.google.com/..." className="input-field" />
        </div>

        <div className="reveal reveal-delay-3">
          <label htmlFor="platform" className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Platform
          </label>
          <select id="platform" name="platform" required className="input-field">
            <option value="google_meet">Google Meet</option>
            <option value="teams">Microsoft Teams</option>
            <option value="zoom">Zoom</option>
          </select>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-[var(--danger-dim)] border border-[rgba(255,90,90,0.15)] text-[var(--danger)] text-sm reveal-scale">
            {error}
          </div>
        )}

        <div className="pt-4 reveal reveal-delay-4">
          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
            {loading ? "Sending bot..." : "Create & send bot"}
          </button>
        </div>
      </form>
    </div>
  );
}
