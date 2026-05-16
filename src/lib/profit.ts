// Per-asset profit calculation. Profit = realized + unrealized for the position.

import type { PublicAsset, PublicPlayer } from "./types";

export function profitFor(p: PublicPlayer, a: PublicAsset): number {
  const shares = p.shares[a.id] ?? 0;
  const basis = p.costBasis[a.id] ?? 0;
  const realized = p.realizedPL[a.id] ?? 0;
  const value = shares * a.price;
  return realized + (value - basis);
}

/** CD profit: realized (collected matured payouts minus their principal). Active CDs are at par. */
export function cdProfit(p: PublicPlayer): number {
  const realized = p.realizedPL["cd"] ?? 0;
  const matured = p.cdMatured.reduce((s, c) => s + (c.payout - c.principal), 0);
  return realized + matured;
}
