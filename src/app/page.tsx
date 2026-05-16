"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const AVATARS = ["🎩", "🦊", "🦉", "🐉", "🐻", "🦁", "🐢", "🦅", "🐍", "🦂"];

export default function Lobby() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [avatar, setAvatar] = useState(AVATARS[0]);
  const [length, setLength] = useState<"quick" | "full">("full");
  const [reveal, setReveal] = useState<"story" | "pro">("story");

  const begin = () => {
    const trimmed = (name || "Player").trim().slice(0, 16);
    const params = new URLSearchParams({ name: trimmed, avatar, length, reveal });
    router.push(`/game?${params.toString()}`);
  };

  return (
    <div className="overlay" style={{ position: "fixed", inset: 0 }}>
      <div className="overlay-card">
        <div style={{ fontFamily: "Cinzel,serif", letterSpacing: ".18em", fontSize: 11, textAlign:"center", color:"#4a4732" }}>
          A MID-CENTURY MARKET GAME
        </div>
        <h1>STACK</h1>
        <div className="subtitle">Twenty years, twelve months, one ledger.</div>

        <Field label="Your name">
          <input
            className="input-line"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Player"
            maxLength={16}
          />
        </Field>

        <Field label="Avatar">
          <div className="avatar-row">
            {AVATARS.map((a) => (
              <button key={a} onClick={() => setAvatar(a)} className={avatar === a ? "active" : ""} aria-label={`Avatar ${a}`}>
                {a}
              </button>
            ))}
          </div>
        </Field>

        <Field label="Match length">
          <div className="toggle-grid">
            {(["quick", "full"] as const).map((v) => (
              <button key={v} className={`toggle-opt ${length === v ? "active" : ""}`} onClick={() => setLength(v)}>
                <div className="ttl">{v === "quick" ? "Quick" : "Full"}</div>
                <div className="sub">{v === "quick" ? "5 yr · ~5 min" : "20 yr · ~20 min"}</div>
              </button>
            ))}
          </div>
        </Field>

        <Field label="Mode">
          <div className="toggle-grid">
            {(["story", "pro"] as const).map((v) => (
              <button key={v} className={`toggle-opt ${reveal === v ? "active" : ""}`} onClick={() => setReveal(v)}>
                <div className="ttl">{v === "story" ? "Story" : "Pro"}</div>
                <div className="sub">{v === "story" ? "calm. tools unlock year by year" : "live wire. news + queued orders"}</div>
              </button>
            ))}
          </div>
        </Field>

        <button className="cta" onClick={begin}>TAKE YOUR SEAT</button>
        <div style={{ textAlign:"center", marginTop:8, fontStyle:"italic", fontSize:11, color:"#4a4732" }}>
          Three other traders are at the table.
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 14 }}>
      <div className="field-label">{label}</div>
      <div style={{ marginTop: 6 }}>{children}</div>
    </div>
  );
}
