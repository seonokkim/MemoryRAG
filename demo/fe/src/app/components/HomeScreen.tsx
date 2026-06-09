import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { DEMO_USER_ID, getProfile, getSwingSessions } from "../api/client";
import type { SwingSession, UserProfile } from "../api/types";
import {
  TrendingUp,
  ChevronRight,
  MessageCircle,
  User,
  Dumbbell,
  Activity,
  Target,
  Zap,
  Clock,
  Video,
} from "lucide-react";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { c } from "../design";

const scoreData = [
  { s: 68 }, { s: 72 }, { s: 70 }, { s: 75 }, { s: 78 }, { s: 82 },
];

const metrics = [
  { label: "Rhythm", value: 78, icon: Activity },
  { label: "Tempo", value: 85, icon: Clock },
  { label: "Impact", value: 70, icon: Target },
  { label: "Rotation", value: 65, icon: Zap },
];

function ScoreRing({ score }: { score: number }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <svg width={88} height={88} viewBox="0 0 88 88">
      <circle cx={44} cy={44} r={r} fill="none" stroke={c.border} strokeWidth={7} />
      <circle
        cx={44} cy={44} r={r}
        fill="none"
        stroke={c.ink}
        strokeWidth={7}
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 44 44)"
      />
      <text x={44} y={44} textAnchor="middle" dy="0.35em" fill={c.ink} fontSize={22} fontWeight={700}>{score}</text>
      <text x={44} y={62} textAnchor="middle" fill={c.subtle} fontSize={10}>/ 100</text>
    </svg>
  );
}

export function HomeScreen() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [sessions, setSessions] = useState<SwingSession[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [p, s] = await Promise.all([
          getProfile(DEMO_USER_ID),
          getSwingSessions(DEMO_USER_ID),
        ]);
        if (!cancelled) {
          setProfile(p);
          setSessions(s);
        }
      } catch {
        // Demo charts fall back to inline sample data when the API is down.
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const displayName = profile?.name ?? "Riley";
  const recentIssue =
    sessions[0]?.main_issue ??
    profile?.current_main_issue ??
    "Upper body opens quickly\nearly in the downswing";
  const recentScore = sessions[0]?.score ?? 82;
  const chartScores = useMemo(() => {
    if (sessions.length >= 2) {
      return [...sessions]
        .sort(
          (a, b) =>
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        )
        .map(s => ({ s: s.score ?? 0 }));
    }
    return scoreData;
  }, [sessions]);
  const scorePills = useMemo(() => {
    if (sessions.length >= 2) {
      return [...sessions]
        .sort(
          (a, b) =>
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        )
        .map(s => String(s.score ?? "—"));
    }
    return ["68", "72", "70", "75", "78", "82"];
  }, [sessions]);
  const latestSessionId = sessions[0]?.id ?? 1;
  const golferSub =
    profile?.golfer_type ?? "Fast upper-body rotation type";

  return (
    <div className="flex flex-col bg-white min-h-full">
      <div className="bg-[#09090B] px-5 pt-14 pb-8">
        <div className="flex items-center justify-between mb-1">
          <div>
            <p style={{ color: c.onDarkMuted, fontSize: 13, marginBottom: 2 }}>
              AI Swing Coach
            </p>
            <h1 style={{ color: c.onDark, fontSize: 22, fontWeight: 700, lineHeight: 1.3 }}>
              Hi, {displayName}
              {loading ? "…" : ""}
            </h1>
          </div>
          <div
            style={{
              width: 44, height: 44, borderRadius: 22,
              background: c.surface,
              border: `1px solid ${c.border}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: c.ink, fontWeight: 700, fontSize: 18,
            }}
          >
            R
          </div>
        </div>
        <p style={{ color: c.onDarkMuted, fontSize: 13, marginTop: 6 }}>
          Keep improving your swing today
        </p>

        <button
          onClick={() => navigate("/upload")}
          style={{
            marginTop: 20,
            width: "100%",
            background: c.surface,
            border: "none",
            borderRadius: 14,
            padding: "14px 20px",
            color: c.ink,
            fontWeight: 700,
            fontSize: 16,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
          }}
        >
          <Video size={20} />
          Start swing analysis
        </button>
      </div>

      <div className="px-4 py-5 flex flex-col gap-4">

        <div
          style={{
            background: c.bg,
            borderRadius: 16,
            padding: "16px",
            border: `1px solid ${c.border}`,
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p style={{ color: c.muted, fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Recent swing diagnosis
              </p>
              <p style={{ color: c.ink, fontSize: 14, fontWeight: 600, marginTop: 6, lineHeight: 1.5, whiteSpace: "pre-line" }}>
                {recentIssue.replace(/\n/g, "\n")}
              </p>
              <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{
                  background: c.surface,
                  color: c.ink,
                  fontSize: 11,
                  fontWeight: 600,
                  padding: "2px 8px",
                  borderRadius: 20,
                  border: `1px solid ${c.ink}`,
                }}>
                  Needs attention
                </span>
                <span style={{ color: c.subtle, fontSize: 11 }}>2 hours ago</span>
              </div>
            </div>
            <ScoreRing score={recentScore} />
          </div>
          <button
            onClick={() => navigate(`/analysis?sessionId=${latestSessionId}`)}
            style={{
              marginTop: 12,
              width: "100%",
              background: c.surface,
              border: `1px solid ${c.border}`,
              borderRadius: 10,
              padding: "9px",
              color: c.ink,
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 4,
            }}
          >
            View full analysis <ChevronRight size={14} />
          </button>
        </div>

        <div
          style={{
            background: c.surface,
            borderRadius: 16,
            padding: "16px",
            border: `1px solid ${c.border}`,
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <TrendingUp size={16} color={c.ink} />
                <p style={{ color: c.ink, fontSize: 14, fontWeight: 700 }}>
                  Avg. score (last 5 swings)
                </p>
              </div>
              <p style={{ color: c.ink, fontSize: 22, fontWeight: 800, marginTop: 2 }}>
                +7 pts <span style={{ fontSize: 13, color: c.muted, fontWeight: 400 }}>improvement</span>
              </p>
            </div>
            <div style={{ width: 90, height: 48 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartScores}>
                  <Line
                    type="monotone"
                    dataKey="s"
                    stroke={c.chart1}
                    strokeWidth={2}
                    dot={false}
                  />
                  <Tooltip
                    contentStyle={{ fontSize: 11, borderRadius: 8, border: `1px solid ${c.border}` }}
                    formatter={(v: number) => [`${v} pts`]}
                    labelFormatter={() => ""}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            {scorePills.map((s, i) => (
              <div
                key={i}
                style={{
                  background: i === scorePills.length - 1 ? c.ink : c.surface,
                  borderRadius: 8,
                  padding: "3px 9px",
                  fontSize: 12,
                  fontWeight: 600,
                  color: i === scorePills.length - 1 ? c.surface : c.muted,
                  border: `1px solid ${c.border}`,
                }}
              >
                {s}
              </div>
            ))}
          </div>
        </div>

        <div>
          <p style={{ color: c.ink, fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
            Key metrics
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {metrics.map(({ label, value, icon: Icon }) => (
              <div
                key={label}
                style={{
                  background: c.bg,
                  borderRadius: 12,
                  padding: "12px",
                  border: `1px solid ${c.border}`,
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon size={16} color={c.ink} />
                  <span style={{ fontSize: 13, fontWeight: 700, color: c.ink }}>{value}</span>
                </div>
                <p style={{ fontSize: 12, color: c.muted, fontWeight: 500 }}>{label}</p>
                <div style={{
                  marginTop: 6,
                  height: 4,
                  background: c.borderLight,
                  borderRadius: 2,
                  overflow: "hidden",
                }}>
                  <div style={{
                    width: `${value}%`,
                    height: "100%",
                    background: value >= 80 ? c.chart1 : value >= 70 ? c.chart2 : c.chart3,
                    borderRadius: 2,
                    transition: "width 0.8s ease",
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <p style={{ color: c.ink, fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
            Quick actions
          </p>
          <div className="flex flex-col gap-2">
            {[
              { icon: MessageCircle, label: "Ask the AI coach", sub: "Ask anything about your swing", to: "/coach" },
              { icon: User, label: "View my golfer type", sub: golferSub, to: "/profile" },
              { icon: Dumbbell, label: "Today's practice routine", sub: "3 drills · 25 min", to: "/routine" },
            ].map(({ icon: Icon, label, sub, to }) => (
              <button
                key={to}
                onClick={() => navigate(to)}
                style={{
                  background: c.surface,
                  border: `1px solid ${c.border}`,
                  borderRadius: 12,
                  padding: "12px 14px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  textAlign: "left",
                }}
              >
                <div style={{
                  width: 38, height: 38, borderRadius: 10,
                  background: c.accentMuted,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                }}>
                  <Icon size={18} color={c.ink} />
                </div>
                <div className="flex-1">
                  <p style={{ color: c.ink, fontSize: 13, fontWeight: 600 }}>{label}</p>
                  <p style={{ color: c.subtle, fontSize: 11, marginTop: 1 }}>{sub}</p>
                </div>
                <ChevronRight size={16} color={c.subtle} />
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => navigate("/report")}
          style={{
            background: c.ink,
            border: "none",
            borderRadius: 12,
            padding: "13px 16px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 4,
          }}
        >
          <div className="flex items-center gap-3">
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "rgba(255,255,255,0.1)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <TrendingUp size={18} color={c.onDark} />
            </div>
            <div style={{ textAlign: "left" }}>
              <p style={{ color: c.onDark, fontSize: 13, fontWeight: 600 }}>This month's swing report</p>
              <p style={{ color: c.onDarkMuted, fontSize: 11 }}>24 analyses · avg. +9 pts</p>
            </div>
          </div>
          <ChevronRight size={16} color={c.onDarkMuted} />
        </button>
      </div>
    </div>
  );
}
