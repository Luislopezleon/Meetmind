export interface Meeting {
  id: number;
  title: string;
  meeting_url: string;
  platform: "google_meet" | "teams" | "zoom";
  status: string;
  recall_bot_id: string | null;
  participants: string[];
  duration_minutes: number | null;
  scheduled_at: string;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptChunk {
  id: number;
  meeting_id: number;
  text: string;
  speaker_name: string | null;
  speaker_id: string | null;
  confidence: number | null;
  start_time: number | null;
  end_time: number | null;
  timestamp: string;
}

export interface ActionItem {
  id: number;
  meeting_id: number;
  task: string;
  assignee: string | null;
  deadline: string | null;
  priority: "low" | "medium" | "high";
  status: "open" | "in_progress" | "completed";
  confidence_score: number | null;
  detected_at: string;
}

export interface Decision {
  id: number;
  meeting_id: number;
  decision: string;
  context: string | null;
  impact: "low" | "medium" | "high";
  decision_maker: string | null;
  confidence_score: number | null;
  detected_at: string;
}

export interface Risk {
  id: number;
  meeting_id: number;
  risk_description: string;
  category: string | null;
  severity: "low" | "medium" | "high" | "critical";
  mitigation_suggested: string | null;
  confidence_score: number | null;
  detected_at: string;
}

export interface OpenQuestion {
  id: number;
  meeting_id: number;
  question: string;
  context: string | null;
  asked_by: string | null;
  assigned_to: string | null;
  status: string;
  detected_at: string;
}

export interface MeetingSummary {
  id: number;
  meeting_id: number;
  executive_summary: string;
  key_topics: string[];
  next_steps: string | null;
  generated_by: string;
  word_count: number | null;
  generated_at: string;
}

export interface WebSocketMessage {
  type: "meeting_connected" | "transcript_chunk" | "insight_detected" | "status_update" | "pong";
  data: Record<string, unknown>;
  timestamp: string;
}
