import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { ChevronLeft, AlertTriangle, CheckCircle, AlertCircle, MessageCircle, TrendingUp } from "lucide-react";
import { getSwingAnalysis } from "../api/client";
import type { SwingAnalysis } from "../api/types";
import { c } from "../design";

const DEFAULT_PHASES = [
  { name: "Address", status: "Stable", tone: c.chart1 },
  { name: "Backswing", status: "Stable", tone: c.chart1 },
  { name: "Top", status: "Caution", tone: c.chart2 },
  { name: "Downswing", status: "Needs work", tone: c.chart3 },
  { name: "Impact", status: "Needs work", tone: c.chart3 },
  { name: "Follow", status: "Caution", tone: c.chart2 },
];

const DEFAULT_METRICS = [
  { label: "Shoulder rotation speed", value: 68, ref: 80, unit: "°/s", status: "low" },
  { label: "Hip rotation timing", value: 72, ref: 80, unit: "ms", status: "low" },
  { label: "Knee stability", value: 85, ref: 80, unit: "%", status: "ok" },
  { label: "Swing tempo", value: 88, ref: 80, unit: "", status: "ok" },
  { label: "Wrist angle (impact)", value: 61, ref: 80, unit: "°", status: "low" },
];

function formatPhaseStatus(raw: string): string {
  const s = raw.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function phaseTone(status: string): string {
  const lower = status.toLowerCase();
  if (lower.includes("stable")) return c.chart1;
  if (lower.includes("caution")) return c.chart2;
  return c.chart3;
}

function ScoreRingLarge({ score }: { score: number }) {
  const r = 54;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <svg width={132} height={132} viewBox="0 0 132 132">
      <circle cx={66} cy={66} r={r} fill="none" stroke={c.border} strokeWidth={10} />
      <circle
        cx={66} cy={66} r={r}
        fill="none"
        stroke={c.ink}
        strokeWidth={10}
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 66 66)"
      />
      <text x={66} y={62} textAnchor="middle" fill={c.ink} fontSize={34} fontWeight={800}>{score}</text>
      <text x={66} y={80} textAnchor="middle" fill={c.subtle} fontSize={13}>/ 100</text>
    </svg>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === "Stable") return <CheckCircle size={14} color={c.chart1} />;
  if (status === "Caution") return <AlertCircle size={14} color={c.chart2} />;
  return <AlertTriangle size={14} color={c.chart3} />;
}

export function AnalysisResultScreen() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = Number(searchParams.get("sessionId") || "1");
  const [analysis, setAnalysis] = useState<SwingAnalysis | null>(null);

  useEffect(() => {
    let cancelled = false;
    getSwingAnalysis(sessionId)
      .then(data => {
        if (!cancelled) setAnalysis(data);
      })
      .catch(() => {
        if (!cancelled) setAnalysis(null);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const score = analysis?.score ?? 82;
  const mainIssue =
    analysis?.main_issue ??
    analysis?.priority_issue ??
    "Upper body opens quickly\nearly in the downswing";
  const evidence =
    analysis?.evidence_text ??
    "In your last 3 swings, early downswing upper-body rotation was faster than average. This pattern correlates strongly with slice outcomes.";
  const priority =
    analysis?.priority_issue ?? "Early upper-body opening before impact";
  const recommended =
    analysis?.recommended_action ?? "Today we recommend 10 minutes of lower-body lead drills.";

  const phases = useMemo(() => {
    const raw = analysis?.phase_summary?.phases;
    if (Array.isArray(raw) && raw.length > 0) {
      return raw.map((p: { name?: string; status?: string }) => {
        const status = formatPhaseStatus(String(p.status ?? "caution"));
        return {
          name: String(p.name ?? "Phase"),
          status,
          tone: phaseTone(status),
        };
      });
    }
    return DEFAULT_PHASES;
  }, [analysis]);

  const metrics = useMemo(() => {
    const pm = analysis?.pose_metrics;
    if (pm && typeof pm === "object") {
      const entries = Object.entries(pm as Record<string, number>);
      if (entries.length > 0) {
        return entries.map(([key, value]) => {
          const label = key
            .replace(/_/g, " ")
            .replace(/\b\w/g, ch => ch.toUpperCase());
          const status = value >= 80 ? "ok" : value >= 70 ? "mid" : "low";
          return {
            label,
            value: Number(value),
            ref: 80,
            unit: key.includes("timing") ? "ms" : key.includes("angle") ? "°" : key.includes("tempo") ? "" : "%",
            status,
          };
        });
      }
    }
    return DEFAULT_METRICS;
  }, [analysis]);

  return (
    <div className="flex flex-col min-h-full" style={{ background: c.bg }}>
      <div className="px-5 pt-12 pb-5" style={{ background: c.ink }}>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/upload")}
            style={{ background: "rgba(255,255,255,0.1)", border: "none", borderRadius: 10, padding: "6px", cursor: "pointer" }}
          >
            <ChevronLeft size={18} color={c.onDark} />
          </button>
          <div>
            <h1 style={{ color: c.onDark, fontSize: 18, fontWeight: 700 }}>Swing analysis results</h1>
            <p style={{ color: c.onDarkMuted, fontSize: 11, marginTop: 1 }}>
              Session #{sessionId} · Driver · Front
            </p>
          </div>
        </div>
      </div>

      <div className="px-4 py-4 flex flex-col gap-4">

        <div style={{
          background: c.surface,
          borderRadius: 16,
          padding: "20px",
          border: `1px solid ${c.border}`,
          display: "flex",
          gap: 16,
          alignItems: "center",
        }}>
          <ScoreRingLarge score={score} />
          <div className="flex-1">
            <div style={{
              background: c.accentMuted,
              borderRadius: 8,
              padding: "6px 10px",
              display: "inline-flex",
              alignItems: "center",
              gap: 5,
              marginBottom: 8,
              border: `1px solid ${c.border}`,
            }}>
              <AlertTriangle size={12} color={c.ink} />
              <span style={{ color: c.ink, fontSize: 11, fontWeight: 700 }}>Main issue</span>
            </div>
            <p style={{ color: c.ink, fontSize: 14, fontWeight: 700, lineHeight: 1.5, whiteSpace: "pre-line" }}>
              {mainIssue}
            </p>
            <div style={{ marginTop: 8, display: "flex", gap: 6 }}>
              <span style={{
                background: c.surface,
                color: c.inkSoft,
                fontSize: 10,
                fontWeight: 600,
                padding: "2px 7px",
                borderRadius: 20,
                border: `1px solid ${c.border}`,
              }}>Slice risk</span>
              <span style={{
                background: c.ink,
                color: c.surface,
                fontSize: 10,
                fontWeight: 600,
                padding: "2px 7px",
                borderRadius: 20,
              }}>Stable tempo</span>
            </div>
          </div>
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
            Swing phase analysis
          </p>
          <div style={{ overflowX: "auto", paddingBottom: 4 }}>
            <div style={{ display: "flex", gap: 8, minWidth: "max-content" }}>
              {phases.map((phase, i) => (
                <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <div style={{
                      width: 40, height: 40,
                      borderRadius: 12,
                      background: c.accentMuted,
                      border: `2px solid ${phase.tone}`,
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      <StatusIcon status={phase.status} />
                    </div>
                  </div>
                  <span style={{ color: c.ink, fontSize: 10, fontWeight: 600, whiteSpace: "nowrap" }}>{phase.name}</span>
                  <span style={{
                    color: phase.tone,
                    fontSize: 9,
                    fontWeight: 600,
                    whiteSpace: "nowrap",
                    background: c.accentMuted,
                    padding: "2px 5px",
                    borderRadius: 8,
                  }}>
                    {phase.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
            Pose time-series metrics
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {metrics.map(m => (
              <div key={m.label}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                  <span style={{ color: c.muted, fontSize: 12 }}>{m.label}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{
                      color: m.status === "ok" ? c.ink : c.muted,
                      fontSize: 12,
                      fontWeight: 700,
                    }}>{m.value}{m.unit}</span>
                    <span style={{ color: c.subtle, fontSize: 11 }}>/ {m.ref}{m.unit}</span>
                  </div>
                </div>
                <div style={{ height: 6, background: c.borderLight, borderRadius: 3, overflow: "hidden" }}>
                  <div style={{
                    height: "100%",
                    width: `${Math.min(100, (m.value / 100) * 100)}%`,
                    background: m.status === "ok" ? c.chart1 : m.value > 70 ? c.chart2 : c.chart3,
                    borderRadius: 3,
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{
          background: c.accentMuted,
          borderRadius: 16,
          padding: "14px 16px",
          border: `1px solid ${c.border}`,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <TrendingUp size={14} color={c.ink} />
            <span style={{ color: c.ink, fontSize: 12, fontWeight: 700 }}>Analysis evidence</span>
          </div>
          <p style={{ color: c.inkSoft, fontSize: 13, lineHeight: 1.6 }}>{evidence}</p>
        </div>

        <div style={{
          background: c.surface,
          borderRadius: 16,
          border: `1.5px solid ${c.ink}`,
          padding: "14px 16px",
        }}>
          <p style={{ color: c.muted, fontSize: 11, fontWeight: 700, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>
            Top priority to fix
          </p>
          <p style={{ color: c.ink, fontSize: 15, fontWeight: 700 }}>{priority}</p>
          <p style={{ color: c.muted, fontSize: 12, marginTop: 4, lineHeight: 1.5 }}>{recommended}</p>
        </div>

        <button
          onClick={() => navigate("/coach")}
          style={{
            background: c.ink,
            border: "none",
            borderRadius: 14,
            padding: "15px",
            color: c.surface,
            fontSize: 15,
            fontWeight: 700,
            cursor: "pointer",
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            marginBottom: 8,
          }}
        >
          <MessageCircle size={18} />
          Ask the AI coach for details
        </button>
      </div>
    </div>
  );
}
