import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { ChevronLeft, Database, Shield } from "lucide-react";
import {
  DEMO_CONVERSATION_KEY,
  getConversationTrace,
  getPromptVersions,
} from "../api/client";
import type { ConversationTrace, PromptVersion } from "../api/types";

const GRAPH_NODES: { key: string; label: string; desc: string }[] = [
  { key: "load_context", label: "Load context", desc: "Recent messages from MySQL" },
  { key: "classify_question", label: "Classify question", desc: "Route by question type" },
  { key: "retrieve_profile", label: "Retrieve profile", desc: "User profile and goals" },
  { key: "retrieve_swing_history", label: "Swing history", desc: "Recent swing sessions" },
  { key: "retrieve_memory", label: "Long-term memory", desc: "Stored coaching memories" },
  { key: "retrieve_knowledge", label: "Knowledge retrieval", desc: "SQL / vector knowledge chunks" },
  { key: "invoke_tools", label: "Agent tools", desc: "Allowlisted LangChain tools" },
  { key: "generate_answer", label: "Generate answer", desc: "Structured coaching JSON" },
  { key: "validate_output", label: "Validate output", desc: "Pydantic schema check" },
  { key: "evaluate_answer", label: "Quality evaluation", desc: "Confidence and grounding checks" },
  { key: "rewrite_query", label: "Rewrite query", desc: "Quality-loop retry retrieval" },
  { key: "fallback_answer", label: "Fallback answer", desc: "Safe response when quality fails" },
  { key: "guardrail", label: "Guardrail", desc: "Safety and scope checks" },
  { key: "save_messages", label: "Save messages", desc: "Persist user and assistant turns" },
  { key: "update_memory", label: "Update memory", desc: "Extract long-term memories" },
  { key: "log_eval", label: "Log evaluation", desc: "eval_logs row + trace metadata" },
];

type Tab = "workflow" | "rag" | "quality" | "versions";

function formatPayload(payload: unknown): string {
  if (payload == null) return "—";
  if (typeof payload === "string") return payload;
  try {
    return JSON.stringify(payload, null, 2);
  } catch {
    return String(payload);
  }
}

export function DevPanelScreen() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<Tab>("workflow");
  const [promptVersions, setPromptVersions] = useState<PromptVersion[] | null>(null);
  const [versionsError, setVersionsError] = useState<string | null>(null);
  const [trace, setTrace] = useState<ConversationTrace | null>(null);
  const [traceError, setTraceError] = useState<string | null>(null);

  useEffect(() => {
    getPromptVersions()
      .then(rows => {
        setPromptVersions(rows);
        setVersionsError(null);
      })
      .catch(() => {
        setPromptVersions([]);
        setVersionsError("Could not load prompt versions from /api/dev/prompt-versions");
      });
  }, []);

  useEffect(() => {
    const raw = sessionStorage.getItem(DEMO_CONVERSATION_KEY);
    if (!raw) {
      setTrace(null);
      setTraceError("No coach conversation in this session — send a message on the Coach screen first.");
      return;
    }
    getConversationTrace(Number(raw))
      .then(row => {
        setTrace(row);
        setTraceError(null);
      })
      .catch(() => {
        setTrace(null);
        setTraceError(`Could not load trace for conversation #${raw}`);
      });
  }, []);

  const workflowSteps = useMemo(() => {
    const nodeTrace = trace?.trace ?? {};
    return GRAPH_NODES.filter(node => node.key in nodeTrace).map(node => ({
      ...node,
      payload: nodeTrace[node.key],
    }));
  }, [trace]);

  const llmLabel = trace?.llm_provider
    ? `${trace.llm_provider}${trace.llm_model ? ` · ${trace.llm_model}` : ""}`
    : "—";

  return (
    <div className="flex min-h-full flex-col bg-[#0A0F1C]">
      <div className="px-5 pb-5 pt-[52px]">
        <div className="mb-3 flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate("/coach")}
            className="cursor-pointer rounded-[10px] border-0 bg-white/10 p-1.5"
          >
            <ChevronLeft size={18} color="#94A3B8" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-[#F8FAFC]">Coach debug panel</h1>
              <span className="rounded-lg bg-[#1E3A5F] px-1.5 py-0.5 text-[9px] font-bold text-[#60A5FA]">
                DEV
              </span>
            </div>
            <p className="mt-0.5 text-[11px] text-[#475569]">
              LangGraph trace and prompt versions from the FastAPI backend
            </p>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-1.5 sm:grid-cols-4">
          {[
            { label: "Latency", value: trace?.latency_ms != null ? `${trace.latency_ms}ms` : "—" },
            { label: "LLM", value: llmLabel },
            { label: "Chunks", value: trace ? String(trace.retrieved_chunk_count) : "—" },
            {
              label: "Guardrail",
              value: trace?.guardrail_status ?? "—",
            },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="rounded-[10px] border border-white/10 bg-white/5 px-2 py-2.5 text-center"
            >
              <p className="truncate text-[11px] font-bold text-[#34D399]">{value}</p>
              <p className="mt-0.5 text-[9px] text-[#475569]">{label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-0.5 overflow-x-auto border-b border-white/10 bg-white/5 px-4">
        {(
          [
            ["workflow", "Workflow"],
            ["rag", "Retrieval"],
            ["quality", "Quality"],
            ["versions", "Versions"],
          ] as const
        ).map(([tab, label]) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className="cursor-pointer border-0 bg-transparent px-3.5 py-2.5 text-xs whitespace-nowrap"
            style={{
              fontWeight: activeTab === tab ? 700 : 400,
              color: activeTab === tab ? "#34D399" : "#475569",
              borderBottom: activeTab === tab ? "2px solid #34D399" : "2px solid transparent",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 pb-8">
        {activeTab === "workflow" && (
          <div className="flex flex-col gap-2">
            {trace ? (
              <div className="mb-1 rounded-[10px] border border-emerald-500/20 bg-emerald-500/10 px-3 py-2.5">
                <p className="text-[11px] leading-relaxed text-[#34D399]">
                  Conversation #{trace.conversation_id} · {trace.workflow} · prompt{" "}
                  {trace.prompt_version}
                  {trace.question_type ? ` · ${trace.question_type}` : ""}
                </p>
              </div>
            ) : (
              <p className="text-[11px] text-[#94A3B8]">{traceError}</p>
            )}

            {workflowSteps.length === 0 && trace && (
              <p className="text-[11px] text-[#64748B]">No per-node trace payload on this conversation.</p>
            )}

            {workflowSteps.map(({ key, label, desc, payload }) => (
              <div
                key={key}
                className="rounded-xl border border-white/10 bg-white/5 p-3"
              >
                <p className="text-[13px] font-semibold text-[#F1F5F9]">{label}</p>
                <p className="mt-1 text-[11px] text-[#64748B]">{desc}</p>
                <pre className="mt-2 overflow-x-auto rounded-lg bg-black/30 p-2 font-mono text-[10px] leading-relaxed text-[#94A3B8]">
                  {formatPayload(payload)}
                </pre>
              </div>
            ))}
          </div>
        )}

        {activeTab === "rag" && (
          <div className="flex flex-col gap-2">
            {!trace ? (
              <p className="text-[11px] text-[#94A3B8]">{traceError}</p>
            ) : (
              <>
                <div className="rounded-xl border border-white/10 bg-white/5 p-3.5">
                  <div className="mb-2 flex items-center gap-2">
                    <Database size={14} color="#A78BFA" />
                    <span className="text-[13px] font-semibold text-[#F1F5F9]">Retrieved sources</span>
                  </div>
                  {trace.retrieved_sources.length === 0 ? (
                    <p className="text-[11px] text-[#64748B]">No sources recorded for this turn.</p>
                  ) : (
                    <ul className="list-inside list-disc text-[11px] text-[#CBD5E1]">
                      {trace.retrieved_sources.map(source => (
                        <li key={source}>{source}</li>
                      ))}
                    </ul>
                  )}
                  <p className="mt-3 text-[10px] text-[#64748B]">
                    Knowledge chunks retrieved: {trace.retrieved_chunk_count}
                  </p>
                </div>

                {"retrieve_knowledge" in (trace.trace ?? {}) && (
                  <div className="rounded-xl border border-white/10 bg-white/5 p-3.5">
                    <p className="mb-2 text-[11px] font-bold text-[#94A3B8]">retrieve_knowledge payload</p>
                    <pre className="overflow-x-auto font-mono text-[10px] leading-relaxed text-[#64748B]">
                      {formatPayload(trace.trace.retrieve_knowledge)}
                    </pre>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "quality" && (
          <div className="flex flex-col gap-2">
            {!trace ? (
              <p className="text-[11px] text-[#94A3B8]">{traceError}</p>
            ) : (
              <div className="rounded-xl border border-white/10 bg-white/5 p-3.5">
                <div className="mb-3 flex items-center gap-2">
                  <Shield size={14} color="#34D399" />
                  <span className="text-[13px] font-semibold text-[#F1F5F9]">Quality and guardrails</span>
                </div>
                {[
                  ["Quality status", trace.quality_status ?? "—"],
                  ["Guardrail", trace.guardrail_status ?? "—"],
                  ["Failure type", trace.failure_type ?? "—"],
                  ["Retries", trace.retry_count != null ? String(trace.retry_count) : "—"],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex justify-between border-b border-white/5 py-2 text-[11px] last:border-0"
                  >
                    <span className="text-[#64748B]">{label}</span>
                    <span className="font-semibold text-[#F1F5F9]">{value}</span>
                  </div>
                ))}

                {"evaluate_answer" in (trace.trace ?? {}) && (
                  <pre className="mt-3 overflow-x-auto rounded-lg bg-black/30 p-2 font-mono text-[10px] text-[#94A3B8]">
                    {formatPayload(trace.trace.evaluate_answer)}
                  </pre>
                )}
                {"guardrail" in (trace.trace ?? {}) && (
                  <pre className="mt-2 overflow-x-auto rounded-lg bg-black/30 p-2 font-mono text-[10px] text-[#94A3B8]">
                    {formatPayload(trace.trace.guardrail)}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === "versions" && (
          <div className="flex flex-col gap-2">
            {versionsError && (
              <p className="text-[11px] text-amber-400/90">{versionsError}</p>
            )}
            {promptVersions === null ? (
              <p className="text-[11px] text-[#64748B]">Loading prompt versions…</p>
            ) : promptVersions.length === 0 ? (
              <p className="text-[11px] text-[#64748B]">No prompt versions returned from the API.</p>
            ) : (
              promptVersions.map(pv => (
                <div
                  key={pv.version}
                  className="rounded-xl border p-3.5"
                  style={{
                    background: pv.is_active ? "rgba(52,211,153,0.06)" : "rgba(255,255,255,0.04)",
                    borderColor: pv.is_active ? "rgba(52,211,153,0.3)" : "rgba(255,255,255,0.08)",
                  }}
                >
                  <div className="mb-1.5 flex items-center gap-2">
                    <span
                      className="rounded-lg px-2 py-0.5 text-[11px] font-bold"
                      style={{
                        background: pv.is_active ? "#34D399" : "rgba(255,255,255,0.1)",
                        color: pv.is_active ? "#0A0F1C" : "#64748B",
                      }}
                    >
                      {pv.version}
                    </span>
                    {pv.is_active && (
                      <span className="text-[10px] font-semibold text-[#34D399]">Active</span>
                    )}
                    <span className="ml-auto text-[10px] text-[#475569]">
                      {pv.created_at.slice(0, 10)}
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed text-[#CBD5E1]">{pv.name}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
