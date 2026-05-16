// News engine. Procedural, mid-century-flavored, deliberately ambiguous.
//
// Each news item has a hidden NewsIntent which biases the next tick's price computation.
// Three credibility tiers control how often the stated intent is truthful:
//   wire    — ~95% truthful  (the wire never lies, but it's terse)
//   analyst — ~70% truthful  (a guess from someone with a desk)
//   rumor   — ~50% truthful  (could be anything)
// Players can't tell analyst from rumor reliably; reading the room is the skill.

import type { NewsCategory, NewsCredibility, NewsIntent, NewsItem, PublicAsset, Regime, Sector } from "./types";
import type { RNG } from "./rng";

// ── Headline templates ────────────────────────────────────────────────────
// Procedural: {NAME}, {SECTOR}, {DIR} get filled in at generation time.

const MACRO_HEADLINES: { text: string; bias: number; regime: Regime }[] = [
  { text: "Reserve hints at tighter money.",        bias: -0.4, regime: "crash" },
  { text: "Trade winds favorable across the seas.", bias: +0.3, regime: "boom"  },
  { text: "Consumer confidence wavers.",            bias: -0.3, regime: "crash" },
  { text: "Bountiful harvest forecast.",            bias: +0.2, regime: "calm"  },
  { text: "Oil shipments delayed at port.",         bias: -0.4, regime: "chaos" },
  { text: "Productivity numbers surprise upward.",  bias: +0.4, regime: "boom"  },
  { text: "Whisper of a tariff in the wind.",       bias: -0.3, regime: "chaos" },
  { text: "Strong jobs report on the wire.",        bias: +0.4, regime: "boom"  },
  { text: "Bank failures rumored downstate.",       bias: -0.5, regime: "crash" },
  { text: "Foreign capital flows in.",              bias: +0.3, regime: "boom"  },
  { text: "Storm clouds over the markets.",         bias: -0.4, regime: "crash" },
  { text: "Treasury auctions go cold.",             bias: -0.2, regime: "chaos" },
];

const SECTOR_HEADLINES: { text: string; bias: number; sector: Sector }[] = [
  { text: "Tech orders pour in from the coast.",      bias: +0.4, sector: "tech"     },
  { text: "Tech inventories pile up.",                bias: -0.3, sector: "tech"     },
  { text: "Refineries running flat out.",             bias: +0.3, sector: "energy"   },
  { text: "Wells coming up dry.",                     bias: -0.3, sector: "energy"   },
  { text: "Banks tighten lending.",                   bias: -0.3, sector: "banking"  },
  { text: "Banks loosen the spigot.",                 bias: +0.3, sector: "banking"  },
  { text: "Foundries booked through next quarter.",   bias: +0.3, sector: "industrial" },
  { text: "Steel orders cancelled overseas.",         bias: -0.4, sector: "industrial" },
  { text: "Holiday spend looking strong.",            bias: +0.3, sector: "consumer" },
  { text: "Department stores cut prices.",            bias: -0.2, sector: "consumer" },
  { text: "New trial shows promise.",                 bias: +0.4, sector: "pharma"   },
  { text: "Trial halted on safety concerns.",         bias: -0.5, sector: "pharma"   },
  { text: "Copper futures rip.",                      bias: +0.3, sector: "materials"},
  { text: "Mines flooded after heavy rains.",         bias: -0.4, sector: "materials"},
  { text: "Rail freight at record levels.",           bias: +0.3, sector: "transport"},
  { text: "Strike threatens the rails.",              bias: -0.4, sector: "transport"},
  { text: "Power demand surges in the heat.",         bias: +0.2, sector: "utilities"},
  { text: "Regulators eye utility rates.",            bias: -0.2, sector: "utilities"},
];

const EARNINGS_HEADLINES: { text: string; bias: number }[] = [
  { text: "{NAME} beats expectations.",          bias: +0.5 },
  { text: "{NAME} misses guidance.",             bias: -0.5 },
  { text: "Whispers of trouble at {NAME}.",      bias: -0.3 },
  { text: "{NAME} raises forecast.",             bias: +0.4 },
  { text: "Quiet confidence around {NAME}.",     bias: +0.2 },
  { text: "{NAME} cuts the dividend.",           bias: -0.4 },
  { text: "{NAME} announces buyback.",           bias: +0.3 },
  { text: "{NAME} loses a key contract.",        bias: -0.4 },
];

const WHISPER_HEADLINES: { text: string; bias: number }[] = [
  { text: "Floor talk: someone loading {NAME}.",      bias: +0.4 },
  { text: "Block trade in {SECTOR} this morning.",    bias: +0.2 },
  { text: "Rumor: insider selling at {NAME}.",        bias: -0.4 },
  { text: "Old hands quietly buying {NAME}.",         bias: +0.3 },
  { text: "Tape watchers wary of {NAME}.",            bias: -0.3 },
];

// ── Public-side hints (so players can interpret) ──────────────────────────
// We DO tell players what asset/sector a news item references — that's the visible signal.
// The HIDDEN part is whether it's truthful and how big the actual move will be.

export interface GeneratedNews {
  item: NewsItem;
  /** Public-facing asset id reference (for highlight on click). */
  aboutAssetId?: string;
  aboutSector?: Sector;
}

function pickCredibility(rng: RNG): NewsCredibility {
  const r = rng.next();
  if (r < 0.40) return "wire";
  if (r < 0.75) return "analyst";
  return "rumor";
}

function truthfulAt(cred: NewsCredibility, rng: RNG): boolean {
  const p = cred === "wire" ? 0.95 : cred === "analyst" ? 0.70 : 0.50;
  return rng.next() < p;
}

function pickCategory(rng: RNG, hasStocks: boolean): NewsCategory {
  // Slight bias toward macro/sector early; allow earnings/whispers when stocks revealed.
  const pool: NewsCategory[] = ["macro", "macro", "sector", "sector"];
  if (hasStocks) pool.push("earnings", "whisper");
  return pool[rng.int(0, pool.length - 1)];
}

export function generateNews(
  rng: RNG,
  year: number,
  month: number,
  assets: PublicAsset[],
): GeneratedNews | null {
  const stocks = assets.filter(a => a.kind === "stock");
  const category = pickCategory(rng, stocks.length > 0);
  const credibility = pickCredibility(rng);
  const truthful = truthfulAt(credibility, rng);
  const id = `n${year}-${month}-${Math.floor(rng.next() * 1e6).toString(36)}`;

  // Build NewsItem per category
  switch (category) {
    case "macro": {
      const tpl = rng.pick(MACRO_HEADLINES);
      const intent: NewsIntent = {
        target: { kind: "regime", regime: tpl.regime },
        bias: tpl.bias,
        persistMonths: rng.int(1, 3),
        truthful,
      };
      return {
        item: { id, text: tpl.text, category, credibility, year, month, intent },
      };
    }

    case "sector": {
      const tpl = rng.pick(SECTOR_HEADLINES);
      const intent: NewsIntent = {
        target: { kind: "sector", sector: tpl.sector },
        bias: tpl.bias,
        persistMonths: rng.int(1, 3),
        truthful,
      };
      return {
        item: { id, text: tpl.text, category, credibility, year, month, intent },
        aboutSector: tpl.sector,
      };
    }

    case "earnings": {
      if (stocks.length === 0) return generateNews(rng, year, month, assets);
      const stock = rng.pick(stocks);
      const tpl = rng.pick(EARNINGS_HEADLINES);
      const text = tpl.text.replace("{NAME}", stock.name);
      const intent: NewsIntent = {
        target: { kind: "asset", assetId: stock.id },
        bias: tpl.bias,
        persistMonths: rng.int(1, 2),
        truthful,
      };
      return {
        item: { id, text, category, credibility, year, month, intent },
        aboutAssetId: stock.id,
      };
    }

    case "whisper": {
      if (stocks.length === 0) return generateNews(rng, year, month, assets);
      const stock = rng.pick(stocks);
      const tpl = rng.pick(WHISPER_HEADLINES);
      const sectorName = stock.sector ? humanSector(stock.sector) : "the floor";
      const text = tpl.text.replace("{NAME}", stock.name).replace("{SECTOR}", sectorName);
      const intent: NewsIntent = {
        target: text.includes("{SECTOR}") || tpl.text.includes("{SECTOR}")
          ? { kind: "sector", sector: stock.sector ?? "industrial" }
          : { kind: "asset", assetId: stock.id },
        bias: tpl.bias,
        persistMonths: rng.int(1, 2),
        truthful,
      };
      return {
        item: { id, text, category, credibility, year, month, intent },
        aboutAssetId: stock.id,
        aboutSector: stock.sector,
      };
    }
  }
}

function humanSector(s: Sector): string {
  const map: Record<Sector, string> = {
    tech: "tech", energy: "oil", banking: "banking", industrial: "steel",
    consumer: "consumer", pharma: "pharma", materials: "materials",
    transport: "rail", utilities: "utilities",
  };
  return map[s];
}
