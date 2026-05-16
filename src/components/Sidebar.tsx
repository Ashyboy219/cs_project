"use client";
import type { PublicMatch, PublicPlayer } from "@/lib/types";
import { Pig, MoneyStack } from "./Pig";

const TOTAL_TICKS = 20; // visual progress bar

export function Sidebar({
  match, you, onLobby,
}: { match: PublicMatch; you: PublicPlayer | null; onLobby: () => void }) {
  const filled = Math.min(TOTAL_TICKS, Math.round((match.year - 1 + match.month / 12) * (TOTAL_TICKS / match.totalYears)));
  const speech = match.banner ?? "Steady tape today.";

  return (
    <aside className="sidebar">
      <div className="year-label">
        <span className="small">YEAR</span>
        <span className="big">{match.year}</span>
        <span className="small">OF {match.totalYears}</span>
      </div>
      <div className="progress" aria-label="match progress">
        {Array.from({ length: TOTAL_TICKS }).map((_, i) => (
          <div key={i} className={`tick ${i < filled ? "" : "empty"}`} />
        ))}
      </div>

      <div className="pig-area">
        <div className="speech">{speech}</div>
        <Pig />
      </div>

      <div className="stats">
        <div>
          <div className="label">POCKET CASH</div>
          <div className="val">${Math.round(you?.cash ?? 0).toLocaleString()}</div>
        </div>
        <div>
          <div className="label"><span className="sortcaret">◆</span>OVERALL NET WORTH</div>
          <div className="val">${Math.round(you?.netWorth ?? 0).toLocaleString()}</div>
        </div>
      </div>

      <MoneyStack />

      <div className="standings">
        {match.players.map((p) => (
          <div key={p.id} className={`row ${p.id === you?.id ? "you" : ""}`}>
            <span className="rank">{p.rank}</span>
            <span className="ava">{p.avatar}</span>
            <span className="nm">{p.name}</span>
            <span className="nw">${Math.round(p.netWorth).toLocaleString()}</span>
          </div>
        ))}
      </div>

      <div className="menu">
        <button className="item" onClick={onLobby}>
          <span className="lt"><span className="caret">▸</span>LEAVE TABLE</span>
        </button>
      </div>

      <button className="info" aria-label="info">i</button>
    </aside>
  );
}
