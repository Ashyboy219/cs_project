"use client";
import { useEffect, useState } from "react";
import clsx from "clsx";
import type { RoundPhase } from "@/lib/useStackMatch";

const PHASE_LABEL: Record<RoundPhase, string> = {
  trading: "TRADING",
  lock:    "LOCKING",
  reveal:  "REVEAL",
  ended:   "FINIS",
};

const PHASE_TOTAL: Record<RoundPhase, number> = {
  trading: 50_000,
  lock:     3_000,
  reveal:   7_000,
  ended:    1,
};

export function PhaseTimer({ phase, endsAt }: { phase: RoundPhase; endsAt: number }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    let raf = 0;
    const loop = () => { setNow(Date.now()); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);
  const remaining = Math.max(0, endsAt - now);
  const total = PHASE_TOTAL[phase];
  const pct = Math.max(0, Math.min(100, (remaining / total) * 100));
  const secs = Math.ceil(remaining / 1000);
  return (
    <div className="phase-timer">
      <span className={clsx("label", phase)}>{PHASE_LABEL[phase]}</span>
      <div className="bar"><div className={clsx("fill", phase)} style={{ width: `${pct}%` }} /></div>
      <span className="secs">{secs}s</span>
    </div>
  );
}
