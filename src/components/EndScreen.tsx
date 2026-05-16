"use client";
import type { PublicPlayer } from "@/lib/types";

export function EndScreen({
  finalRanking, you, onRematch, onLobby,
}: {
  finalRanking: PublicPlayer[];
  you: PublicPlayer | null;
  onRematch: () => void;
  onLobby: () => void;
}) {
  const me = finalRanking.find((p) => p.id === you?.id);
  const myRank = finalRanking.findIndex((p) => p.id === you?.id) + 1 || finalRanking.length;
  const myEnd = me?.netWorth ?? 0;
  const myStart = me?.netWorthHistory?.[0] ?? 10000;
  const ret = myEnd / Math.max(1, myStart) - 1;
  const dd = me?.maxDrawdown ?? 0;

  const verdict = (() => {
    if (myRank === 1) return "Champion of the Floor.";
    if (myRank === 2) return "So close.";
    if (myRank === 3) return "A respectable showing.";
    return "There is always another match.";
  })();

  return (
    <div className="overlay">
      <div className="overlay-card" style={{ width: "min(480px,100%)" }}>
        <div style={{ fontFamily:"Cinzel,serif", letterSpacing:".18em", fontSize:11, textAlign:"center", color:"#4a4732" }}>
          MATCH CONCLUDED
        </div>
        <h1 style={{ fontSize: 30, marginTop: 4 }}>{verdict}</h1>

        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr 1fr", gap:10, marginTop:18 }}>
          <Stat label="Rank" value={`#${myRank}`} />
          <Stat label="Final" value={`$${Math.round(myEnd).toLocaleString()}`} />
          <Stat label="Return" value={`${ret >= 0 ? "+" : ""}${(ret * 100).toFixed(1)}%`} color={ret >= 0 ? "#566532" : "#a64633"} />
          <Stat label="Max DD" value={`-${(dd * 100).toFixed(1)}%`} color="#a64633" />
        </div>

        <div style={{ marginTop: 18, paddingTop: 14, borderTop: "1px dashed rgba(60,50,20,0.45)" }}>
          <div className="field-label" style={{ marginBottom: 6 }}>Leaderboard</div>
          {finalRanking.map((p, i) => (
            <div key={p.id} style={{
              display:"flex", justifyContent:"space-between",
              fontFamily:"Cinzel,serif", fontVariantNumeric:"tabular-nums",
              fontSize:13, padding:"3px 0",
              fontWeight: p.id === you?.id ? 800 : 500,
            }}>
              <span style={{ display:"flex", gap:8, alignItems:"center" }}>
                <span style={{ width:14, color:"#7d7728" }}>{i + 1}</span>
                <span>{p.avatar}</span>
                <span>{p.name}</span>
              </span>
              <span>${Math.round(p.netWorth).toLocaleString()}</span>
            </div>
          ))}
        </div>

        <div style={{ display:"flex", gap:8, marginTop:18 }}>
          <button className="cta" style={{ flex:1, marginTop:0 }} onClick={onRematch}>REMATCH</button>
          <button className="cta" style={{ width:"34%", marginTop:0, background:"transparent", color:"#2c2a1c", border:"1px solid #8b8049" }} onClick={onLobby}>LOBBY</button>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <div className="field-label" style={{ fontSize:10 }}>{label}</div>
      <div style={{ fontFamily:"Cinzel,serif", fontWeight:800, fontSize:24, color: color ?? "#2c2a1c", fontVariantNumeric:"tabular-nums" }}>
        {value}
      </div>
    </div>
  );
}
