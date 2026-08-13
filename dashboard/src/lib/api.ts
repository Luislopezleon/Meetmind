const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  if (res.status === 204) return {} as T;
  return res.json();
}

export async function getMeetings(): Promise<import("@/types").Meeting[]> {
  return fetchAPI("/api/v1/meetings/");
}

export async function getMeeting(id: number): Promise<import("@/types").Meeting> {
  return fetchAPI(`/api/v1/meetings/${id}`);
}

export async function createMeeting(data: {
  title: string;
  meeting_url: string;
  platform: string;
  scheduled_at: string;
  participants?: string[];
}): Promise<import("@/types").Meeting> {
  return fetchAPI("/api/v1/meetings/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteMeeting(id: number): Promise<void> {
  await fetchAPI(`/api/v1/meetings/${id}`, { method: "DELETE" });
}


export async function getMeetingTranscript(id: number): Promise<
  { id: number; text: string; speaker: string; start_time: number | null; end_time: number | null }[]
> {
  return fetchAPI(`/api/v1/meetings/${id}/transcript`);
}

export async function getMeetingInsights(id: number): Promise<{
  action_items: { task: string; assignee: string | null; deadline: string | null; priority: string; confidence: number | null }[];
  decisions: { decision: string; context: string | null; impact: string; decision_maker: string | null; confidence: number | null }[];
  risks: { description: string; category: string | null; severity: string; mitigation: string | null; confidence: number | null }[];
  questions: { question: string; context: string | null; asked_by: string | null; assigned_to: string | null; confidence: number | null }[];
  summary: string | null;
}> {
  return fetchAPI(`/api/v1/meetings/${id}/insights`);
}
