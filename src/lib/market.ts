// Market simulation: regime model + price tick.
//
// The market has 4 hidden regimes. They transition via a Markov chain whose bias shifts
// across the match: early years lean Calm; mid years sharpen swings; late years can
// dump into Crash or Chaos for high-drama finishes.
//
// Each asset has a price that updates monthly via:
//   newPrice = max(floor, prev * (1 + driftEff + momentumKick + vol * gauss()))
// where driftEff = drift * regimeBeta[regime], vol *= regimeVolMult[regime].

import type { Regime, AssetState, AssetDef } from "./types";
import { RNG } from "./rng";
import { generateStockRoster, type GeneratedStock } from "./stockgen";

export interface RegimeState {
  current: Regime;
  monthsInRegime: number;
}

export const REGIMES: Regime[] = ["calm", "boom", "crash", "chaos"];

/** Returns transition probabilities from `from`, biased by progress through the match.
 *  progress ∈ [0,1]. Early game favors Calm; late game lets Crash/Chaos in.
 */
function transitionProbs(from: Regime, progress: number): Record<Regime, number> {
  // base "stickiness" — regimes prefer to persist 4-10 months
  const stay = 0.85;
  const leave = 1 - stay;

  // weights for where to go when leaving `from`; modulated by progress
  // early bias toward calm/boom, late bias toward crash/chaos
  const earlyW: Record<Regime, number> = { calm: 0.55, boom: 0.30, crash: 0.08, chaos: 0.07 };
  const lateW:  Record<Regime, number> = { calm: 0.20, boom: 0.25, crash: 0.30, chaos: 0.25 };
  const w: Record<Regime, number> = {
    calm: earlyW.calm * (1 - progress) + lateW.calm * progress,
    boom: earlyW.boom * (1 - progress) + lateW.boom * progress,
    crash: earlyW.crash * (1 - progress) + lateW.crash * progress,
    chaos: earlyW.chaos * (1 - progress) + lateW.chaos * progress,
  };
  // remove `from` from leave-targets (we don't "leave" to the same regime)
  w[from] = 0;
  const sum = w.calm + w.boom + w.crash + w.chaos || 1;
  const probs: Record<Regime, number> = {
    calm: (w.calm / sum) * leave,
    boom: (w.boom / sum) * leave,
    crash: (w.crash / sum) * leave,
    chaos: (w.chaos / sum) * leave,
  };
  probs[from] = stay;
  return probs;
}

export function stepRegime(rng: RNG, r: RegimeState, progress: number): RegimeState {
  // Only consider transition if we've been in this regime for at least 2 months,
  // unless rolling a forced-transition because we've been here too long.
  const minStay = 2;
  const maxStay = 12;
  if (r.monthsInRegime < minStay) {
    return { current: r.current, monthsInRegime: r.monthsInRegime + 1 };
  }
  const probs = transitionProbs(r.current, progress);
  // forced exit if we've overstayed
  if (r.monthsInRegime >= maxStay) {
    probs[r.current] = 0;
    const s = probs.calm + probs.boom + probs.crash + probs.chaos || 1;
    (Object.keys(probs) as Regime[]).forEach(k => (probs[k] /= s));
  }
  const x = rng.next();
  let acc = 0;
  for (const k of REGIMES) {
    acc += probs[k];
    if (x < acc) {
      const next = k;
      return { current: next, monthsInRegime: next === r.current ? r.monthsInRegime + 1 : 1 };
    }
  }
  return { current: r.current, monthsInRegime: r.monthsInRegime + 1 };
}

/** Internal record kept server-side per asset; carries personality. */
export interface ServerAsset extends AssetState {
  personality?: GeneratedStock["personality"];
  // for momentum: keep recent return
  lastReturn: number;
}

export interface BuiltAssets {
  list: ServerAsset[];
  byId: Map<string, ServerAsset>;
}

const HISTORY_LEN = 36;

export function buildMatchAssets(rng: RNG, stockCount: number): BuiltAssets {
  const assets: ServerAsset[] = [];

  // Anchors first — deterministic feel.
  const indexDef: AssetDef = { id: "index", kind: "index", name: "Index Fund" };
  const goldDef: AssetDef = { id: "gold", kind: "gold", name: "Gold" };
  const savingsDef: AssetDef = { id: "savings", kind: "savings", name: "Savings Account" };
  const bondsDef: AssetDef = {
    id: "bonds", kind: "bonds", name: "Government Bonds",
    bondYieldAnnual: round4(rng.range(0.03, 0.05)),
  };
  const cdDef: AssetDef = {
    id: "cd", kind: "cd", name: "Certificate of Deposit",
    cdTermMonths: rng.pick([6, 12, 12, 18, 24]),
    cdRateAnnual: round4(rng.range(0.04, 0.08)),
  };

  assets.push(asset(savingsDef, 1));      // 1 unit = $1, just nominal
  assets.push(asset(cdDef, 1));
  assets.push(asset(indexDef, 100));
  assets.push(asset(bondsDef, 100));
  assets.push(asset(goldDef, round2(50 + rng.range(0, 30))));

  const wheatDef: AssetDef = { id: "wheat", kind: "wheat", name: "Wheat" };
  assets.push(asset(wheatDef, round2(rng.range(2.5, 6.0))));

  // Procedural stocks
  const stocks = generateStockRoster(rng, stockCount);
  for (const s of stocks) {
    assets.push(asset(s.def, s.startPrice, s.personality));
  }

  const byId = new Map<string, ServerAsset>();
  for (const a of assets) byId.set(a.def.id, a);
  return { list: assets, byId };
}

function asset(def: AssetDef, startPrice: number, personality?: GeneratedStock["personality"]): ServerAsset {
  return {
    def,
    price: startPrice,
    prevPrice: startPrice,
    history: [startPrice],
    personality,
    lastReturn: 0,
  };
}

function round4(n: number) { return Math.round(n * 10000) / 10000; }
function round2(n: number) { return Math.round(n * 100) / 100; }

/** Advance every asset by one month under the given regime. Mutates in place.
 *  `extraBias` is an additive return adjustment per asset id (from active news intents). */
export function tickPrices(
  rng: RNG, assets: ServerAsset[], regime: Regime,
  extraBias: Record<string, number> = {},
): void {
  for (const a of assets) {
    a.prevPrice = a.price;
    const bias = extraBias[a.def.id] ?? 0;
    switch (a.def.kind) {
      case "savings":
        a.price = 1;
        break;
      case "cd":
        a.price = 1;
        break;
      case "index": {
        const driftBase = 0.008;
        const volBase = 0.035;
        const beta = regime === "boom" ? 1.4 : regime === "crash" ? -1.2 : regime === "chaos" ? 0.0 : 1.0;
        const volMult = regime === "crash" ? 1.8 : regime === "chaos" ? 1.6 : regime === "boom" ? 1.1 : 1.0;
        const ret = driftBase * beta + volBase * volMult * rng.gauss() + bias;
        a.price = Math.max(1, round2(a.price * (1 + ret)));
        a.lastReturn = ret;
        break;
      }
      case "bonds": {
        const yieldMonth = (a.def.bondYieldAnnual ?? 0.04) / 12;
        const beta = regime === "crash" ? +1.5 : regime === "chaos" ? +0.2 : regime === "boom" ? -0.4 : 0.5;
        const ret = yieldMonth * beta + 0.012 * rng.gauss() + 0.001 + bias;
        a.price = Math.max(1, round2(a.price * (1 + ret)));
        a.lastReturn = ret;
        break;
      }
      case "gold": {
        const beta = regime === "chaos" ? 1.6 : regime === "crash" ? 1.2 : regime === "boom" ? -0.3 : 0.2;
        const ret = 0.003 * beta + 0.035 * rng.gauss() + bias;
        a.price = Math.max(1, round2(a.price * (1 + ret)));
        a.lastReturn = ret;
        break;
      }
      case "wheat": {
        const driftBase = -0.002;
        const volBase = 0.09;
        const beta = regime === "chaos" ? 1.8 : regime === "boom" ? 1.2 : regime === "crash" ? -0.4 : 0.3;
        const volMult = regime === "chaos" ? 2.0 : regime === "crash" ? 1.6 : regime === "boom" ? 1.2 : 1.0;
        const ret = driftBase * beta + volBase * volMult * rng.gauss() + bias;
        a.price = Math.max(0.5, round2(a.price * (1 + ret)));
        a.lastReturn = ret;
        break;
      }
      case "stock": {
        const p = a.personality!;
        const effDrift = p.drift * p.regimeBeta[regime];
        const effVol = p.vol * p.regimeVolMult[regime];
        const mKick = p.momentum * a.lastReturn;
        const ret = effDrift + mKick + effVol * rng.gauss() + bias;
        let next = a.price * (1 + ret);
        const floor = p.bankruptcyFloor;
        next = Math.max(floor, next);
        a.price = round2(next);
        a.lastReturn = ret;
        break;
      }
    }
    a.history.push(a.price);
    if (a.history.length > HISTORY_LEN) a.history.shift();
  }
}

/** Pick the next opening regime for a fresh match. */
export function initialRegime(rng: RNG): RegimeState {
  // Almost always start calm; tiny chance of boom start for variety.
  const r: Regime = rng.next() < 0.85 ? "calm" : "boom";
  return { current: r, monthsInRegime: 1 };
}
