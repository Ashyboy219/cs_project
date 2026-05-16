// Match engine. Pure step machine.
//
// The Match owns:
//   - the seeded RNG
//   - the asset prices (including hidden personalities)
//   - the regime
//   - every player's cash/holdings/CDs
//
// Caller drives cadence (e.g. a React hook running setInterval). Each call to advance()
// performs one "month": bots act → income accrues → prices tick → regime steps → calendar advances.
// Trades are applied immediately at the currently-posted price (locked between ticks).

import { RNG } from "@/lib/rng";
import { buildMatchAssets, initialRegime, stepRegime, tickPrices, type ServerAsset } from "@/lib/market";
import {
  MATCH_CONFIG,
  type CDHolding,
  type NewsItem,
  type PlayerState,
  type PublicAsset,
  type PublicMatch,
  type PublicNews,
  type PublicPlayer,
  type Regime,
  type RestingOrder,
  type RevealMode,
  type TradeAction,
} from "@/lib/types";
import { BOT_PROFILES, botDecide, type BotKind } from "@/lib/bots";
import { generateNews } from "@/lib/news";

export interface MatchOptions {
  totalYears: number;
  tickMs: number;
  seed: number;
  roomId: string;
  /** Pro mode unlocks news + queued orders. Story keeps the simpler loop. */
  reveal?: RevealMode;
}

/** A news intent currently affecting prices, with its remaining lifetime. */
interface ActiveBias {
  item: NewsItem;
  remainingMonths: number;
}

export class Match {
  readonly roomId: string;
  readonly seed: number;
  readonly totalYears: number;
  readonly tickMs: number;

  rng: RNG;
  year = 1;
  month = 1;
  phase: "lobby" | "playing" | "ended" = "lobby";
  regime: { current: Regime; monthsInRegime: number };
  assets!: ReturnType<typeof buildMatchAssets>;
  players = new Map<string, PlayerState>();
  monthStartedAt = 0;
  banner: string | undefined;
  hintedAssetId: string | undefined;
  /** Public news log (most recent first). Pro mode only. */
  newsLog: PublicNews[] = [];
  /** Server-only: active biases that adjust the next tick's prices. */
  private activeBiases: ActiveBias[] = [];
  /** Server-only: news → public mapping for click-highlight. */
  private newsAbout: Map<string, { aboutAssetId?: string; aboutSector?: string }> = new Map();
  reveal: RevealMode;

  constructor(opts: MatchOptions) {
    this.roomId = opts.roomId;
    this.seed = opts.seed;
    this.totalYears = opts.totalYears;
    this.tickMs = opts.tickMs;
    this.reveal = opts.reveal ?? "story";
    this.rng = new RNG(opts.seed);
    this.regime = initialRegime(this.rng);
  }

  addPlayer(id: string, name: string, avatar: string, isBot = false): PlayerState {
    const p: PlayerState = {
      id, name, avatar, isBot,
      cash: MATCH_CONFIG.STARTING_CASH,
      shares: {},
      cds: [],
      costBasis: {},
      realizedPL: {},
      cdMatured: [],
      restingOrders: [],
      netWorth: MATCH_CONFIG.STARTING_CASH,
      netWorthHistory: [MATCH_CONFIG.STARTING_CASH],
      peakNetWorth: MATCH_CONFIG.STARTING_CASH,
      maxDrawdown: 0,
    };
    this.players.set(id, p);
    return p;
  }

  removePlayer(id: string) {
    this.players.delete(id);
  }

  fillBots(target: number) {
    let added = 0;
    const taken = new Set<string>();
    for (const p of this.players.values()) if (p.isBot) taken.add(p.name);
    for (const profile of BOT_PROFILES) {
      if (this.players.size >= target) break;
      if (taken.has(profile.name)) continue;
      this.addPlayer(`bot:${profile.kind}`, profile.name, profile.avatar, true);
      added++;
    }
    return added;
  }

  start() {
    if (this.phase !== "lobby") return;
    this.assets = buildMatchAssets(this.rng, MATCH_CONFIG.STOCK_COUNT);
    this.phase = "playing";
    this.monthStartedAt = Date.now();
    this.recomputeAllNetWorth();
    this.refreshBanner();
  }

  /** Generate one news item for the upcoming tick (Pro mode only). Public + bias setup. */
  flashNews(): void {
    if (this.reveal !== "pro" || this.phase !== "playing") return;
    if (!this.assets) return;
    const publicAssets = this.assets.list.map(scrub);
    const generated = generateNews(this.rng, this.year, this.month, publicAssets);
    if (!generated) return;
    const pub: PublicNews = {
      id: generated.item.id,
      text: generated.item.text,
      category: generated.item.category,
      credibility: generated.item.credibility,
      year: generated.item.year,
      month: generated.item.month,
      aboutAssetId: generated.aboutAssetId,
      aboutSector: generated.aboutSector,
    };
    this.newsLog = [pub, ...this.newsLog].slice(0, 5);
    if (generated.item.intent.truthful) {
      this.activeBiases.push({ item: generated.item, remainingMonths: generated.item.intent.persistMonths });
    }
  }

  /** Advance one month. Caller controls cadence. Returns true if match is still playing. */
  advance(): boolean {
    if (this.phase !== "playing") return false;

    // 1) Bots decide BEFORE the price ticks (using current month's posted price).
    this.runBots();

    // 2) Accrue savings/CD/bonds interest, dividends, CD maturities.
    this.accrueIncome();

    // 3) Compute extra bias per asset from active news intents.
    const extraBias = this.computeExtraBias();

    // 4) Tick asset prices (with bias applied).
    tickPrices(this.rng, this.assets.list, this.regime.current, extraBias);

    // 5) Step regime.
    const progress = ((this.year - 1) * 12 + (this.month - 1)) / Math.max(1, this.totalYears * 12 - 1);
    this.regime = stepRegime(this.rng, this.regime, progress);

    // 6) Fire any resting orders that crossed.
    this.fireRestingOrders();

    // 7) Decay news biases.
    this.activeBiases = this.activeBiases
      .map(b => ({ ...b, remainingMonths: b.remainingMonths - 1 }))
      .filter(b => b.remainingMonths > 0);

    // 8) Advance calendar.
    this.month++;
    if (this.month > MATCH_CONFIG.MONTHS_PER_YEAR) {
      this.month = 1;
      this.year++;
    }
    this.monthStartedAt = Date.now();

    // 9) Recompute net worth + drawdown.
    this.recomputeAllNetWorth();
    if (this.month === 1) {
      for (const p of this.players.values()) p.netWorthHistory.push(p.netWorth);
    }

    // 10) Update banner/hint — only at year boundaries so the pig + hilite
    // don't strobe during the rapid reveal-phase ticks.
    if (this.month === 1) this.refreshBanner();

    // 11) End?
    if (this.year > this.totalYears) {
      this.phase = "ended";
      return false;
    }
    return true;
  }

  /** Sum bias contributions per asset id from active news intents. */
  private computeExtraBias(): Record<string, number> {
    const out: Record<string, number> = {};
    const SCALE = 0.10; // bias 0.4 → +4% return; tunable
    for (const b of this.activeBiases) {
      const i = b.item.intent;
      const amt = i.bias * SCALE;
      switch (i.target.kind) {
        case "asset":
          out[i.target.assetId] = (out[i.target.assetId] ?? 0) + amt;
          break;
        case "sector":
          for (const a of this.assets.list) {
            if (a.def.kind === "stock" && a.def.sector === i.target.sector) {
              out[a.def.id] = (out[a.def.id] ?? 0) + amt;
            }
          }
          break;
        case "regime":
          // Apply to risk assets (stocks + index + wheat) in the bias direction.
          // Bonds get the opposite (flight-to-safety in crash regimes).
          for (const a of this.assets.list) {
            if (a.def.kind === "stock" || a.def.kind === "index" || a.def.kind === "wheat") {
              out[a.def.id] = (out[a.def.id] ?? 0) + amt;
            } else if (a.def.kind === "bonds") {
              out[a.def.id] = (out[a.def.id] ?? 0) - amt * 0.4;
            } else if (a.def.kind === "gold" && (i.target.regime === "chaos" || i.target.regime === "crash")) {
              out[a.def.id] = (out[a.def.id] ?? 0) + Math.abs(amt) * 0.5;
            }
          }
          break;
        case "noise":
          break;
      }
    }
    return out;
  }

  /** Fire any resting orders whose triggers were crossed by the just-ticked price. */
  private fireRestingOrders() {
    for (const p of this.players.values()) {
      if (p.restingOrders.length === 0) continue;
      const remaining: RestingOrder[] = [];
      for (const o of p.restingOrders) {
        const a = this.assets.byId.get(o.assetId);
        if (!a) { remaining.push(o); continue; }
        const fires = (
          (o.kind === "limit-buy"   && a.price <= o.trigger) ||
          (o.kind === "take-profit" && a.price >= o.trigger) ||
          (o.kind === "stop-loss"   && a.price <= o.trigger)
        );
        if (!fires) { remaining.push(o); continue; }
        // Execute at the trigger price (player's planned level).
        const fillPrice = o.trigger;
        if (o.kind === "limit-buy") {
          const cost = o.qty * fillPrice;
          if (cost > p.cash + 1e-6) continue; // can't afford → quietly skip
          p.cash = round2(p.cash - cost);
          p.shares[o.assetId] = (p.shares[o.assetId] ?? 0) + o.qty;
          p.costBasis[o.assetId] = round2((p.costBasis[o.assetId] ?? 0) + cost);
        } else {
          // sell
          const owned = p.shares[o.assetId] ?? 0;
          const qty = Math.min(o.qty, Math.floor(owned));
          if (qty <= 0) continue;
          const proceeds = qty * fillPrice;
          const avgCost = (p.costBasis[o.assetId] ?? 0) / Math.max(1, owned);
          const removedBasis = avgCost * qty;
          p.cash = round2(p.cash + proceeds);
          p.shares[o.assetId] = owned - qty;
          p.costBasis[o.assetId] = round2((p.costBasis[o.assetId] ?? 0) - removedBasis);
          p.realizedPL[o.assetId] = round2((p.realizedPL[o.assetId] ?? 0) + (proceeds - removedBasis));
        }
      }
      p.restingOrders = remaining;
    }
  }

  /** Apply a trade intent from a player (human or bot). */
  applyTrade(playerId: string, action: TradeAction): { ok: boolean; reason?: string } {
    const p = this.players.get(playerId);
    if (!p) return { ok: false, reason: "no such player" };
    if (this.phase !== "playing") return { ok: false, reason: "not playing" };

    switch (action.type) {
      case "buy":
      case "sell": {
        const a = this.assets.byId.get(action.assetId);
        if (!a) return { ok: false, reason: "no such asset" };
        if (!["stock", "index", "gold", "wheat"].includes(a.def.kind)) return { ok: false, reason: "not tradeable" };
        const qty = Math.floor(action.qty);
        if (qty <= 0) return { ok: false, reason: "qty<=0" };
        if (action.type === "buy") {
          const cost = qty * a.price;
          if (cost > p.cash + 1e-6) return { ok: false, reason: "not enough cash" };
          p.cash = round2(p.cash - cost);
          p.shares[a.def.id] = (p.shares[a.def.id] ?? 0) + qty;
          p.costBasis[a.def.id] = round2((p.costBasis[a.def.id] ?? 0) + cost);
        } else {
          const owned = p.shares[a.def.id] ?? 0;
          if (qty > owned) return { ok: false, reason: "not enough shares" };
          const proceeds = qty * a.price;
          // proportional cost basis removed
          const avgCost = (p.costBasis[a.def.id] ?? 0) / Math.max(1, owned);
          const removedBasis = avgCost * qty;
          p.cash = round2(p.cash + proceeds);
          p.shares[a.def.id] = owned - qty;
          p.costBasis[a.def.id] = round2((p.costBasis[a.def.id] ?? 0) - removedBasis);
          p.realizedPL[a.def.id] = round2((p.realizedPL[a.def.id] ?? 0) + (proceeds - removedBasis));
        }
        return { ok: true };
      }
      case "savings:deposit": {
        const amt = Math.max(0, Math.floor(action.amount));
        if (amt > p.cash) return { ok: false, reason: "not enough cash" };
        p.cash = round2(p.cash - amt);
        p.shares["savings"] = (p.shares["savings"] ?? 0) + amt;
        return { ok: true };
      }
      case "savings:withdraw": {
        const amt = Math.max(0, Math.floor(action.amount));
        const have = p.shares["savings"] ?? 0;
        if (amt > have) return { ok: false, reason: "not enough in savings" };
        p.shares["savings"] = have - amt;
        p.cash = round2(p.cash + amt);
        return { ok: true };
      }
      case "cd:open": {
        const amt = Math.max(0, Math.floor(action.amount));
        if (amt < 100) return { ok: false, reason: "CD minimum $100" };
        if (amt > p.cash) return { ok: false, reason: "not enough cash" };
        const openCount = p.cds.length + p.cdMatured.length;
        if (openCount >= 3) return { ok: false, reason: "max 3 CDs at once" };
        const cd = this.assets.byId.get("cd")!;
        p.cash = round2(p.cash - amt);
        p.cds.push({
          principal: amt,
          rateAnnual: cd.def.cdRateAnnual ?? 0.05,
          monthsRemaining: cd.def.cdTermMonths ?? 12,
        });
        p.costBasis["cd"] = round2((p.costBasis["cd"] ?? 0) + amt);
        return { ok: true };
      }
      case "cd:collect": {
        const idx = action.index;
        if (idx < 0 || idx >= p.cdMatured.length) return { ok: false, reason: "no such coin" };
        const coin = p.cdMatured[idx];
        p.cash = round2(p.cash + coin.payout);
        p.realizedPL["cd"] = round2((p.realizedPL["cd"] ?? 0) + (coin.payout - coin.principal));
        p.costBasis["cd"] = round2((p.costBasis["cd"] ?? 0) - coin.principal);
        p.cdMatured = p.cdMatured.filter((_, i) => i !== idx);
        return { ok: true };
      }
      case "bonds:buy": {
        const amt = Math.max(0, Math.floor(action.amount));
        if (amt > p.cash) return { ok: false, reason: "not enough cash" };
        const bonds = this.assets.byId.get("bonds")!;
        const units = amt / bonds.price;
        p.cash = round2(p.cash - amt);
        p.shares["bonds"] = round4((p.shares["bonds"] ?? 0) + units);
        p.costBasis["bonds"] = round2((p.costBasis["bonds"] ?? 0) + amt);
        return { ok: true };
      }
      case "bonds:sell": {
        const amt = Math.max(0, Math.floor(action.amount));
        const bonds = this.assets.byId.get("bonds")!;
        const have = p.shares["bonds"] ?? 0;
        const unitsToSell = Math.min(have, amt / bonds.price);
        if (unitsToSell <= 0) return { ok: false, reason: "nothing to sell" };
        const proceeds = unitsToSell * bonds.price;
        const avgCost = (p.costBasis["bonds"] ?? 0) / Math.max(1e-6, have);
        const removedBasis = avgCost * unitsToSell;
        p.cash = round2(p.cash + proceeds);
        p.shares["bonds"] = round4(have - unitsToSell);
        p.costBasis["bonds"] = round2((p.costBasis["bonds"] ?? 0) - removedBasis);
        p.realizedPL["bonds"] = round2((p.realizedPL["bonds"] ?? 0) + (proceeds - removedBasis));
        return { ok: true };
      }
      case "order:place": {
        if (this.reveal !== "pro") return { ok: false, reason: "orders are pro-mode only" };
        const a = this.assets.byId.get(action.assetId);
        if (!a) return { ok: false, reason: "no such asset" };
        if (!["stock", "index", "gold", "wheat"].includes(a.def.kind)) return { ok: false, reason: "not orderable" };
        if (action.qty <= 0 || action.trigger <= 0) return { ok: false, reason: "invalid order" };
        if (p.restingOrders.length >= 12) return { ok: false, reason: "too many open orders" };
        const order: RestingOrder = {
          id: `o${Date.now().toString(36)}-${Math.floor(this.rng.next() * 1e6).toString(36)}`,
          assetId: action.assetId,
          kind: action.kind,
          qty: Math.floor(action.qty),
          trigger: round2(action.trigger),
          placedYear: this.year,
          placedMonth: this.month,
        };
        p.restingOrders.push(order);
        return { ok: true };
      }
      case "order:cancel": {
        const before = p.restingOrders.length;
        p.restingOrders = p.restingOrders.filter(o => o.id !== action.orderId);
        return { ok: p.restingOrders.length < before };
      }
    }
  }

  private accrueIncome() {
    const savingsRateMonth = 0.02 / 12; // baseline savings APY ~2%
    for (const p of this.players.values()) {
      // Savings interest
      const sav = p.shares["savings"] ?? 0;
      if (sav > 0) {
        p.shares["savings"] = round2(sav * (1 + savingsRateMonth));
      }
      // CD maturity → drop into cdMatured "coin" (player must collect)
      const stillRunning: CDHolding[] = [];
      for (const cd of p.cds) {
        cd.monthsRemaining--;
        if (cd.monthsRemaining <= 0) {
          const months = (this.assets.byId.get("cd")?.def.cdTermMonths ?? 12);
          const payout = round2(cd.principal * (1 + cd.rateAnnual * (months / 12)));
          if (p.isBot) {
            // bots auto-collect
            p.cash = round2(p.cash + payout);
            p.realizedPL["cd"] = round2((p.realizedPL["cd"] ?? 0) + (payout - cd.principal));
            p.costBasis["cd"] = round2((p.costBasis["cd"] ?? 0) - cd.principal);
          } else {
            p.cdMatured.push({ payout, principal: cd.principal });
          }
        } else {
          stillRunning.push(cd);
        }
      }
      p.cds = stillRunning;
      // Stock dividends
      for (const a of this.assets.list) {
        if (a.def.kind !== "stock") continue;
        const qty = p.shares[a.def.id] ?? 0;
        if (qty <= 0) continue;
        const rate = a.personality?.dividendRate ?? 0;
        if (rate > 0) {
          p.cash = round2(p.cash + qty * a.price * rate);
        }
      }
    }
  }

  private runBots() {
    if (!this.assets) return;
    for (const p of this.players.values()) {
      if (!p.isBot) continue;
      const kind = (p.id.split(":")[1] ?? "carla") as BotKind;
      const a = botDecide(kind, p, this.assets.list, {
        year: this.year,
        month: this.month,
        totalYears: this.totalYears,
        rng: () => this.rng.next(),
      });
      if (a) this.applyTrade(p.id, a);
    }
  }

  private recomputeAllNetWorth() {
    for (const p of this.players.values()) {
      let nw = p.cash;
      for (const [aid, qty] of Object.entries(p.shares)) {
        if (qty <= 0) continue;
        if (aid === "savings") { nw += qty; continue; }
        const a = this.assets?.byId.get(aid);
        if (!a) continue;
        nw += qty * a.price;
      }
      for (const cd of p.cds) nw += cd.principal;
      for (const coin of p.cdMatured) nw += coin.payout;
      p.netWorth = round2(nw);
      // Track peak + drawdown
      if (p.netWorth > p.peakNetWorth) p.peakNetWorth = p.netWorth;
      if (p.peakNetWorth > 0) {
        const dd = (p.peakNetWorth - p.netWorth) / p.peakNetWorth;
        if (dd > p.maxDrawdown) p.maxDrawdown = dd;
      }
    }
  }

  private refreshBanner() {
    const r = this.regime.current;
    const banners: Record<Regime, string[]> = {
      calm:  ["Markets steady.", "A quiet trading floor.", "Volume light today.", "Tape moves sideways."],
      boom:  ["Optimism in the air.", "Crowd cheers a new high.", "Confidence rising.", "Bulls take the floor."],
      crash: ["A red day.", "Selling pressure mounts.", "The wires are quiet.", "Panic on the floor."],
      chaos: ["Conflicting reports.", "An unsettled tape.", "Whipsaw conditions.", "Storm clouds gather."],
    };
    this.banner = banners[r][Math.floor(this.rng.next() * banners[r].length)];

    // Hint one card by recent move — not necessarily helpful, just *signal*.
    const candidates = this.assets.list.filter(a => ["stock", "index", "gold", "bonds"].includes(a.def.kind));
    if (candidates.length) {
      const pick = candidates[Math.floor(this.rng.next() * candidates.length)];
      this.hintedAssetId = pick.def.id;
    }
  }

  toPublic(): PublicMatch {
    const players: PublicPlayer[] = [];
    const ranked = [...this.players.values()].sort((a, b) => b.netWorth - a.netWorth);
    ranked.forEach((p, i) => {
      players.push(toPublicPlayer(p, i + 1));
    });
    const assets: PublicAsset[] = this.assets ? this.assets.list.map(scrub) : [];
    return {
      roomId: this.roomId,
      phase: this.phase,
      year: this.year,
      month: this.month,
      totalYears: this.totalYears,
      tickMs: this.tickMs,
      monthStartedAt: this.monthStartedAt,
      assets,
      players,
      banner: this.banner,
      hintedAssetId: this.hintedAssetId,
      news: this.newsLog.slice(),
    };
  }

  finalRanking(): PublicPlayer[] {
    return [...this.players.values()]
      .sort((a, b) => b.netWorth - a.netWorth)
      .map((p, i) => toPublicPlayer(p, i + 1));
  }

  dispose() {
    // step machine — nothing to dispose now.
  }
}

function scrub(a: ServerAsset): PublicAsset {
  return {
    id: a.def.id,
    kind: a.def.kind,
    name: a.def.name,
    ticker: a.def.ticker,
    sector: a.def.sector,
    price: a.price,
    prevPrice: a.prevPrice,
    history: a.history.slice(),
    cdTermMonths: a.def.cdTermMonths,
    cdRateAnnual: a.def.cdRateAnnual,
    bondYieldAnnual: a.def.bondYieldAnnual,
  };
}

function toPublicPlayer(p: PlayerState, rank: number): PublicPlayer {
  return {
    id: p.id, name: p.name, avatar: p.avatar, isBot: p.isBot,
    cash: p.cash, shares: { ...p.shares }, cds: p.cds.map(c => ({ ...c })),
    costBasis: { ...p.costBasis }, realizedPL: { ...p.realizedPL },
    cdMatured: p.cdMatured.slice(),
    restingOrders: p.restingOrders.map(o => ({ ...o })),
    netWorth: p.netWorth, netWorthHistory: p.netWorthHistory.slice(),
    peakNetWorth: p.peakNetWorth, maxDrawdown: p.maxDrawdown,
    rank,
  };
}

function round2(n: number) { return Math.round(n * 100) / 100; }
function round4(n: number) { return Math.round(n * 10000) / 10000; }
