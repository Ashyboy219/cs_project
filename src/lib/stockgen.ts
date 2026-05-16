// Procedurally generate the stock roster for a match.
// Each match should feel new: different names, different sectors, different personalities —
// but each personality is bounded by its sector's realistic band so a Bank can't behave like
// a meme tech stock. Players should be able to slowly learn sector archetypes across runs
// while never being sure of the specifics within a single match.

import type { AssetDef, Regime, Sector, StockPersonality } from "./types";
import { RNG } from "./rng";

// ── Name pools ────────────────────────────────────────────────────────────

const NAMES: Record<Sector, { names: string[]; tickers: string[] }> = {
  tech: {
    names: ["Helios Compute", "Cinder Labs", "Atlas Systems", "Polaris Data", "Vector Industries", "Quanta Works"],
    tickers: ["HCMP", "CNDR", "ATLS", "PLRS", "VCTR", "QNTA"],
  },
  energy: {
    names: ["Sunbelt Oil", "Northwind Petroleum", "Bedrock Resources", "Coalfield United", "Magma Energy"],
    tickers: ["SBLT", "NWND", "BDRK", "CFLD", "MGMA"],
  },
  banking: {
    names: ["Continental Trust", "Federated Savings", "Pinewood Mutual", "Crown Bancorp", "Heritage Holdings"],
    tickers: ["CTRT", "FDSV", "PNWD", "CRWN", "HRTG"],
  },
  industrial: {
    names: ["Atlas Steel", "Hammond Foundry", "Reliance Machine", "Granite Works", "Ironbridge Mfg"],
    tickers: ["ATSL", "HMFD", "RMCH", "GRWK", "IRBR"],
  },
  consumer: {
    names: ["Bluebird Stores", "Harvest Foods", "Sterling Apparel", "Hometown Goods", "Maple Brewing"],
    tickers: ["BLBD", "HRVS", "STRL", "HMTN", "MAPL"],
  },
  pharma: {
    names: ["Meridian Pharma", "Cygnus Biologics", "Beacon Health", "Verity Labs"],
    tickers: ["MRDN", "CYGN", "BCNH", "VRTY"],
  },
  materials: {
    names: ["Cascade Mining", "Redrock Copper", "Highline Lumber", "Tundra Materials"],
    tickers: ["CSCD", "RDCP", "HILM", "TNDR"],
  },
  transport: {
    names: ["Northstar Rail", "Pacific Cable & Wire", "Skyline Freight", "Liberty Shipping"],
    tickers: ["NSTR", "PCWR", "SKYF", "LBSH"],
  },
  utilities: {
    names: ["Edison Power", "Citywide Gas", "Brightwater Utility", "Meridian Electric"],
    tickers: ["EDSN", "CTWG", "BRWT", "MRDE"],
  },
};

// ── Sector bands ──────────────────────────────────────────────────────────
// Each sector defines a band; per-stock personality is sampled inside it.
// Numbers are monthly: drift = mean return, vol = stdev.

interface SectorBand {
  drift: [number, number];
  vol: [number, number];
  momentum: [number, number];
  bankruptcyFloor: [number, number]; // 0 = can go to zero; >0 = floor (e.g. utilities)
  dividend: [number, number];
  // multiplier on drift in each regime
  regimeBeta: Record<Regime, [number, number]>;
  regimeVolMult: Record<Regime, [number, number]>;
  startPrice: [number, number];
}

const BANDS: Record<Sector, SectorBand> = {
  tech: {
    drift:       [0.005, 0.025],
    vol:         [0.06, 0.12],
    momentum:    [0.05, 0.30],     // trend-following
    bankruptcyFloor: [0, 0],
    dividend:    [0, 0.0005],
    regimeBeta: {
      calm:  [0.8, 1.1],
      boom:  [1.6, 2.4],            // amplifies booms
      crash: [-1.8, -1.0],          // crushed in crashes
      chaos: [-0.5, 0.8],
    },
    regimeVolMult: { calm: [0.9, 1.1], boom: [1.0, 1.3], crash: [1.4, 2.0], chaos: [1.5, 2.2] },
    startPrice: [40, 90],
  },
  energy: {
    drift:       [-0.005, 0.012],
    vol:         [0.05, 0.10],
    momentum:    [-0.10, 0.15],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0008, 0.0020],
    regimeBeta: {
      calm:  [0.7, 1.0],
      boom:  [0.8, 1.4],
      crash: [-1.0, -0.3],
      chaos: [1.2, 2.2],            // swings hard in chaos
    },
    regimeVolMult: { calm: [1.0, 1.2], boom: [1.0, 1.4], crash: [1.2, 1.8], chaos: [1.7, 2.5] },
    startPrice: [25, 80],
  },
  banking: {
    drift:       [0.001, 0.012],
    vol:         [0.03, 0.07],
    momentum:    [-0.15, 0.10],     // slightly mean-reverting
    bankruptcyFloor: [0, 0],
    dividend:    [0.0015, 0.0030],
    regimeBeta: {
      calm:  [0.9, 1.1],
      boom:  [1.0, 1.6],
      crash: [-2.2, -1.4],          // crushed in crashes
      chaos: [-1.0, 0.2],
    },
    regimeVolMult: { calm: [0.9, 1.1], boom: [1.0, 1.3], crash: [1.6, 2.2], chaos: [1.3, 1.8] },
    startPrice: [60, 180],
  },
  industrial: {
    drift:       [0.000, 0.014],
    vol:         [0.03, 0.07],
    momentum:    [-0.10, 0.15],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0010, 0.0025],
    regimeBeta: {
      calm:  [0.9, 1.1],
      boom:  [1.2, 1.8],
      crash: [-1.4, -0.7],
      chaos: [-0.4, 0.6],
    },
    regimeVolMult: { calm: [0.9, 1.1], boom: [1.0, 1.3], crash: [1.3, 1.7], chaos: [1.2, 1.6] },
    startPrice: [40, 120],
  },
  consumer: {
    drift:       [0.003, 0.013],
    vol:         [0.025, 0.06],
    momentum:    [-0.10, 0.10],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0010, 0.0025],
    regimeBeta: {
      calm:  [1.0, 1.2],
      boom:  [1.0, 1.4],
      crash: [-0.8, -0.2],          // defensive
      chaos: [-0.2, 0.4],
    },
    regimeVolMult: { calm: [0.9, 1.0], boom: [1.0, 1.2], crash: [1.1, 1.4], chaos: [1.1, 1.4] },
    startPrice: [20, 70],
  },
  pharma: {
    drift:       [0.005, 0.020],
    vol:         [0.05, 0.11],
    momentum:    [-0.10, 0.20],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0005, 0.0015],
    regimeBeta: {
      calm:  [1.0, 1.3],
      boom:  [1.1, 1.7],
      crash: [-0.6, 0.0],            // somewhat defensive
      chaos: [-0.5, 1.0],            // event-driven, big swings
    },
    regimeVolMult: { calm: [1.0, 1.2], boom: [1.0, 1.3], crash: [1.1, 1.5], chaos: [1.5, 2.2] },
    startPrice: [30, 100],
  },
  materials: {
    drift:       [-0.002, 0.012],
    vol:         [0.045, 0.09],
    momentum:    [-0.10, 0.20],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0008, 0.0020],
    regimeBeta: {
      calm:  [0.8, 1.1],
      boom:  [1.0, 1.6],
      crash: [-1.4, -0.5],
      chaos: [0.8, 1.8],
    },
    regimeVolMult: { calm: [1.0, 1.2], boom: [1.0, 1.3], crash: [1.3, 1.7], chaos: [1.5, 2.0] },
    startPrice: [15, 60],
  },
  transport: {
    drift:       [0.002, 0.012],
    vol:         [0.035, 0.075],
    momentum:    [-0.05, 0.15],
    bankruptcyFloor: [0, 0],
    dividend:    [0.0010, 0.0020],
    regimeBeta: {
      calm:  [0.9, 1.1],
      boom:  [1.1, 1.7],
      crash: [-1.2, -0.5],
      chaos: [-0.4, 0.6],
    },
    regimeVolMult: { calm: [0.9, 1.1], boom: [1.0, 1.3], crash: [1.2, 1.6], chaos: [1.3, 1.7] },
    startPrice: [30, 90],
  },
  utilities: {
    drift:       [0.003, 0.009],
    vol:         [0.015, 0.035],
    momentum:    [-0.20, 0.05],
    bankruptcyFloor: [0.30, 0.50],
    dividend:    [0.0025, 0.0040],
    regimeBeta: {
      calm:  [1.0, 1.2],
      boom:  [0.6, 1.0],
      crash: [-0.3, 0.3],
      chaos: [-0.2, 0.4],
    },
    regimeVolMult: { calm: [0.9, 1.0], boom: [0.9, 1.1], crash: [1.0, 1.3], chaos: [1.0, 1.3] },
    startPrice: [40, 110],
  },
};

const ALL_SECTORS: Sector[] = Object.keys(BANDS) as Sector[];

export interface GeneratedStock {
  def: AssetDef;
  startPrice: number;
  personality: StockPersonality;
}

export function generateStockRoster(rng: RNG, count: number): GeneratedStock[] {
  // Pick sectors with light constraints: ensure variety.
  // Always include 1 high-vol (tech/pharma/energy/materials) and 1 defensive (utilities/consumer/banking).
  const highVol: Sector[] = ["tech", "pharma", "energy", "materials"];
  const defensive: Sector[] = ["utilities", "consumer", "banking"];
  const chosen = new Set<Sector>();

  chosen.add(rng.pick(highVol));
  chosen.add(rng.pick(defensive));

  // Fill the rest from any unused sector
  const remaining = ALL_SECTORS.filter(s => !chosen.has(s));
  for (const s of rng.sample(remaining, count - chosen.size)) chosen.add(s);

  const stocks: GeneratedStock[] = [];
  const usedNames = new Set<string>();

  for (const sector of chosen) {
    const band = BANDS[sector];
    const pool = NAMES[sector];
    // pick an unused name+ticker
    let idx = rng.int(0, pool.names.length - 1);
    for (let tries = 0; tries < pool.names.length && usedNames.has(pool.names[idx]); tries++) {
      idx = (idx + 1) % pool.names.length;
    }
    usedNames.add(pool.names[idx]);

    const personality: StockPersonality = {
      sector,
      drift: rng.range(band.drift[0], band.drift[1]),
      vol: rng.range(band.vol[0], band.vol[1]),
      momentum: rng.range(band.momentum[0], band.momentum[1]),
      bankruptcyFloor: rng.range(band.bankruptcyFloor[0], band.bankruptcyFloor[1]),
      dividendRate: rng.range(band.dividend[0], band.dividend[1]),
      regimeBeta: {
        calm: rng.range(band.regimeBeta.calm[0], band.regimeBeta.calm[1]),
        boom: rng.range(band.regimeBeta.boom[0], band.regimeBeta.boom[1]),
        crash: rng.range(band.regimeBeta.crash[0], band.regimeBeta.crash[1]),
        chaos: rng.range(band.regimeBeta.chaos[0], band.regimeBeta.chaos[1]),
      },
      regimeVolMult: {
        calm: rng.range(band.regimeVolMult.calm[0], band.regimeVolMult.calm[1]),
        boom: rng.range(band.regimeVolMult.boom[0], band.regimeVolMult.boom[1]),
        crash: rng.range(band.regimeVolMult.crash[0], band.regimeVolMult.crash[1]),
        chaos: rng.range(band.regimeVolMult.chaos[0], band.regimeVolMult.chaos[1]),
      },
    };

    const startPrice = Math.round(rng.range(band.startPrice[0], band.startPrice[1]) * 100) / 100;

    stocks.push({
      def: {
        id: `stock_${sector}_${idx}`,
        kind: "stock",
        name: pool.names[idx],
        ticker: pool.tickers[idx],
        sector,
      },
      startPrice,
      personality,
    });
  }

  return stocks;
}
