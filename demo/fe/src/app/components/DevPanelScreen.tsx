import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { ChevronLeft, CheckCircle, AlertCircle, Clock, DollarSign, Database, Shield } from "lucide-react";
import {
  DEMO_CONVERSATION_KEY,
  getConversationTrace,
  getPromptVersions,
} from "../api/client";
import type { ConversationTrace, PromptVersion } from "../api/types";

const WORKFLOW_STEPS = [
  {
    step: 1,
    label: "Question classification",
    desc: "Classify user questions (swing analysis / progress check / drill request)",
    model: "claude-haiku-4-5",
    latency: "0.2s",
    status: "pass",
  },
  {
    step: 2,
    label: "Swing history retrieval",
    desc: "Vector search over last 10 swings and pose time-series summary",
    model: "RAG (pgvector)",
    latency: "0.4s",
    status: "pass",
  },
  {
    step: 3,
    label: "Golf knowledge retrieval",
    desc: "Search coaching knowledge base for relevant techniques and fixes",
    model: "RAG (pgvector)",
    latency: "0.5s",
    status: "pass",
  },
  {
    step: 4,
    label: "Coaching response generation",
    desc: "Generate coaching response in structured output format",
    model: "claude-sonnet-4-6",
    latency: "0.5s",
    status: "pass",
  },
  {
    step: 5,
    label: "Guardrail application",
    desc: "Block non-golf questions / validate response quality / safety filter",
    model: "Rule-based + LLM",
    latency: "0.2s",
    status: "pass",
  },
];

const RAG_SOURCES = [
  { name: "Golf coaching knowledge base", docs: 2840, updated: "2024.05", topK: 5, score: 0.87 },
  { name: "User swing history", docs: 10, updated: "Live", topK: 3, score: 0.95 },
  { name: "Previous conversations", docs: 24, updated: "Live", topK: 5, score: 0.91 },
];

const FAILURE_CASES = [
  { case: "Insufficient swing data", action: "Default guide response + prompt to upload", freq: "Low" },
  { case: "Ambiguous question", action: "Generate clarification question", freq: "Medium" },
  { case: "Low RAG retrieval confidence", action: "Fallback response + show confidence", freq: "Low" },
  { case: "Guardrail block", action: "Redirect to golf-related questions", freq: "Low" },
];

const VERSIONS = [
  { v: "v0.3", date: "2024.06.04", change: "Structured output + stronger guardrails", current: true },
  { v: "v0.2", date: "2024.05.20", change: "RAG source tagging added", current: false },
  { v: "v0.1", date: "2024.05.01", change: "Initial version", current: false },
];

export function DevPanelScreen() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"workflow" | "rag" | "quality" | "versions">("workflow");
  const [promptVersions, setPromptVersions] = useState<PromptVersion[] | null>(null);
  const [trace, setTrace] = useState<ConversationTrace | null>(null);

  useEffect(() => {
    getPromptVersions()
      .then(setPromptVersions)
      .catch(() => setPromptVersions(null));
  }, []);

  useEffect(() => {
    const raw = sessionStorage.getItem(DEMO_CONVERSATION_KEY);
    if (!raw) return;
    getConversationTrace(Number(raw))
      .then(setTrace)
      .catch(() => setTrace(null));
  }, []);

  const versionRows =
    promptVersions?.map(pv => ({
      v: pv.version,
      date: pv.created_at.slice(0, 10),
      change: `${pv.name}${pv.is_active ? " (active)" : ""}`,
      current: pv.is_active,
    })) ?? VERSIONS;

  const workflowBanner = trace
    ? `LangGraph trace · conversation #${trace.conversation_id} · ${trace.prompt_version} · ${trace.latency_ms ?? "—"}ms`
    : "Full pipeline healthy · total latency 1.8s · prompt v0.3 (mock workflow)";

  return (
    <div className="flex flex-col min-h-full bg-[#0A0F1C]">
      {/* Header */}
      <div style={{ background: "#0A0F1C", padding: "52px 20px 20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <button
            onClick={() => navigate("/coach")}
            style={{ background: "rgba(255,255,255,0.08)", border: "none", borderRadius: 10, padding: "6px", cursor: "pointer" }}
          >
            <ChevronLeft size={18} color="#94A3B8" />
          </button>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <h1 style={{ color: "#F8FAFC", fontSize: 18, fontWeight: 700 }}>AI quality panel</h1>
              <span style={{
                background: "#1E3A5F",
                color: "#60A5FA",
                fontSize: 9, fontWeight: 700,
                padding: "2px 7px", borderRadius: 8,
              }}>DEV</span>
            </div>
            <p style={{ color: "#475569", fontSize: 11, marginTop: 2 }}>AI/LLM Engineer Debug View</p>
          </div>
        </div>

        {/* System metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 6, marginTop: 12 }}>
          {[
            { icon: Clock, label: "Latency", value: "1.8s", color: "#34D399" },
            { icon: DollarSign, label: "Cost", value: "Low", color: "#60A5FA" },
            { icon: Database, label: "Cache", value: "On", color: "#A78BFA" },
            { icon: Shield, label: "Guardrail", value: "Pass", color: "#34D399" },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} style={{
              background: "rgba(255,255,255,0.04)",
              borderRadius: 10,
              padding: "10px 8px",
              textAlign: "center",
              border: "1px solid rgba(255,255,255,0.08)",
            }}>
              <Icon size={14} color={color} style={{ margin: "0 auto 4px" }} />
              <p style={{ color, fontSize: 12, fontWeight: 700 }}>{value}</p>
              <p style={{ color: "#475569", fontSize: 9, marginTop: 1 }}>{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div style={{
        display: "flex",
        background: "rgba(255,255,255,0.04)",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
        padding: "0 16px",
        overflowX: "auto",
        gap: 2,
      }}>
        {(["workflow", "rag", "quality", "versions"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: "none",
              border: "none",
              padding: "10px 14px",
              fontSize: 12,
              fontWeight: activeTab === tab ? 700 : 400,
              color: activeTab === tab ? "#34D399" : "#475569",
              cursor: "pointer",
              borderBottom: activeTab === tab ? "2px solid #34D399" : "2px solid transparent",
              whiteSpace: "nowrap",
            }}
          >
            {tab === "workflow" ? "Workflow" : tab === "rag" ? "RAG sources" : tab === "quality" ? "Quality log" : "Versions"}
          </button>
        ))}
      </div>

      <div style={{ padding: "16px", flex: 1, overflowY: "auto", paddingBottom: 32 }}>

        {/* Workflow tab */}
        {activeTab === "workflow" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{
              background: "rgba(52,211,153,0.08)",
              borderRadius: 10,
              padding: "10px 12px",
              border: "1px solid rgba(52,211,153,0.2)",
              marginBottom: 4,
            }}>
              <p style={{ color: "#34D399", fontSize: 11, lineHeight: 1.5 }}>{workflowBanner}</p>
              {trace && (
                <p style={{ color: "#64748B", fontSize: 10, marginTop: 6, lineHeight: 1.4 }}>
                  Q: {trace.question_type ?? "—"} · chunks: {trace.retrieved_chunk_count} · guardrail:{" "}
                  {trace.guardrail_status ?? "—"}
                </p>
              )}
            </div>
            {WORKFLOW_STEPS.map(({ step, label, desc, model, latency, status }) => (
              <div key={step} style={{
                background: "rgba(255,255,255,0.04)",
                borderRadius: 12,
                padding: "12px",
                border: "1px solid rgba(255,255,255,0.08)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                  <div style={{
                    width: 22, height: 22, borderRadius: 11,
                    background: "#1E3A5F",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0,
                  }}>
                    <span style={{ color: "#60A5FA", fontSize: 10, fontWeight: 700 }}>{step}</span>
                  </div>
                  <span style={{ color: "#F1F5F9", fontSize: 13, fontWeight: 600 }}>{label}</span>
                  <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ color: "#475569", fontSize: 10 }}>{latency}</span>
                    <CheckCircle size={13} color="#34D399" />
                  </div>
                </div>
                <p style={{ color: "#64748B", fontSize: 11, lineHeight: 1.5, marginLeft: 32 }}>{desc}</p>
                <div style={{ marginLeft: 32, marginTop: 5 }}>
                  <span style={{
                    background: "rgba(96,165,250,0.1)",
                    color: "#60A5FA",
                    fontSize: 9, fontWeight: 600,
                    padding: "2px 7px", borderRadius: 6,
                    border: "1px solid rgba(96,165,250,0.2)",
                  }}>{model}</span>
                </div>
              </div>
            ))}

            {/* Latency breakdown */}
            <div style={{
              background: "rgba(255,255,255,0.04)",
              borderRadius: 12,
              padding: "12px",
              border: "1px solid rgba(255,255,255,0.08)",
              marginTop: 4,
            }}>
              <p style={{ color: "#94A3B8", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>Latency breakdown</p>
              {WORKFLOW_STEPS.map(({ step, label, latency }) => (
                <div key={step} style={{ marginBottom: 6 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                    <span style={{ color: "#64748B", fontSize: 10 }}>{label}</span>
                    <span style={{ color: "#94A3B8", fontSize: 10 }}>{latency}</span>
                  </div>
                  <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                    <div style={{
                      height: "100%",
                      width: `${(parseFloat(latency) / 1.8) * 100}%`,
                      background: "#34D399",
                      borderRadius: 2,
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RAG tab */}
        {activeTab === "rag" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {RAG_SOURCES.map(({ name, docs, updated, topK, score }) => (
              <div key={name} style={{
                background: "rgba(255,255,255,0.04)",
                borderRadius: 12,
                padding: "14px",
                border: "1px solid rgba(255,255,255,0.08)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <Database size={14} color="#A78BFA" />
                  <span style={{ color: "#F1F5F9", fontSize: 13, fontWeight: 600 }}>{name}</span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
                  {[
                    { label: "Documents", value: `${docs}` },
                    { label: "Updated", value: updated },
                    { label: "Top-K", value: `${topK}` },
                  ].map(({ label, value }) => (
                    <div key={label} style={{
                      background: "rgba(255,255,255,0.04)",
                      borderRadius: 8,
                      padding: "7px",
                      textAlign: "center",
                    }}>
                      <p style={{ color: "#94A3B8", fontSize: 9 }}>{label}</p>
                      <p style={{ color: "#F1F5F9", fontSize: 12, fontWeight: 600, marginTop: 2 }}>{value}</p>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                    <span style={{ color: "#64748B", fontSize: 10 }}>Avg. similarity score</span>
                    <span style={{ color: "#34D399", fontSize: 10, fontWeight: 600 }}>{score}</span>
                  </div>
                  <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
                    <div style={{
                      height: "100%",
                      width: `${score * 100}%`,
                      background: score > 0.9 ? "#34D399" : "#60A5FA",
                      borderRadius: 3,
                    }} />
                  </div>
                </div>
              </div>
            ))}

            {/* Prompt snippet */}
            <div style={{
              background: "rgba(255,255,255,0.04)",
              borderRadius: 12,
              padding: "14px",
              border: "1px solid rgba(255,255,255,0.08)",
            }}>
              <p style={{ color: "#94A3B8", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>
                System prompt preview (v0.3)
              </p>
              <pre style={{
                color: "#64748B",
                fontSize: 10,
                lineHeight: 1.7,
                overflowX: "auto",
                whiteSpace: "pre-wrap",
                fontFamily: "monospace",
              }}>{`You are an AI swing coach.
Use the user's swing history, golfer profile,
and golf coaching knowledge to deliver
personalized coaching.

[Output Format]
{
  "cause": "root cause",
  "fix": "correction focus",
  "drill": "recommended drill",
  "effect": "expected improvement"
}

[Guardrail]
- Non-golf topics: refuse
- Low confidence: disclose`}</pre>
            </div>
          </div>
        )}

        {/* Quality tab */}
        {activeTab === "quality" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
              <p style={{ color: "#94A3B8", fontSize: 11, fontWeight: 700, marginBottom: 10 }}>Failure case log</p>
              {FAILURE_CASES.map(({ case: c, action, freq }) => (
                <div key={c} style={{
                  borderBottom: "1px solid rgba(255,255,255,0.06)",
                  padding: "10px 0",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                    <AlertCircle size={12} color="#F59E0B" />
                    <span style={{ color: "#F1F5F9", fontSize: 12, fontWeight: 600 }}>{c}</span>
                    <span style={{
                      marginLeft: "auto",
                      background: freq === "Low" ? "rgba(52,211,153,0.15)" : "rgba(245,158,11,0.15)",
                      color: freq === "Low" ? "#34D399" : "#F59E0B",
                      fontSize: 9, fontWeight: 600,
                      padding: "1px 6px", borderRadius: 6,
                    }}>{freq}</span>
                  </div>
                  <p style={{ color: "#64748B", fontSize: 11, lineHeight: 1.5, marginLeft: 18 }}>→ {action}</p>
                </div>
              ))}
            </div>

            {/* Feedback loop */}
            <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
              <p style={{ color: "#94A3B8", fontSize: 11, fontWeight: 700, marginBottom: 10 }}>Feedback loop</p>
              {[
                { label: "Helpful", count: 18, total: 24, color: "#34D399" },
                { label: "Not accurate", count: 6, total: 24, color: "#F87171" },
              ].map(({ label, count, total, color }) => (
                <div key={label} style={{ marginBottom: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ color: "#94A3B8", fontSize: 11 }}>{label}</span>
                    <span style={{ color, fontSize: 11, fontWeight: 600 }}>{count}/{total}</span>
                  </div>
                  <div style={{ height: 6, background: "rgba(255,255,255,0.06)", borderRadius: 3 }}>
                    <div style={{
                      height: "100%",
                      width: `${(count / total) * 100}%`,
                      background: color,
                      borderRadius: 3,
                    }} />
                  </div>
                </div>
              ))}
              <div style={{ marginTop: 10, padding: "10px", background: "rgba(255,255,255,0.04)", borderRadius: 8 }}>
                <p style={{ color: "#64748B", fontSize: 11, lineHeight: 1.5 }}>
                  Adjusting re-ranking weights from negative feedback<br />
                  Prompt A/B test: v0.3 win rate 75%
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Versions tab */}
        {activeTab === "versions" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {versionRows.map(({ v, date, change, current }) => (
              <div key={v} style={{
                background: current ? "rgba(52,211,153,0.06)" : "rgba(255,255,255,0.04)",
                borderRadius: 12,
                padding: "14px",
                border: `1px solid ${current ? "rgba(52,211,153,0.3)" : "rgba(255,255,255,0.08)"}`,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <span style={{
                    background: current ? "#34D399" : "rgba(255,255,255,0.1)",
                    color: current ? "#0A0F1C" : "#64748B",
                    fontSize: 11, fontWeight: 700,
                    padding: "2px 8px", borderRadius: 8,
                  }}>{v}</span>
                  {current && (
                    <span style={{ color: "#34D399", fontSize: 10, fontWeight: 600 }}>Current</span>
                  )}
                  <span style={{ color: "#475569", fontSize: 10, marginLeft: "auto" }}>{date}</span>
                </div>
                <p style={{ color: current ? "#CBD5E1" : "#64748B", fontSize: 12, lineHeight: 1.5 }}>{change}</p>
              </div>
            ))}

            <div style={{
              background: "rgba(255,255,255,0.04)",
              borderRadius: 12,
              padding: "14px",
              border: "1px solid rgba(255,255,255,0.08)",
            }}>
              <p style={{ color: "#94A3B8", fontSize: 11, fontWeight: 700, marginBottom: 8 }}>Cache status</p>
              {[
                { label: "Prompt cache", status: "Enabled", detail: "Anthropic Prompt Caching" },
                { label: "RAG result cache", status: "Enabled", detail: "TTL: 5 min" },
                { label: "Embedding cache", status: "Enabled", detail: "pgvector persistent storage" },
              ].map(({ label, status, detail }) => (
                <div key={label} style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "7px 0",
                  borderBottom: "1px solid rgba(255,255,255,0.04)",
                }}>
                  <div>
                    <p style={{ color: "#F1F5F9", fontSize: 12 }}>{label}</p>
                    <p style={{ color: "#475569", fontSize: 10 }}>{detail}</p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <div style={{ width: 6, height: 6, borderRadius: 3, background: "#34D399" }} />
                    <span style={{ color: "#34D399", fontSize: 11 }}>{status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
