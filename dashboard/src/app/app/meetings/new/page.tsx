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
      router.push(`/app/meetings/${meeting.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto reveal">
      <h1 className="text-3xl font-bold tracking-tight mb-2">New meeting</h1>
      <p className="text-sm text-[var(--text-muted)] mb-10">
        Paste a meeting link. The AI bot joins automatically.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="reveal reveal-delay-1">
          <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider">Title</label>
          <input name="title" type="text" required placeholder="Sprint planning" className="input-field" />
        </div>

        <div className="reveal reveal-delay-2">
          <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider">Meeting URL</label>
          <input name="meeting_url" type="url" required placeholder="https://meet.google.com/..." className="input-field" />
        </div>

        <div className="reveal reveal-delay-3">
          <label className="block text-xs text-[var(--text-muted)] mb-2 uppercase tracking-wider">Platform</label>
          <select name="platform" required className="input-field">
            <option value="google_meet">Google Meet</option>
            <option value="teams">Microsoft Teams</option>
            <option value="zoom">Zoom</option>
          </select>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
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
