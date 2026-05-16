"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Match } from "@/lib/match";
import { randomSeed } from "@/lib/rng";
import { MATCH_CONFIG, visibleAssetIds, type PublicMatch, type PublicPlayer, type RevealMode, type TradeAction } from "@/lib/types";

const HUMAN_ID = "you";

/** Phase state machine.
 *  - trading: prices frozen, news visible, player can place orders
 *  - lock:    short countdown, last chance feeling, no trades
 *  - reveal:  the year's 12 months tick through cinematically
 *  - ended:   match over
 */
export type RoundPhase = "trading" | "lock" | "reveal" | "ended";

const TIMING = {
  trading: 50_000,  // 50s — read, plan, position
  lock:     3_000,  // 3s — orders frozen
  reveal:   7_000,  // 7s — 12 months play out
  monthsPerRound: 12,
};

export interface UseStackMatch {
  match: PublicMatch | null;
  you: PublicPlayer | null;
  ended: { finalRanking: PublicPlayer[] } | null;
  error: string | null;
  visible: Set<string>;
  phase: RoundPhase;
  /** Wall-clock end of current phase, for countdown UI. */
  phaseEndsAt: number;
  trade: (a: TradeAction) => void;
  rematch: () => void;
}

export function useStackMatch({
  name, avatar, length, reveal,
}: { name: string; avatar: string; length: "quick" | "full"; reveal: RevealMode }): UseStackMatch {
  const [snapshot, setSnapshot] = useState<PublicMatch | null>(null);
  const [ended, setEnded] = useState<UseStackMatch["ended"]>(null);
  const [error, setError] = useState<string | null>(null);
  const [phase, setPhase] = useState<RoundPhase>("trading");
  const [phaseEndsAt, setPhaseEndsAt] = useState<number>(Date.now() + TIMING.trading);
  const matchRef = useRef<Match | null>(null);
  const phaseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const newsTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const revealInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  const buildMatch = useCallback(() => {
    const totalYears = length === "quick" ? MATCH_CONFIG.YEARS_QUICK : MATCH_CONFIG.YEARS_FULL;
    const m = new Match({
      roomId: `local-${Date.now()}`,
      seed: randomSeed(),
      totalYears,
      tickMs: 580, // intra-reveal tick (~12 in 7s); kept for HeaderBar/MonthBar compatibility
      reveal,
    });
    m.addPlayer(HUMAN_ID, (name || "Player").slice(0, 16), avatar || "🎩", false);
    m.fillBots(MATCH_CONFIG.PLAYERS_PER_ROOM);
    m.start();
    // Initial news for the very first trading window.
    if (reveal === "pro") {
      m.flashNews();
      // 30% chance of a second item right away — gives a fuller news strip on year 1
      if (Math.random() < 0.3) m.flashNews();
    }
    return m;
  }, [name, avatar, length, reveal]);

  const clearTimers = () => {
    if (phaseTimer.current) { clearTimeout(phaseTimer.current); phaseTimer.current = null; }
    if (newsTimer.current) { clearTimeout(newsTimer.current); newsTimer.current = null; }
    if (revealInterval.current) { clearInterval(revealInterval.current); revealInterval.current = null; }
  };

  // mount
  useEffect(() => {
    const m = buildMatch();
    matchRef.current = m;
    setSnapshot(m.toPublic());
    setEnded(null);
    setPhase("trading");
    setPhaseEndsAt(Date.now() + TIMING.trading);
    return () => {
      clearTimers();
      m.dispose();
      matchRef.current = null;
    };
  }, [buildMatch]);

  // Phase state machine
  useEffect(() => {
    const m = matchRef.current;
    if (!m) return;
    clearTimers();

    if (phase === "ended") return;

    if (phase === "trading") {
      // Maybe drop a second news item mid-window so the strip stays fresh.
      if (m.reveal === "pro") {
        newsTimer.current = setTimeout(() => {
          if (matchRef.current === m) {
            m.flashNews();
            setSnapshot(m.toPublic());
          }
        }, Math.floor(TIMING.trading * 0.55));
      }
      phaseTimer.current = setTimeout(() => setPhase("lock"), TIMING.trading);
      return () => clearTimers();
    }

    if (phase === "lock") {
      phaseTimer.current = setTimeout(() => setPhase("reveal"), TIMING.lock);
      return () => clearTimers();
    }

    if (phase === "reveal") {
      // Run 12 monthly ticks across TIMING.reveal ms.
      const stepMs = Math.max(60, Math.floor(TIMING.reveal / TIMING.monthsPerRound));
      let ticks = 0;
      revealInterval.current = setInterval(() => {
        const stillPlaying = m.advance();
        ticks++;
        setSnapshot(m.toPublic());
        if (!stillPlaying) {
          clearTimers();
          setEnded({ finalRanking: m.finalRanking() });
          setPhase("ended");
          return;
        }
        if (ticks >= TIMING.monthsPerRound) {
          clearTimers();
          // Start next round's trading phase
          if (m.reveal === "pro") m.flashNews();
          setSnapshot(m.toPublic());
          setPhase("trading");
          setPhaseEndsAt(Date.now() + TIMING.trading);
        }
      }, stepMs);
      return () => clearTimers();
    }
  }, [phase]);

  // Update phaseEndsAt whenever phase changes
  useEffect(() => {
    if (phase === "trading") setPhaseEndsAt(Date.now() + TIMING.trading);
    else if (phase === "lock") setPhaseEndsAt(Date.now() + TIMING.lock);
    else if (phase === "reveal") setPhaseEndsAt(Date.now() + TIMING.reveal);
  }, [phase]);

  const trade = useCallback((action: TradeAction) => {
    const m = matchRef.current;
    if (!m) return;
    // Gate trades during lock/reveal — except cancellations always allowed.
    if (phase !== "trading" && action.type !== "order:cancel") {
      setError("trades locked");
      setTimeout(() => setError(null), 1500);
      return;
    }
    const res = m.applyTrade(HUMAN_ID, action);
    if (!res.ok) {
      setError(res.reason ?? "trade rejected");
      setTimeout(() => setError(null), 1500);
      return;
    }
    setSnapshot(m.toPublic());
  }, [phase]);

  const rematch = useCallback(() => {
    clearTimers();
    if (matchRef.current) matchRef.current.dispose();
    const m = buildMatch();
    matchRef.current = m;
    setSnapshot(m.toPublic());
    setEnded(null);
    setPhase("trading");
    setPhaseEndsAt(Date.now() + TIMING.trading);
  }, [buildMatch]);

  const you = snapshot?.players.find(p => p.id === HUMAN_ID) ?? null;
  const visible = snapshot
    ? visibleAssetIds(snapshot.assets, snapshot.year, snapshot.totalYears, reveal)
    : new Set<string>();
  return { match: snapshot, you, ended, error, visible, phase, phaseEndsAt, trade, rematch };
}
