import { useNavigate } from "react-router";
import { TrendingUp, TrendingDown, BarChart3, Brain, Calendar, Check } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { c } from "../design";

const SWING_HISTORY = [
  { label: "#1", score: 68, slice: 72, tempo: 70 },
  { label: "#2", score: 72, slice: 68, tempo: 73 },
  { label: "#3", score: 70, slice: 70, tempo: 75 },
  { label: "#4", score: 75, slice: 62, tempo: 78 },
  { label: "#5", score: 78, slice: 58, tempo: 80 },
  { label: "#6", score: 74, slice: 60, tempo: 82 },
  { label: "#7", score: 80, slice: 54, tempo: 84 },
  { label: "#8", score: 79, slice: 56, tempo: 85 },
  { label: "#9", score: 81, slice: 50, tempo: 87 },
  { label: "#10", score: 82, slice: 48, tempo: 88 },
];

const STRENGTHS = [
  "Backswing path is consistent",
  "Swing tempo is stable",
  "Address posture is repeatable",
];

const WEAKNESSES = [
  "Upper body opens quickly early in the downswing",
  "Wrist angle varies through impact",
  "Follow-through completion is low",
];

const MEMORY_ISSUES = [
  { label: "Early upper-body opening", count: 8, trend: "persist" },
  { label: "Wrist angle at impact", count: 5, trend: "improve" },
  { label: "Incomplete follow-through", count: 3, trend: "improve" },
];

const IMPROVEMENTS = [
  "Swing tempo: 70 → 88 pts (+18 pts)",
  "Backswing path stability: 65 → 82 pts",
  "Address consistency: +12 pts",
];

export function GolferProfileScreen() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col min-h-full" style={{ background: c.bg }}>
      <div style={{
        background: c.ink,
        padding: "52px 20px 24px",
      }}>
        <p style={{ color: c.onDarkMuted, fontSize: 12, fontWeight: 600, marginBottom: 4 }}>My golfer type</p>
        <h1 style={{ color: c.onDark, fontSize: 22, fontWeight: 800, lineHeight: 1.3 }}>
          Fast upper-body<br />rotation golfer
        </h1>
        <div style={{
          marginTop: 12,
          background: "rgba(255,255,255,0.06)",
          borderRadius: 12,
          padding: "10px 14px",
          display: "flex",
          alignItems: "center",
          gap: 8,
          border: "1px solid rgba(255,255,255,0.08)",
        }}>
          <BarChart3 size={16} color={c.onDarkMuted} />
          <p style={{ color: c.onDarkMuted, fontSize: 12, lineHeight: 1.5 }}>
            Direction can vary, but swing tempo tends to stay stable.
          </p>
        </div>
      </div>

      <div className="px-4 py-4 flex flex-col gap-4">

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
            <Brain size={15} color={c.ink} />
            <p style={{ color: c.ink, fontSize: 13, fontWeight: 700 }}>Long-term memory summary</p>
            <span style={{
              background: c.accentMuted,
              color: c.muted,
              fontSize: 10,
              fontWeight: 600,
              padding: "1px 6px",
              borderRadius: 8,
              border: `1px solid ${c.border}`,
            }}>Last 10 swings</span>
          </div>

          <p style={{ color: c.muted, fontSize: 12, marginBottom: 10, lineHeight: 1.6 }}>
            Across 10 analyzed swings, early upper-body opening in the downswing repeats,
            while tempo and backswing path keep improving.
          </p>

          <p style={{ color: c.ink, fontSize: 12, fontWeight: 700, marginBottom: 6 }}>Recurring issues</p>
          {MEMORY_ISSUES.map(({ label, count, trend }) => (
            <div key={label} style={{
              display: "flex", alignItems: "center",
              justifyContent: "space-between",
              padding: "7px 0",
              borderBottom: `1px solid ${c.borderLight}`,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{
                  width: 6, height: 6, borderRadius: 3,
                  background: trend === "persist" ? c.ink : c.chart2,
                }} />
                <span style={{ color: c.ink, fontSize: 12 }}>{label}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ color: c.muted, fontSize: 11 }}>{count} occurrences</span>
                {trend === "persist"
                  ? <TrendingDown size={12} color={c.muted} />
                  : <TrendingUp size={12} color={c.ink} />
                }
              </div>
            </div>
          ))}

          <p style={{ color: c.ink, fontSize: 12, fontWeight: 700, marginTop: 10, marginBottom: 6 }}>Improvements</p>
          {IMPROVEMENTS.map(item => (
            <div key={item} style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "5px 0",
            }}>
              <div style={{
                width: 16, height: 16, borderRadius: 8,
                background: c.ink,
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
              }}>
                <Check size={10} color={c.surface} />
              </div>
              <span style={{ color: c.muted, fontSize: 12 }}>{item}</span>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <div style={{ background: c.surface, borderRadius: 14, padding: "14px", border: `1px solid ${c.border}` }}>
            <p style={{ color: c.ink, fontSize: 11, fontWeight: 700, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.04em" }}>Strengths</p>
            {STRENGTHS.map(s => (
              <p key={s} style={{ color: c.inkSoft, fontSize: 11, marginBottom: 5, lineHeight: 1.5 }}>· {s}</p>
            ))}
          </div>
          <div style={{ background: c.accentMuted, borderRadius: 14, padding: "14px", border: `1px solid ${c.border}` }}>
            <p style={{ color: c.muted, fontSize: 11, fontWeight: 700, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.04em" }}>Weaknesses</p>
            {WEAKNESSES.map(s => (
              <p key={s} style={{ color: c.inkSoft, fontSize: 11, marginBottom: 5, lineHeight: 1.5 }}>· {s}</p>
            ))}
          </div>
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 4 }}>Last 10 swings trend</p>
          <p style={{ color: c.muted, fontSize: 11, marginBottom: 14 }}>Score / slice risk / tempo stability</p>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={SWING_HISTORY}>
              <CartesianGrid strokeDasharray="3 3" stroke={c.borderLight} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 9, fill: c.subtle }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={[40, 100]}
                tick={{ fontSize: 9, fill: c.subtle }}
                axisLine={false}
                tickLine={false}
                width={28}
              />
              <Tooltip
                contentStyle={{ fontSize: 11, borderRadius: 8, border: `1px solid ${c.border}` }}
              />
              <Legend
                wrapperStyle={{ fontSize: 10, paddingTop: 8 }}
                iconType="circle"
                iconSize={6}
              />
              <Line
                type="monotone" dataKey="score" name="Score"
                stroke={c.chart1} strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 4 }}
              />
              <Line
                type="monotone" dataKey="slice" name="Slice risk"
                stroke={c.chart2} strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 4 }}
                strokeDasharray="4 2"
              />
              <Line
                type="monotone" dataKey="tempo" name="Tempo stability"
                stroke={c.chart3} strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div style={{
            marginTop: 12,
            background: c.bg,
            borderRadius: 10,
            padding: "8px 12px",
            fontSize: 11,
            color: c.muted,
            lineHeight: 1.5,
            border: `1px solid ${c.border}`,
          }}>
            Slice risk is steadily decreasing (72 → 48), while score and tempo are trending up.
          </div>
        </div>

        <button
          onClick={() => navigate("/report")}
          style={{
            background: c.ink,
            border: "none",
            borderRadius: 12,
            padding: "14px",
            cursor: "pointer",
            color: c.surface,
            fontSize: 14,
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            marginBottom: 8,
          }}
        >
          <Calendar size={16} />
          View this month's report
        </button>
      </div>
    </div>
  );
}
