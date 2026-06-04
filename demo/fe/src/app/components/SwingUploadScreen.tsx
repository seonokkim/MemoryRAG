import { useState } from "react";
import { useNavigate } from "react-router";
import { Upload, Camera, ChevronLeft, CheckCircle, Bot } from "lucide-react";
import { motion } from "motion/react";
import { createSwingSession, DEMO_USER_ID } from "../api/client";
import { c } from "../design";

const VIEWS = ["Front", "Side", "Front + Side"];
const CLUBS = ["Driver", "Iron", "Wedge"];
const CONCERNS = ["Slice", "Lack of distance", "Inconsistent contact", "Unstable impact"];

const STEPS = [
  "Extracting video frames",
  "Pose time-series analysis",
  "Swing phase segmentation",
  "Generating coaching feedback",
];

export function SwingUploadScreen() {
  const navigate = useNavigate();
  const [view, setView] = useState("Front");
  const [club, setClub] = useState("Driver");
  const [concerns, setConcerns] = useState<string[]>(["Slice"]);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [uploaded, setUploaded] = useState(false);

  const toggleConcern = (c: string) => {
    setConcerns(prev =>
      prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]
    );
  };

  const startAnalysis = () => {
    setLoading(true);
    setStep(0);
    let sessionId: number | null = null;
    const viewType = view === "Front + Side" ? "Front" : view;
    const concern = concerns.length ? concerns.join(", ") : "Slice";

    createSwingSession(DEMO_USER_ID, {
      club_type: club,
      view_type: viewType,
      concern,
      video_url: "file://data/uploads/mock_upload.mp4",
    })
      .then(session => {
        sessionId = session.id;
      })
      .catch(() => {
        sessionId = null;
      });

    const interval = setInterval(() => {
      setStep(prev => {
        if (prev >= STEPS.length - 1) {
          clearInterval(interval);
          setTimeout(() => {
            const q = sessionId ? `?sessionId=${sessionId}` : "";
            navigate(`/analysis${q}`);
          }, 700);
          return prev;
        }
        return prev + 1;
      });
    }, 900);
  };

  if (loading) {
    return (
      <div className="flex flex-col min-h-full items-center justify-center px-6" style={{ background: c.ink }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full"
        >
          {/* Animated ring */}
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 32 }}>
            <div style={{ position: "relative", width: 100, height: 100 }}>
              <svg width={100} height={100} viewBox="0 0 100 100" style={{ position: "absolute", top: 0, left: 0 }}>
                <circle cx={50} cy={50} r={42} fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth={6} />
                <circle
                  cx={50} cy={50} r={42}
                  fill="none"
                  stroke={c.surface}
                  strokeWidth={6}
                  strokeDasharray={`${(step + 1) / STEPS.length * 264} 264`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                  style={{ transition: "stroke-dasharray 0.6s ease" }}
                />
              </svg>
              <div style={{
                position: "absolute", inset: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                flexDirection: "column",
              }}>
                <span style={{ color: c.onDark, fontSize: 22, fontWeight: 800 }}>
                  {Math.round((step + 1) / STEPS.length * 100)}
                </span>
                <span style={{ color: c.onDarkMuted, fontSize: 11 }}>%</span>
              </div>
            </div>
          </div>

          <p style={{ color: c.onDark, fontSize: 18, fontWeight: 700, textAlign: "center", marginBottom: 8 }}>
            Analyzing with AI...
          </p>
          <p style={{ color: c.onDarkMuted, fontSize: 13, textAlign: "center", marginBottom: 32, lineHeight: 1.6 }}>
            Analyzing your swing video and<br />pose time-series data…
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {STEPS.map((s, i) => (
              <div
                key={s}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  background: i <= step ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.05)",
                  borderRadius: 12,
                  padding: "12px 14px",
                  border: `1px solid ${i <= step ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.08)"}`,
                  transition: "all 0.4s ease",
                }}
              >
                <div style={{
                  width: 24, height: 24, borderRadius: 12,
                  background: i < step ? c.surface : i === step ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.1)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                  transition: "background 0.4s ease",
                }}>
                  {i < step ? (
                    <CheckCircle size={14} color={c.ink} />
                  ) : (
                    <span style={{ color: i === step ? c.onDark : c.onDarkMuted, fontSize: 11, fontWeight: 700 }}>
                      {i + 1}
                    </span>
                  )}
                </div>
                <span style={{
                  color: i <= step ? c.onDark : c.onDarkMuted,
                  fontSize: 13,
                  fontWeight: i === step ? 600 : 400,
                  transition: "color 0.4s ease",
                }}>
                  {s}
                </span>
                {i === step && (
                  <div style={{ marginLeft: "auto", display: "flex", gap: 3 }}>
                    {[0, 1, 2].map(j => (
                      <div
                        key={j}
                        style={{
                          width: 5, height: 5, borderRadius: 3,
                          background: c.onDark,
                          animation: `pulse 1.2s ${j * 0.2}s infinite`,
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
        <style>{`@keyframes pulse { 0%,100%{opacity:0.3;transform:scale(0.8)} 50%{opacity:1;transform:scale(1)} }`}</style>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-full bg-white">
      {/* Header */}
      <div className="px-5 pt-12 pb-5" style={{ background: c.ink }}>
        <div className="flex items-center gap-3 mb-1">
          <button
            onClick={() => navigate("/")}
            style={{ background: "rgba(255,255,255,0.1)", border: "none", borderRadius: 10, padding: "6px", cursor: "pointer" }}
          >
            <ChevronLeft size={18} color={c.onDark} />
          </button>
          <h1 style={{ color: c.onDark, fontSize: 18, fontWeight: 700 }}>Upload Swing</h1>
        </div>
        <p style={{ color: c.onDarkMuted, fontSize: 12, marginTop: 4, marginLeft: 40 }}>
          Upload or record a video
        </p>
      </div>

      <div className="px-4 py-5 flex flex-col gap-5">

        {/* Upload Area */}
        <div
          onClick={() => setUploaded(true)}
          style={{
            border: `2px dashed ${uploaded ? c.ink : c.border}`,
            borderRadius: 16,
            padding: "32px 20px",
            textAlign: "center",
            cursor: "pointer",
            background: uploaded ? c.accentMuted : c.bg,
            transition: "all 0.3s ease",
          }}
        >
          {uploaded ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 26,
                background: c.ink,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <CheckCircle size={26} color={c.surface} />
              </div>
              <p style={{ color: c.ink, fontSize: 14, fontWeight: 700 }}>Video uploaded</p>
              <p style={{ color: c.muted, fontSize: 12 }}>swing_20240604.mp4 · 12.4MB</p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 26,
                background: c.borderLight,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Upload size={24} color={c.subtle} />
              </div>
              <p style={{ color: c.ink, fontSize: 14, fontWeight: 600 }}>Upload swing video</p>
              <p style={{ color: c.subtle, fontSize: 12 }}>Upload a front or side view video</p>
              <p style={{ color: c.muted, fontSize: 11 }}>MP4, MOV · Max 500MB</p>
            </div>
          )}
        </div>

        {/* Record Option */}
        <button
          style={{
            background: "white",
            border: `1px solid ${c.border}`,
            borderRadius: 12,
            padding: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            color: c.ink,
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          <Camera size={18} color={c.ink} />
          Record a new swing
        </button>

        {/* Select View */}
        <div>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 8 }}>
            Camera angle
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            {VIEWS.map(v => (
              <button
                key={v}
                onClick={() => setView(v)}
                style={{
                  flex: 1,
                  padding: "9px 4px",
                  borderRadius: 10,
                  border: `1.5px solid ${view === v ? c.ink : c.border}`,
                  background: view === v ? c.accentMuted : c.surface,
                  color: view === v ? c.ink : c.muted,
                  fontSize: 12,
                  fontWeight: view === v ? 700 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                {v}
              </button>
            ))}
          </div>
        </div>

        {/* Select Club */}
        <div>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 8 }}>
            Select club
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            {CLUBS.map(clubName => (
              <button
                key={clubName}
                onClick={() => setClub(clubName)}
                style={{
                  flex: 1,
                  padding: "10px 4px",
                  borderRadius: 10,
                  border: `1.5px solid ${club === clubName ? c.ink : c.border}`,
                  background: club === clubName ? c.ink : c.surface,
                  color: club === clubName ? c.surface : c.muted,
                  fontSize: 13,
                  fontWeight: club === c ? 700 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                {clubName}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p style={{ color: c.ink, fontSize: 13, fontWeight: 700, marginBottom: 8 }}>
            Main concerns <span style={{ color: c.subtle, fontWeight: 400 }}>select multiple</span>
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {CONCERNS.map(concern => (
              <button
                key={concern}
                onClick={() => toggleConcern(concern)}
                style={{
                  padding: "8px 14px",
                  borderRadius: 20,
                  border: `1.5px solid ${concerns.includes(concern) ? c.ink : c.border}`,
                  background: concerns.includes(concern) ? c.ink : c.surface,
                  color: concerns.includes(concern) ? c.surface : c.muted,
                  fontSize: 13,
                  fontWeight: concerns.includes(concern) ? 600 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                {concern}
              </button>
            ))}
          </div>
        </div>

        {/* Analysis Info */}
        <div style={{
          background: c.accentMuted,
          borderRadius: 12,
          padding: "12px 14px",
          display: "flex",
          alignItems: "flex-start",
          gap: 10,
          border: `1px solid ${c.border}`,
        }}>
          <Bot size={16} color={c.ink} style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <p style={{ color: c.ink, fontSize: 12, fontWeight: 600, marginBottom: 2 }}>About AI analysis</p>
            <p style={{ color: c.muted, fontSize: 11, lineHeight: 1.6 }}>
              We analyze pose time-series data together with your<br />
              past swings to deliver personalized coaching feedback
            </p>
          </div>
        </div>

        {/* Start Button */}
        <button
          onClick={startAnalysis}
          style={{
            background: c.ink,
            border: "none",
            borderRadius: 14,
            padding: "15px",
            color: c.surface,
            fontSize: 16,
            fontWeight: 700,
            cursor: "pointer",
            width: "100%",
            marginBottom: 8,
          }}
        >
          Start AI analysis
        </button>
        <p style={{ textAlign: "center", color: c.subtle, fontSize: 12 }}>
          You can start the demo without uploading a video
        </p>
      </div>
    </div>
  );
}
