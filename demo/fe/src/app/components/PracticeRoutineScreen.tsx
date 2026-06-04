import { useState } from "react";
import {
  Clock,
  ChevronRight,
  CheckCircle,
  Play,
  Target,
  Footprints,
  Dumbbell,
  Timer,
  Trophy,
  Bot,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { c } from "../design";

const DRILLS: {
  id: number;
  name: string;
  time: number;
  difficulty: string;
  issue: string;
  reason: string;
  detail: string;
  steps: string[];
  icon: LucideIcon;
}[] = [
  {
    id: 1,
    name: "Lower-body lead drill",
    time: 10,
    difficulty: "Beginner",
    issue: "Upper body leads downswing",
    reason: "Recommended to reduce early upper-body opening in the downswing",
    detail: "Swing with your heels slightly lifted to feel the lower body leading the motion.",
    steps: ["Address → lift right heel slightly", "Focus weight on right foot in backswing", "Start downswing rotation from left hip"],
    icon: Footprints,
  },
  {
    id: 2,
    name: "Shoulder closure drill",
    time: 8,
    difficulty: "Intermediate",
    issue: "Unstable wrist angle at impact",
    reason: "Recommended to stabilize clubface before impact",
    detail: "Keep shoulders closed through the downswing so they do not open toward the target too early.",
    steps: ["Half swing at hip height", "Keep shoulder line pointing right of target", "Maintain closure through impact and follow-through"],
    icon: Dumbbell,
  },
  {
    id: 3,
    name: "Tempo consistency drill",
    time: 7,
    difficulty: "Beginner",
    issue: "Unstable rhythm",
    reason: "Recommended to keep rhythm and tempo consistent",
    detail: "Use a 1-2-3 count to train consistent backswing–top–impact timing.",
    steps: ["'One' – slow backswing", "'Two' – pause 0.3s at the top", "'Three' – smooth downswing"],
    icon: Timer,
  },
];

export function PracticeRoutineScreen() {
  const [expanded, setExpanded] = useState<number | null>(null);
  const [started, setStarted] = useState<Set<number>>(new Set());
  const [done, setDone] = useState<Set<number>>(new Set());

  const toggle = (id: number) => setExpanded(prev => prev === id ? null : id);
  const startDrill = (id: number) => {
    setStarted(prev => new Set(prev).add(id));
    setTimeout(() => setDone(prev => new Set(prev).add(id)), 3000);
  };

  const totalTime = DRILLS.reduce((a, d) => a + d.time, 0);
  const doneCount = done.size;

  return (
    <div className="flex flex-col min-h-full" style={{ background: c.bg }}>
      <div style={{
        background: c.ink,
        padding: "52px 20px 24px",
      }}>
        <p style={{ color: c.onDarkMuted, fontSize: 12, fontWeight: 600, marginBottom: 4 }}>AI personalized routine</p>
        <h1 style={{ color: c.onDark, fontSize: 22, fontWeight: 800 }}>Today's practice routine</h1>
        <div style={{ marginTop: 12, display: "flex", gap: 12 }}>
          <div style={{
            background: "rgba(255,255,255,0.08)",
            borderRadius: 10, padding: "8px 14px",
            display: "flex", alignItems: "center", gap: 6,
          }}>
            <Clock size={14} color={c.onDarkMuted} />
            <span style={{ color: c.onDark, fontSize: 13, fontWeight: 600 }}>{totalTime} min</span>
          </div>
          <div style={{
            background: "rgba(255,255,255,0.08)",
            borderRadius: 10, padding: "8px 14px",
            display: "flex", alignItems: "center", gap: 6,
          }}>
            <Target size={14} color={c.onDarkMuted} />
            <span style={{ color: c.onDark, fontSize: 13, fontWeight: 600 }}>{DRILLS.length} drills</span>
          </div>
          <div style={{
            background: doneCount === DRILLS.length ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.08)",
            borderRadius: 10, padding: "8px 14px",
            display: "flex", alignItems: "center", gap: 6,
          }}>
            <CheckCircle size={14} color={c.onDark} />
            <span style={{ color: c.onDark, fontSize: 13, fontWeight: 600 }}>{doneCount}/{DRILLS.length} done</span>
          </div>
        </div>

        <div style={{ marginTop: 14, height: 4, background: "rgba(255,255,255,0.15)", borderRadius: 2 }}>
          <div style={{
            height: "100%",
            width: `${(doneCount / DRILLS.length) * 100}%`,
            background: c.surface,
            borderRadius: 2,
            transition: "width 0.5s ease",
          }} />
        </div>
      </div>

      <div style={{
        margin: "12px 16px 0",
        background: c.surface,
        borderRadius: 12,
        padding: "10px 14px",
        border: `1px solid ${c.border}`,
        display: "flex",
        gap: 8,
        alignItems: "flex-start",
      }}>
        <Bot size={14} color={c.ink} style={{ marginTop: 2, flexShrink: 0 }} />
        <p style={{ color: c.muted, fontSize: 11, lineHeight: 1.6 }}>
          AI personalized this routine around today's <strong style={{ color: c.ink }}>early upper-body opening before impact</strong>.
        </p>
      </div>

      <div className="px-4 py-4 flex flex-col gap-3">
        {DRILLS.map((drill, idx) => {
          const isDone = done.has(drill.id);
          const isStarted = started.has(drill.id);
          const isExpanded = expanded === drill.id;
          const DrillIcon = drill.icon;

          return (
            <div
              key={drill.id}
              style={{
                background: isDone ? c.accentMuted : c.surface,
                borderRadius: 16,
                border: `1.5px solid ${isDone ? c.ink : c.border}`,
                overflow: "hidden",
                transition: "all 0.2s",
              }}
            >
              <button
                onClick={() => toggle(drill.id)}
                style={{
                  width: "100%",
                  background: "none",
                  border: "none",
                  padding: "14px 16px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  textAlign: "left",
                }}
              >
                <div style={{
                  width: 44, height: 44,
                  borderRadius: 12,
                  background: isDone ? c.ink : c.accentMuted,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                }}>
                  {isDone ? <CheckCircle size={22} color={c.surface} /> : <DrillIcon size={20} color={c.ink} />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
                    <span style={{
                      background: c.accentMuted,
                      color: c.inkSoft,
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "1px 6px",
                      borderRadius: 8,
                      border: `1px solid ${c.border}`,
                    }}>{drill.difficulty}</span>
                    <span style={{ color: c.subtle, fontSize: 10 }}>Related: {drill.issue}</span>
                  </div>
                  <p style={{ color: isDone ? c.ink : c.ink, fontSize: 14, fontWeight: 700 }}>
                    {idx + 1}. {drill.name}
                  </p>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 2 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
                      <Clock size={11} color={c.subtle} />
                      <span style={{ color: c.subtle, fontSize: 11 }}>{drill.time} min</span>
                    </div>
                    {isDone && (
                      <span style={{ color: c.ink, fontSize: 11, fontWeight: 600 }}>Done</span>
                    )}
                  </div>
                </div>

                <ChevronRight
                  size={16}
                  color={c.subtle}
                  style={{ transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)", transition: "transform 0.2s" }}
                />
              </button>

              {isExpanded && (
                <div style={{ padding: "0 16px 16px", borderTop: `1px solid ${c.borderLight}` }}>
                  <div style={{
                    background: c.bg,
                    borderRadius: 10,
                    padding: "10px 12px",
                    marginBottom: 10,
                    marginTop: 10,
                    border: `1px solid ${c.border}`,
                  }}>
                    <p style={{ color: c.ink, fontSize: 11, fontWeight: 600, marginBottom: 2 }}>Why recommended</p>
                    <p style={{ color: c.muted, fontSize: 12, lineHeight: 1.5 }}>{drill.reason}</p>
                  </div>

                  <p style={{ color: c.muted, fontSize: 12, lineHeight: 1.6, marginBottom: 10 }}>{drill.detail}</p>

                  <p style={{ color: c.ink, fontSize: 12, fontWeight: 700, marginBottom: 6 }}>Steps</p>
                  {drill.steps.map((step, i) => (
                    <div key={i} style={{ display: "flex", gap: 8, marginBottom: 5 }}>
                      <div style={{
                        width: 18, height: 18, borderRadius: 9,
                        background: c.ink,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0, marginTop: 1,
                      }}>
                        <span style={{ color: c.surface, fontSize: 9, fontWeight: 700 }}>{i + 1}</span>
                      </div>
                      <p style={{ color: c.muted, fontSize: 12, lineHeight: 1.5 }}>{step}</p>
                    </div>
                  ))}

                  <button
                    onClick={() => startDrill(drill.id)}
                    disabled={isDone}
                    style={{
                      marginTop: 12,
                      width: "100%",
                      background: isDone ? c.borderLight : isStarted ? c.accentMuted : c.ink,
                      border: isStarted && !isDone ? `1px solid ${c.border}` : "none",
                      borderRadius: 12,
                      padding: "12px",
                      color: isDone ? c.subtle : isStarted ? c.ink : c.surface,
                      fontSize: 14,
                      fontWeight: 700,
                      cursor: isDone ? "default" : "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 6,
                    }}
                  >
                    {isDone ? (
                      <><CheckCircle size={16} /> Done</>
                    ) : isStarted ? (
                      <><Timer size={16} /> In progress...</>
                    ) : (
                      <><Play size={16} /> Start</>
                    )}
                  </button>
                </div>
              )}
            </div>
          );
        })}

        {doneCount === DRILLS.length && (
          <div style={{
            background: c.surface,
            borderRadius: 16,
            padding: "20px",
            textAlign: "center",
            border: `1px solid ${c.ink}`,
          }}>
            <Trophy size={32} color={c.ink} style={{ margin: "0 auto 8px" }} />
            <p style={{ color: c.ink, fontSize: 16, fontWeight: 800, marginBottom: 4 }}>
              Routine complete
            </p>
            <p style={{ color: c.muted, fontSize: 12, lineHeight: 1.5 }}>
              You finished 25 minutes of practice.<br />Check your next swing analysis for improvement.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
