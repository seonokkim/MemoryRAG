import { useState, useRef, useEffect } from "react";
import { Send, ThumbsUp, ThumbsDown, Code2, Bot } from "lucide-react";
import { useNavigate } from "react-router";
import {
  ApiError,
  DEMO_CONVERSATION_KEY,
  DEMO_USER_ID,
  getHealth,
  sendCoachMessage,
  sendFeedback,
} from "../api/client";
import { c } from "../design";

const SUGGESTED = [
  "Why do I keep slicing?",
  "Am I improving compared to last time?",
  "What should I practice today?",
  "What type of golfer am I?",
];

interface Message {
  id: number;
  role: "user" | "ai";
  text: string;
  sources?: string[];
  structured?: { cause: string; fix: string; drill: string; effect: string } | null;
  feedback?: "good" | "bad" | null;
  backendMessageId?: number;
  fromLiveApi?: boolean;
}

function mapSources(sources: string[] | undefined): string[] {
  if (!sources?.length) return [];
  return sources.map(s =>
    s
      .replace(/_/g, " ")
      .replace(/\b\w/g, ch => ch.toUpperCase())
  );
}

export function AIChatScreen() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(() => {
    const raw = sessionStorage.getItem(DEMO_CONVERSATION_KEY);
    return raw ? Number(raw) : null;
  });
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then(h => {
        if (!cancelled) {
          setApiConnected(h.status === "ok");
          setApiError(null);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setApiConnected(false);
          const msg = err instanceof ApiError ? err.message : "API unreachable";
          setApiError(msg);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || typing) return;
    const userMsg: Message = { id: Date.now(), role: "user", text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setTyping(true);
    setApiError(null);

    try {
      const res = await sendCoachMessage({
        user_id: DEMO_USER_ID,
        conversation_id: conversationId,
        message: text,
      });
      setConversationId(res.conversation_id);
      sessionStorage.setItem(DEMO_CONVERSATION_KEY, String(res.conversation_id));

      const structured = res.structured_output
        ? {
            cause: res.structured_output.cause ?? "",
            fix: res.structured_output.fix ?? "",
            drill: res.structured_output.recommended_drill ?? "",
            effect: res.structured_output.expected_effect ?? "",
          }
        : null;

      const aiMsg: Message = {
        id: Date.now() + 1,
        role: "ai",
        text: res.answer,
        sources: mapSources(res.sources),
        structured,
        feedback: null,
        backendMessageId: res.message_id,
        fromLiveApi: true,
      };
      setApiConnected(true);
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setApiConnected(false);
      const msg =
        err instanceof ApiError
          ? err.message
          : "Cannot reach the coach API. Start the backend (uvicorn :8000) and retry.";
      setApiError(msg);
      const aiMsg: Message = {
        id: Date.now() + 1,
        role: "ai",
        text: `Coach API error: ${msg}\n\nCoach chat requires the backend on :8000 (mock or real LLM).`,
        feedback: null,
      };
      setMessages(prev => [...prev, aiMsg]);
    } finally {
      setTyping(false);
    }
  };

  const setFeedback = (id: number, fb: "good" | "bad") => {
    setMessages(prev => {
      const target = prev.find(m => m.id === id);
      if (target?.backendMessageId) {
        sendFeedback({
          user_id: DEMO_USER_ID,
          message_id: target.backendMessageId,
          feedback_type: fb === "good" ? "helpful" : "not_accurate",
        }).catch(() => {
          /* UI already updated; offline fallback */
        });
      }
      return prev.map(m => (m.id === id ? { ...m, feedback: fb } : m));
    });
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100dvh", background: c.bg }}>
      <div style={{
        background: c.ink,
        padding: "52px 20px 16px",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 16,
                background: c.surface,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Bot size={16} color={c.ink} />
              </div>
              <h1 style={{ color: c.onDark, fontSize: 18, fontWeight: 700 }}>AI Coach</h1>
              <span style={{
                background: apiConnected === false ? "#fecaca" : apiConnected ? "#bbf7d0" : c.surface,
                color: apiConnected === false ? "#991b1b" : apiConnected ? "#166534" : c.muted,
                fontSize: 9, fontWeight: 700, padding: "2px 6px", borderRadius: 8,
              }}>
                {apiConnected === null ? "…" : apiConnected ? "LIVE API" : "OFFLINE"}
              </span>
            </div>
            <p style={{ color: c.onDarkMuted, fontSize: 11, marginTop: 4, marginLeft: 40 }}>
              {apiConnected
                ? "Answers from FastAPI LangGraph workflow"
                : "Start backend at :8000 — coach chat has no offline fallback"}
            </p>
          </div>
          <button
            onClick={() => navigate("/dev")}
            style={{
              background: "rgba(255,255,255,0.08)",
              border: "1px solid rgba(255,255,255,0.15)",
              borderRadius: 8,
              padding: "6px 8px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            <Code2 size={14} color={c.onDarkMuted} />
            <span style={{ color: c.onDarkMuted, fontSize: 10, fontWeight: 600 }}>Dev</span>
          </button>
        </div>
      </div>

      {apiError && (
        <div style={{
          background: "#fef2f2",
          borderBottom: `1px solid #fecaca`,
          color: "#991b1b",
          fontSize: 11,
          padding: "8px 14px",
          flexShrink: 0,
        }}>
          {apiError}
        </div>
      )}

      {/* Messages */}
      <div
        ref={scrollRef}
        style={{ flex: 1, overflowY: "auto", padding: "16px 12px", display: "flex", flexDirection: "column", gap: 12 }}
      >
        {messages.length === 0 && !typing && (
          <div style={{
            margin: "24px 8px",
            padding: "16px",
            borderRadius: 14,
            border: `1px solid ${c.border}`,
            background: c.surface,
          }}>
            <p style={{ color: c.ink, fontSize: 14, fontWeight: 600, marginBottom: 6 }}>Ask about your swing</p>
            <p style={{ color: c.muted, fontSize: 12, lineHeight: 1.6 }}>
              Questions go to the FastAPI coach workflow. Pick a suggestion below or type your own.
            </p>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id} style={{
            display: "flex",
            flexDirection: "column",
            alignItems: msg.role === "user" ? "flex-end" : "flex-start",
            gap: 4,
          }}>
            {msg.role === "ai" && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                <div style={{
                  width: 22, height: 22, borderRadius: 11,
                  background: c.ink,
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <Bot size={12} color={c.surface} />
                </div>
                <span style={{ color: c.subtle, fontSize: 11, fontWeight: 600 }}>AI Coach</span>
                {msg.fromLiveApi && (
                  <span data-testid="coach-live-reply" style={{ color: "#166534", fontSize: 9, fontWeight: 700 }}>
                    LIVE
                  </span>
                )}
              </div>
            )}

            <div style={{
              maxWidth: "88%",
              background: msg.role === "user" ? c.ink : c.surface,
              color: msg.role === "user" ? c.surface : c.ink,
              borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "4px 18px 18px 18px",
              padding: "12px 14px",
              fontSize: 13,
              lineHeight: 1.7,
              border: msg.role === "ai" ? `1px solid ${c.border}` : "none",
              whiteSpace: "pre-wrap",
            }}>
              {msg.text}
            </div>

            {/* Source chips */}
            {msg.role === "ai" && msg.sources && msg.sources.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 2 }}>
                {msg.sources.map(s => (
                  <span key={s} style={{
                    background: c.surface,
                    color: c.muted,
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "2px 8px",
                    borderRadius: 20,
                    border: `1px solid ${c.border}`,
                  }}>
                    {s}
                  </span>
                ))}
              </div>
            )}

            {/* Structured output */}
            {msg.role === "ai" && msg.structured && (
              <div style={{
                background: c.bg,
                borderRadius: 12,
                border: `1px solid ${c.border}`,
                padding: "12px",
                width: "100%",
                maxWidth: "88%",
              }}>
                <p style={{ color: c.muted, fontSize: 10, fontWeight: 700, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Structured output
                </p>
                {[
                  { label: "Root cause", value: msg.structured.cause },
                  { label: "Correction focus", value: msg.structured.fix },
                  { label: "Recommended drill", value: msg.structured.drill },
                  { label: "Expected improvement", value: msg.structured.effect },
                ].map(({ label, value }) => (
                  <div key={label} style={{ display: "flex", gap: 8, marginBottom: 5 }}>
                    <span style={{ color: c.subtle, fontSize: 11, fontWeight: 600, minWidth: 72, flexShrink: 0 }}>{label}</span>
                    <span style={{ color: c.ink, fontSize: 11, lineHeight: 1.5 }}>{value}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Feedback */}
            {msg.role === "ai" && msg.id !== 1 && (
              <div style={{ display: "flex", gap: 8, marginTop: 2 }}>
                <button
                  onClick={() => setFeedback(msg.id, "good")}
                  style={{
                    display: "flex", alignItems: "center", gap: 4,
                    background: msg.feedback === "good" ? c.accentMuted : c.surface,
                    border: `1px solid ${msg.feedback === "good" ? c.ink : c.border}`,
                    borderRadius: 20, padding: "4px 10px",
                    cursor: "pointer", fontSize: 11,
                    color: msg.feedback === "good" ? c.ink : c.muted,
                  }}
                >
                  <ThumbsUp size={11} />
                  Helpful
                </button>
                <button
                  onClick={() => setFeedback(msg.id, "bad")}
                  style={{
                    display: "flex", alignItems: "center", gap: 4,
                    background: msg.feedback === "bad" ? c.accentMuted : c.surface,
                    border: `1px solid ${msg.feedback === "bad" ? c.inkSoft : c.border}`,
                    borderRadius: 20, padding: "4px 10px",
                    cursor: "pointer", fontSize: 11,
                    color: msg.feedback === "bad" ? c.inkSoft : c.muted,
                  }}
                >
                  <ThumbsDown size={11} />
                  Not accurate
                </button>
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {typing && (
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{
              width: 22, height: 22, borderRadius: 11,
              background: c.ink,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Bot size={12} color={c.surface} />
            </div>
            <div style={{
              background: c.surface,
              borderRadius: "4px 18px 18px 18px",
              padding: "10px 14px",
              border: `1px solid ${c.border}`,
              display: "flex",
              gap: 4,
              alignItems: "center",
            }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 6, height: 6, borderRadius: 3,
                  background: c.subtle,
                  animation: `bounce 1.2s ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div style={{ padding: "8px 12px", flexShrink: 0, overflowX: "auto" }}>
          <div style={{ display: "flex", gap: 8, minWidth: "max-content" }}>
            {SUGGESTED.map(q => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                style={{
                  background: c.surface,
                  border: `1.5px solid ${c.border}`,
                  borderRadius: 20,
                  padding: "8px 14px",
                  fontSize: 12,
                  color: c.ink,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  fontWeight: 500,
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div style={{
        background: c.surface,
        borderTop: `1px solid ${c.border}`,
        padding: "10px 12px 24px",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage(input)}
            placeholder="Ask about your swing..."
            style={{
              flex: 1,
              background: c.bg,
              border: `1.5px solid ${c.border}`,
              borderRadius: 22,
              padding: "10px 16px",
              fontSize: 13,
              color: c.ink,
              outline: "none",
            }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || typing}
            style={{
              width: 42, height: 42,
              borderRadius: 21,
              background: input.trim() ? c.ink : c.border,
              border: "none",
              cursor: input.trim() ? "pointer" : "default",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
              transition: "background 0.2s",
            }}
          >
            <Send size={16} color={input.trim() ? c.surface : c.subtle} />
          </button>
        </div>
        <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 6 }}>
          {messages.length > 1 && SUGGESTED.slice(0, 2).map(q => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              style={{
                background: c.accentMuted,
                border: `1px solid ${c.border}`,
                borderRadius: 16,
                padding: "4px 10px",
                fontSize: 11,
                color: c.ink,
                cursor: "pointer",
                fontWeight: 500,
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>
      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); opacity: 0.4; }
          50% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
