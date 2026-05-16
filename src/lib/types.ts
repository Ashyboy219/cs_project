// Shared types between server and client. Keep this file framework-free.

export type Regime = "calm" | "boom" | "crash" | "chaos";

export type AssetKind =
  | "savings"
  | "cd"
  | "index"
  | "bonds"
  | "gold"
  | "wheat"
  | "stock";

export type Sector =
  | "tech"
  | "energy"
  | "banking"
  | "industrial"
  | "consumer"
  | "pharma"
  | "materials"
  | "transport"
  | "utilities";

/** Hidden personality of a stock — never sent to the client raw. */
export interface StockPersonality {
  sector: Sector;
  drift: number;          // mean monthly return, e.g. 0.012 = +1.2%
  vol: number;            // monthly stdev, e.g. 0.05 = 5%
  momentum: number;       // [-0.5..+0.5] negative = mean-reverting, positive = trend-following
  bankruptcyFloor: number;// minimum price floor; can be 0 (true risk) or e.g. 1
  dividendRate: number;   // monthly cash yield as fraction of price (0..0.003)
  regimeBeta: Record<Regime, number>; // multiplier applied to drift in each regime
  regimeVolMult: Record<Regime, number>; // multiplier applied to vol in each regime
}

export interface AssetDef {
  id: string;
  kind: AssetKind;
  name: string;
  ticker?: string;        // for stocks
  sector?: Sector;        // for stocks
  cdTermMonths?: number;  // for CD
  cdRateAnnual?: number;  // for CD (sampled per match)
  bondYieldAnnual?: number; // for bonds (sampled per match)
}

export interface AssetState {
  def: AssetDef;
  price: number;
  prevPrice: number;
  history: number[];      // last N prices for sparkline (server trims)
  // private to server (not sent over the wire):
  // personality?: StockPersonality;
}

/** Public asset snapshot (sent to client). Hidden fields scrubbed. */
export interface PublicAsset {
  id: string;
  kind: AssetKind;
  name: string;
  ticker?: string;
  sector?: Sector;
  price: number;
  prevPrice: number;
  history: number[];
  cdTermMonths?: number;
  cdRateAnnual?: number;
  bondYieldAnnual?: number;
}

export interface CDHolding {
  principal: number;
  rateAnnual: number;
  monthsRemaining: number; // counts down each tick
}

/** A resting (queued) order. Fires on next tick when price crosses the trigger. */
export interface RestingOrder {
  id: string;
  assetId: string;
  /** limit-buy: fires when price <= trigger. take-profit: fires when price >= trigger.
   *  stop-loss: fires when price <= trigger. */
  kind: "limit-buy" | "take-profit" | "stop-loss";
  qty: number;        // share count
  trigger: number;    // price level
  placedYear: number; // diagnostics
  placedMonth: number;
}

export interface PlayerState {
  id: string;          // socket id or bot id
  name: string;
  avatar: string;      // emoji
  isBot: boolean;
  cash: number;
  shares: Record<string, number>;     // assetId -> share count (stock/index/gold/bonds/wheat)
  cds: CDHolding[];
  /** $ paid for current holdings of this asset. Decreases proportionally on sell. */
  costBasis: Record<string, number>;
  /** Realized P/L per asset (collected from sells minus cost of those shares). */
  realizedPL: Record<string, number>;
  /** Matured CDs awaiting collect. Each: { payout: principal+interest, principal }. */
  cdMatured: { payout: number; principal: number }[];
  /** Pending resting orders by assetId. */
  restingOrders: RestingOrder[];
  netWorth: number;
  netWorthHistory: number[];
  /** Highest net worth observed so far. */
  peakNetWorth: number;
  /** Largest peak→trough drop, as a fraction (0..1). */
  maxDrawdown: number;
}

export type MatchPhase = "lobby" | "playing" | "ended";

export interface PublicMatch {
  roomId: string;
  phase: MatchPhase;
  year: number;        // 1..totalYears
  month: number;       // 1..12
  totalYears: number;
  tickMs: number;
  monthStartedAt: number; // server epoch ms
  assets: PublicAsset[];
  players: PublicPlayer[];
  banner?: string;     // ambiguous round banner
  hintedAssetId?: string;  // one card highlighted
  /** Last 5 news items (Pro mode only — empty in Story). */
  news: PublicNews[];
  // regime never sent
}

export interface PublicPlayer {
  id: string;
  name: string;
  avatar: string;
  isBot: boolean;
  cash: number;
  shares: Record<string, number>;
  cds: CDHolding[];
  costBasis: Record<string, number>;
  realizedPL: Record<string, number>;
  cdMatured: { payout: number; principal: number }[];
  restingOrders: RestingOrder[];
  netWorth: number;
  netWorthHistory: number[];
  peakNetWorth: number;
  maxDrawdown: number;
  rank?: number;
}

export type TradeAction =
  | { type: "buy"; assetId: string; qty: number }
  | { type: "sell"; assetId: string; qty: number }
  | { type: "savings:deposit"; amount: number }
  | { type: "savings:withdraw"; amount: number }
  | { type: "cd:open"; amount: number }
  | { type: "cd:collect"; index: number }
  | { type: "bonds:buy"; amount: number }
  | { type: "bonds:sell"; amount: number }
  | { type: "order:place"; assetId: string; kind: RestingOrder["kind"]; qty: number; trigger: number }
  | { type: "order:cancel"; orderId: string };

// ── News ──────────────────────────────────────────────────────────────────

export type NewsCategory = "macro" | "sector" | "earnings" | "whisper";
export type NewsCredibility = "wire" | "analyst" | "rumor";

/** Server-side news item with hidden intent. */
export interface NewsItem {
  id: string;
  text: string;
  category: NewsCategory;
  credibility: NewsCredibility;
  /** Year/month when published. */
  year: number;
  month: number;
  /** Hidden — not sent to client. */
  intent: NewsIntent;
}

export interface NewsIntent {
  /** Where the bias lands. */
  target:
    | { kind: "regime"; regime: Regime }
    | { kind: "asset"; assetId: string }
    | { kind: "sector"; sector: Sector }
    | { kind: "noise" };
  /** Magnitude of the bias to apply. -1..+1 added to drift this tick. */
  bias: number;
  /** How many ticks the bias persists. */
  persistMonths: number;
  /** True if this news's intent will actually fire. False = misleading. */
  truthful: boolean;
}

/** Public news item — no hidden intent. */
export interface PublicNews {
  id: string;
  text: string;
  category: NewsCategory;
  credibility: NewsCredibility;
  year: number;
  month: number;
  /** Asset id this is "about" if any (for highlighting on click). */
  aboutAssetId?: string;
  /** Sector this is "about" if any (for highlighting on click). */
  aboutSector?: Sector;
}

export interface ClientToServerEvents {
  "lobby:join": (payload: { name: string; avatar: string; mode: "quick" | "full" }) => void;
  "lobby:start": () => void;
  "match:trade": (action: TradeAction) => void;
  "match:rematch": () => void;
}

export interface ServerToClientEvents {
  "lobby:joined": (payload: { roomId: string; you: PublicPlayer }) => void;
  "match:state": (state: PublicMatch) => void;
  "match:tick": (state: PublicMatch) => void;
  "match:end": (state: PublicMatch & { finalRanking: PublicPlayer[] }) => void;
  "error": (message: string) => void;
}

export const MATCH_CONFIG = {
  STARTING_CASH: 10_000,
  MONTHS_PER_YEAR: 12,
  TICK_MS: 5000,           // 5s per month
  YEARS_FULL: 20,
  YEARS_QUICK: 5,
  PLAYERS_PER_ROOM: 4,
  STOCK_COUNT: 5,          // procedural stocks per match
  HISTORY_LEN: 36,         // 3 years of monthly history kept for sparkline
} as const;

export type RevealMode = "story" | "pro";

/** Order in which assets reveal in story mode. Stock slots map to first/second/... stock in roster. */
export const REVEAL_ORDER = [
  "savings", "cd", "index", "stock1", "bonds", "stock2", "wheat", "gold", "stock3", "stock4", "stock5",
] as const;

/** Returns the set of asset IDs visible at a given match year. */
export function visibleAssetIds(
  assets: PublicAsset[], year: number, totalYears: number, mode: RevealMode,
): Set<string> {
  if (mode === "pro") return new Set(assets.map(a => a.id));
  // Designed so the last asset unlocks at `revealEnd` year. 20yr → 7, 10yr → 5, 5yr → 4.
  const revealEnd = Math.max(3, Math.min(7, Math.ceil(totalYears * 0.4)));
  const t = Math.min(1, (year - 1) / Math.max(1, revealEnd - 1));
  const slotsOpen = Math.max(2, Math.ceil(2 + t * (REVEAL_ORDER.length - 2)));
  const stocks = assets.filter(a => a.kind === "stock");
  const out = new Set<string>();
  for (let i = 0; i < Math.min(slotsOpen, REVEAL_ORDER.length); i++) {
    const slot = REVEAL_ORDER[i];
    if (slot === "stock1") stocks[0] && out.add(stocks[0].id);
    else if (slot === "stock2") stocks[1] && out.add(stocks[1].id);
    else if (slot === "stock3") stocks[2] && out.add(stocks[2].id);
    else if (slot === "stock4") stocks[3] && out.add(stocks[3].id);
    else if (slot === "stock5") stocks[4] && out.add(stocks[4].id);
    else out.add(slot);
  }
  return out;
}
