export interface UserProfile {
  user_id: number;
  name: string;
  email?: string | null;
  level?: string | null;
  dominant_hand?: string | null;
  goal?: string | null;
  golfer_type?: string | null;
  current_main_issue?: string | null;
  preferred_feedback_style?: string | null;
  profile_summary?: string | null;
  memory_summary?: string[];
}

export interface SwingSession {
  id: number;
  user_id: number;
  club_type?: string | null;
  view_type?: string | null;
  concern?: string | null;
  video_url?: string | null;
  score?: number | null;
  main_issue?: string | null;
  created_at: string;
}

export interface SwingSessionCreatePayload {
  club_type?: string;
  view_type?: string;
  concern?: string | null;
  video_url?: string | null;
}

export interface SwingAnalysis {
  session_id: number;
  score?: number | null;
  main_issue?: string | null;
  phase_summary?: Record<string, unknown>;
  pose_metrics?: Record<string, unknown>;
  diagnosis_text?: string | null;
  evidence_text?: string | null;
  priority_issue?: string | null;
  recommended_action?: string | null;
}

export interface StructuredCoachingOutput {
  summary?: string;
  cause?: string;
  fix?: string;
  recommended_drill?: string;
  expected_effect?: string;
  sources?: string[];
  confidence?: number;
}

export interface CoachChatRequest {
  user_id: number;
  message: string;
  conversation_id?: number | null;
}

export interface CoachChatResponse {
  message_id: number;
  conversation_id: number;
  answer: string;
  structured_output?: StructuredCoachingOutput | null;
  sources?: string[];
  latency_ms: number;
  trace_id?: string;
  guardrail_status?: string;
  failure_type?: string | null;
}

export interface FeedbackRequest {
  user_id: number;
  message_id: number;
  feedback_type: string;
  reason?: string | null;
}

export interface FeedbackResponse {
  id: number;
  status: string;
}

export interface PromptVersion {
  name: string;
  version: string;
  is_active: boolean;
  created_at: string;
}

export interface ConversationTrace {
  conversation_id: number;
  workflow: string;
  prompt_version: string;
  latency_ms?: number | null;
  retrieved_chunk_count: number;
  guardrail_status?: string | null;
  failure_type?: string | null;
  retrieved_sources: string[];
  question_type?: string | null;
  trace: Record<string, unknown>;
}
