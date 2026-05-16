// AI bot personalities. Bots see the same public market data players see — no cheating —
// and act each tick with bounded behavior. They exist to provide rank pressure, not to win.
//
// Personalities:
//   Conservative Carla — keeps most cash in CD/savings/bonds, dabbles in index.
//   Trend-Follower Ty  — chases recent winners.
//   Hedger Hana        — holds gold + bonds + some index.
//   YOLO Vince         — concentrates on whatever's hottest, all-in moves.

import type { ServerAsset } from "./market";
import type { PlayerState, TradeAction } from "./types";

export type BotKind = "carla" | "ty" | "hana" | "vince";

export const BOT_PROFILES: { kind: BotKind; name: string; avatar: string }[] = [
  { kind: "carla", name: "Carla",  avatar: "🦉" },  // Conservative
  { kind: "ty",    name: "Ty",     avatar: "🐺" },  // Trend follower
  { kind: "hana",  name: "Hana",   avatar: "🦊" },  // Hedger
  { kind: "vince", name: "Vince",  avatar: "🐉" },  // YOLO
];

/** Decide one action this tick. May return null (no-op). */
export function botDecide(
  kind: BotKind,
  me: PlayerState,
  assets: ServerAsset[],
  ctx: { year: number; totalYears: number; month: number; rng: () => number }
): TradeAction | null {
  const stocks = assets.filter(a => a.def.kind === "stock");
  const index = assets.find(a => a.def.id === "index");
  const gold = assets.find(a => a.def.id === "gold");
  const bonds = assets.find(a => a.def.id === "bonds");
  const cd = assets.find(a => a.def.id === "cd");
  const rng = ctx.rng;

  const progress = (ctx.year - 1) / Math.max(1, ctx.totalYears - 1);

  // Quick helper: which stock had biggest recent gain over last 3 months?
  const recentGain = (a: ServerAsset) => {
    const h = a.history;
    if (h.length < 2) return 0;
    const lookback = Math.min(3, h.length - 1);
    return (h[h.length - 1] - h[h.length - 1 - lookback]) / Math.max(0.01, h[h.length - 1 - lookback]);
  };

  switch (kind) {
    case "carla": {
      // Quietly drip cash into CD early, then into bonds, then a bit of index.
      if (me.cash > 1000 && rng() < 0.35 && cd) return { type: "cd:open", amount: Math.floor(me.cash * 0.4) };
      if (me.cash > 500 && rng() < 0.35 && bonds) return { type: "bonds:buy", amount: Math.floor(me.cash * 0.3) };
      if (me.cash > 300 && rng() < 0.25 && index) {
        const q = Math.floor((me.cash * 0.3) / index.price);
        if (q > 0) return { type: "buy", assetId: index.def.id, qty: q };
      }
      // late-game shave risk: sell some stocks
      if (progress > 0.7 && rng() < 0.3) {
        const owned = stocks.filter(s => (me.shares[s.def.id] ?? 0) > 0);
        if (owned.length) {
          const s = owned[Math.floor(rng() * owned.length)];
          const qty = Math.ceil((me.shares[s.def.id] ?? 0) * 0.3);
          if (qty > 0) return { type: "sell", assetId: s.def.id, qty };
        }
      }
      return null;
    }

    case "ty": {
      // Chase recent winners; bail on losers.
      const sorted = stocks.slice().sort((a, b) => recentGain(b) - recentGain(a));
      const top = sorted[0];
      const worst = sorted[sorted.length - 1];
      if (worst && (me.shares[worst.def.id] ?? 0) > 0 && recentGain(worst) < -0.05 && rng() < 0.6) {
        return { type: "sell", assetId: worst.def.id, qty: me.shares[worst.def.id] };
      }
      if (top && me.cash > top.price && rng() < 0.5) {
        const q = Math.max(1, Math.floor((me.cash * 0.4) / top.price));
        return { type: "buy", assetId: top.def.id, qty: q };
      }
      return null;
    }

    case "hana": {
      // Hedge: keep gold + bonds + a little index.
      if (gold && me.cash > gold.price && rng() < 0.35) {
        const q = Math.max(1, Math.floor((me.cash * 0.25) / gold.price));
        return { type: "buy", assetId: gold.def.id, qty: q };
      }
      if (bonds && me.cash > 500 && rng() < 0.3) return { type: "bonds:buy", amount: Math.floor(me.cash * 0.3) };
      if (index && me.cash > index.price && rng() < 0.25) {
        const q = Math.max(1, Math.floor((me.cash * 0.2) / index.price));
        return { type: "buy", assetId: index.def.id, qty: q };
      }
      return null;
    }

    case "vince": {
      // Concentrate. Pick a stock and pour cash in. Occasionally dump everything.
      if (rng() < 0.15) {
        // dump
        for (const s of stocks) {
          if ((me.shares[s.def.id] ?? 0) > 0) {
            return { type: "sell", assetId: s.def.id, qty: me.shares[s.def.id] };
          }
        }
      }
      const sorted = stocks.slice().sort((a, b) => recentGain(b) - recentGain(a));
      const pick = sorted[0];
      if (pick && me.cash > pick.price && rng() < 0.55) {
        const q = Math.max(1, Math.floor(me.cash / pick.price));
        return { type: "buy", assetId: pick.def.id, qty: q };
      }
      return null;
    }
  }
}
