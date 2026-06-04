import { useNavigate } from "react-router";
import {
  ChevronLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  LineChart as LineChartIcon,
  Trophy,
  Target,
  Zap,
  Footprints,
  Bot,
  FlaskConical,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import { c } from "../design";

const WEEKLY_DATA = [
  { week: "Wk 1", avg: 73 },
  { week: "Wk 2", avg: 76 },
  { week: "Wk 3", avg: 79 },
  { week: "Wk 4", avg: 82 },
];

const ISSUES_FREQ = [
  { issue: "Upper body opening", count: 18 },
  { issue: "Wrist angle", count: 12 },
  { issue: "Follow", count: 8 },
  { issue: "Tempo", count: 5 },
];

const NEXT_FOCUS = [
  { label: "Direction control", icon: Target, priority: "High" },
  { label: "Impact stability", icon: Zap, priority: "High" },
  { label: "Lower-body lead", icon: Footprints, priority: "Medium" },
];

const STAT_ICONS = [BarChart3, LineChartIcon, Trophy] as const;

export function MonthlyReportScreen() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col min-h-full" style={{ background: c.bg }}>
      <div style={{
        background: c.ink,
        padding: "52px 20px 24px",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <button
            onClick={() => navigate("/")}
            style={{ background: "rgba(255,255,255,0.1)", border: "none", borderRadius: 10, padding: "6px", cursor: "pointer" }}
          >
            <ChevronLeft size={18} color={c.onDark} />
          </button>
          <div>
            <p style={{ color: c.onDarkMuted, fontSize: 12, fontWeight: 600 }}>Monthly report</p>
            <h1 style={{ color: c.onDark, fontSize: 20, fontWeight: 800 }}>This month's swing report</h1>
          </div>
        </div>
        <p style={{ color: c.onDarkMuted, fontSize: 12, marginLeft: 40 }}>June 2024 · 24 analyses</p>
      </div>

      <div className="px-4 py-4 flex flex-col gap-4">

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
          {[
            { label: "Total analyses", value: "24" },
            { label: "Avg. score change", value: "+9 pts" },
            { label: "Best score", value: "87 pts" },
          ].map(({ label, value }, i) => {
            const Icon = STAT_ICONS[i];
            return (
              <div key={label} style={{
                background: c.surface,
                borderRadius: 14,
                padding: "14px 10px",
                textAlign: "center",
                border: `1px solid ${c.border}`,
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: c.accentMuted,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 8px",
                }}>
                  <Icon size={18} color={c.ink} />
                </div>
                <p style={{ color: c.ink, fontSize: 16, fontWeight: 800 }}>{value}</p>
                <p style={{ color: c.subtle, fontSize: 10, marginTop: 2, lineHeight: 1.3 }}>{label}</p>
              </div>
            );
          })}
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <p style={{ color: c.ink, fontSize: 13, fontWeight: 700 }}>Weekly average score</p>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <TrendingUp size={14} color={c.ink} />
              <span style={{ color: c.ink, fontSize: 12, fontWeight: 700 }}>+9 pts</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={130}>
            <BarChart data={WEEKLY_DATA} barSize={28}>
              <CartesianGrid strokeDasharray="3 3" stroke={c.borderLight} vertical={false} />
              <XAxis dataKey="week" tick={{ fontSize: 11, fill: c.subtle }} axisLine={false} tickLine={false} />
              <YAxis domain={[60, 90]} tick={{ fontSize: 10, fill: c.subtle }} axisLine={false} tickLine={false} width={28} />
              <Tooltip
                contentStyle={{ fontSize: 11, borderRadius: 8, border: `1px solid ${c.border}` }}
                formatter={(v: number) => [`${v} pts`, "Average score"]}
              />
              <Bar dataKey="avg" fill={c.chart1} radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <div style={{ background: c.surface, borderRadius: 14, padding: "14px", border: `1px solid ${c.border}` }}>
            <p style={{ color: c.muted, fontSize: 10, fontWeight: 700, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.04em" }}>Most improved metric</p>
            <p style={{ color: c.ink, fontSize: 13, fontWeight: 700 }}>Tempo stability</p>
            <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 4 }}>
              <TrendingUp size={14} color={c.ink} />
              <span style={{ color: c.ink, fontSize: 12, fontWeight: 600 }}>70 → 88 pts</span>
            </div>
          </div>
          <div style={{ background: c.accentMuted, borderRadius: 14, padding: "14px", border: `1px solid ${c.border}` }}>
            <p style={{ color: c.muted, fontSize: 10, fontWeight: 700, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.04em" }}>Most frequent issue</p>
            <p style={{ color: c.ink, fontSize: 13, fontWeight: 700 }}>Early upper-body opening</p>
            <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 4 }}>
              <TrendingDown size={14} color={c.muted} />
              <span style={{ color: c.muted, fontSize: 12, fontWeight: 600 }}>Detected 18×</span>
            </div>
          </div>
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>Issue frequency</p>
          {ISSUES_FREQ.map(({ issue, count }, i) => (
            <div key={issue} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ color: c.muted, fontSize: 12 }}>{issue}</span>
                <span style={{ color: c.ink, fontSize: 12, fontWeight: 600 }}>{count}×</span>
              </div>
              <div style={{ height: 6, background: c.borderLight, borderRadius: 3 }}>
                <div style={{
                  height: "100%",
                  width: `${(count / 18) * 100}%`,
                  background: i === 0 ? c.chart1 : i === 1 ? c.chart2 : c.chart3,
                  borderRadius: 3,
                }} />
              </div>
            </div>
          ))}
        </div>

        <div style={{
          background: c.accentMuted,
          borderRadius: 16,
          padding: "16px",
          border: `1px solid ${c.border}`,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <div style={{
              width: 28, height: 28, borderRadius: 14,
              background: c.ink,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Bot size={14} color={c.surface} />
            </div>
            <p style={{ color: c.ink, fontSize: 13, fontWeight: 700 }}>AI monthly summary</p>
          </div>
          <p style={{ color: c.inkSoft, fontSize: 13, lineHeight: 1.7 }}>
            Your swing tempo stabilized this month, but upper-body rotation timing before impact still needs work. Slice risk is steadily decreasing, and a more consistent backswing path is a major win.
          </p>
          <div style={{
            marginTop: 10,
            borderTop: `1px solid ${c.border}`,
            paddingTop: 10,
            display: "flex",
            gap: 6,
            flexWrap: "wrap",
          }}>
            {["Recent swing history", "User profile", "Golf coaching knowledge"].map(tag => (
              <span key={tag} style={{
                background: c.surface,
                color: c.muted,
                fontSize: 10,
                fontWeight: 600,
                padding: "2px 8px",
                borderRadius: 20,
                border: `1px solid ${c.border}`,
              }}>{tag}</span>
            ))}
          </div>
        </div>

        <div style={{ background: c.surface, borderRadius: 16, padding: "16px", border: `1px solid ${c.border}` }}>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>Focus for next month</p>
          {NEXT_FOCUS.map(({ label, icon: Icon, priority }) => (
            <div key={label} style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              padding: "9px 0",
              borderBottom: `1px solid ${c.borderLight}`,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <Icon size={16} color={c.ink} />
                <span style={{ color: c.ink, fontSize: 13, fontWeight: 500 }}>{label}</span>
              </div>
              <span style={{
                background: c.accentMuted,
                color: c.inkSoft,
                fontSize: 10,
                fontWeight: 700,
                padding: "2px 8px",
                borderRadius: 20,
                border: `1px solid ${c.border}`,
              }}>{priority}</span>
            </div>
          ))}
        </div>

        <button
          onClick={() => navigate("/dev")}
          style={{
            background: c.inkSoft,
            border: "none",
            borderRadius: 12,
            padding: "13px",
            color: c.onDarkMuted,
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 6,
            marginBottom: 8,
          }}
        >
          <FlaskConical size={14} />
          View AI quality panel
        </button>
      </div>
    </div>
  );
}
