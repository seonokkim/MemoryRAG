import type {
  CoachChatRequest,
  CoachChatResponse,
  ConversationTrace,
  FeedbackRequest,
  FeedbackResponse,
  PromptVersion,
  SwingAnalysis,
  SwingSession,
  SwingSessionCreatePayload,
  UserProfile,
} from "./types";

/** In dev, default "" so requests hit Vite proxy (/api → :8000). Override with VITE_API_BASE_URL. */
const API_BASE = (
  import.meta.env.VITE_API_BASE_URL as string | undefined
)?.replace(/\/$/, "") ?? (import.meta.env.DEV ? "" : "http://localhost:8000");

const API_PREFIX = "/api";

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export const DEMO_USER_ID = Number(import.meta.env.VITE_DEMO_USER_ID ?? 1);

export const DEMO_CONVERSATION_KEY = "demo_conversation_id";

class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${API_PREFIX}${path}`;
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Network error";
    throw new ApiError(`Cannot reach API at ${API_BASE}: ${msg}`, 0);
  }

  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new ApiError(`Invalid JSON from ${path}`, response.status, text);
    }
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(detail || `Request failed (${response.status})`, response.status, data);
  }

  return data as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getProfile(userId: number = DEMO_USER_ID): Promise<UserProfile> {
  return request<UserProfile>(`/users/${userId}/profile`);
}

export function getSwingSessions(userId: number = DEMO_USER_ID): Promise<SwingSession[]> {
  return request<SwingSession[]>(`/users/${userId}/swing-sessions`);
}

export function createSwingSession(
  userId: number,
  payload: SwingSessionCreatePayload
): Promise<SwingSession> {
  return request<SwingSession>(`/users/${userId}/swing-sessions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getSwingAnalysis(sessionId: number): Promise<SwingAnalysis> {
  return request<SwingAnalysis>(`/swing-sessions/${sessionId}/analysis`);
}

export function sendCoachMessage(payload: CoachChatRequest): Promise<CoachChatResponse> {
  return request<CoachChatResponse>("/coach/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function sendFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  return request<FeedbackResponse>("/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getPromptVersions(): Promise<PromptVersion[]> {
  return request<PromptVersion[]>("/dev/prompt-versions");
}

export function getConversationTrace(conversationId: number): Promise<ConversationTrace> {
  return request<ConversationTrace>(`/dev/conversations/${conversationId}/trace`);
}

export { ApiError };
