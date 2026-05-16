"use client";
import { useState } from "react";
import clsx from "clsx";
import type { PublicAsset, PublicPlayer, TradeAction } from "@/lib/types";
import { profitFor } from "@/lib/profit";
import { AnimatedSparkline } from "../AnimatedSparkline";
import { AnimatedNumber } from "../AnimatedNumber";
import { OrderPanel } from "../OrderPanel";

type Armed = number | "max" | "custom";
const PRESETS = [1, 75];

export function WheatCard({
  asset, you, hinted, ordersEnabled = false, onTrade,
}: { asset: PublicAsset; you: PublicPlayer; hinted: boolean; ordersEnabled?: boolean; onTrade: (a: TradeAction) => void }) {
  const change = asset.prevPrice ? (asset.price - asset.prevPrice) / asset.prevPrice : 0;
  const up = change >= 0;
  const owned = Math.floor(you.shares[asset.id] ?? 0);
  const profit = profitFor(you, asset);
  const maxBuy = asset.price > 0 ? Math.floor(you.cash / asset.price) : 0;

  const [armed, setArmed] = useState<Armed>(1);
  const [customOpen, setCustomOpen] = useState(false);
  const [customVal, setCustomVal] = useState("");
  const [ordersOpen, setOrdersOpen] = useState(false);
  const myOrders = you.restingOrders.filter(o => o.assetId === asset.id);

  const qtyFor = (side: "buy" | "sell") => {
    const cap = side === "buy" ? maxBuy : owned;
    if (armed === "max") return cap;
    if (armed === "custom") {
      const n = Math.max(0, Math.floor(Number(customVal) || 0));
      return Math.min(n, cap);
    }
    return Math.min(armed, cap);
  };
  const fire = (side: "buy" | "sell") => {
    const q = qtyFor(side);
    if (q <= 0) return;
    onTrade(side === "buy"
      ? { type: "buy", assetId: asset.id, qty: q }
      : { type: "sell", assetId: asset.id, qty: q });
  };

  return (
    <div className={clsx("card wheat blue", hinted && "hilite", ordersOpen && "has-popover")}>
      <span className="help">?</span>
      <div className="title">{asset.name}</div>
      <div className="body">
        <div className="wheat-stats">
          <span className={clsx("price", !up && "dn")}>${asset.price.toFixed(2)}</span>
          <span className={clsx("delta", up ? "up" : "dn")}>{(Math.abs(change)*100).toFixed(2)}%</span>
        </div>
        <div className="chart-area">
          <span className="shares-tag">shares: {owned.toLocaleString()}</span>
          <AnimatedSparkline
            data={asset.history} viewW={320} viewH={60}
            stroke={up ? "#736b1f" : "#9a4131"}
            fill={up ? "#9c9234" : "#cd6450"}
          />
        </div>
        <div className="meta-row">
          <div className="label lbl-sort">PROFIT</div>
          <div className={clsx("value", profit > 0 && "up", profit < 0 && "dn")}>
            <AnimatedNumber value={profit} format={(n) => `${n < 0 ? "-" : ""}$${Math.abs(Math.round(n)).toLocaleString()}`} flashOnChange={false} />
          </div>
        </div>
        {customOpen ? (
          <div className="numpad">
            <input
              autoFocus type="number" min={1} value={customVal}
              onChange={(e) => setCustomVal(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { setArmed("custom"); setCustomOpen(false); } if (e.key === "Escape") { setCustomOpen(false); setCustomVal(""); } }}
              placeholder="qty"
            />
            <button className="btn sm" onClick={() => { setArmed("custom"); setCustomOpen(false); }}>ok</button>
          </div>
        ) : (
          <div className="qty-line">
            <div className="nums">
              {PRESETS.map((p) => (
                <button key={p} className={clsx(armed === p && "armed")} onClick={() => setArmed(p)}>{p}</button>
              ))}
              <button className={clsx(armed === "custom" && "armed")} onClick={() => setCustomOpen(true)}>⋯</button>
              <button className={clsx(armed === "max" && "armed")} onClick={() => setArmed("max")}>ALL</button>
            </div>
            <div className="right">
              <button className="btn" disabled={owned <= 0} onClick={() => fire("sell")}>sell</button>
              <button className="btn" disabled={maxBuy <= 0} onClick={() => fire("buy")}>buy</button>
              {ordersEnabled && (
                <button
                  className={clsx("order-btn", myOrders.length > 0 && "has")}
                  onClick={() => setOrdersOpen(!ordersOpen)}
                >
                  orders {myOrders.length > 0 ? `(${myOrders.length})` : "▾"}
                </button>
              )}
            </div>
          </div>
        )}
        {ordersOpen && (
          <OrderPanel asset={asset} you={you} onClose={() => setOrdersOpen(false)} onTrade={onTrade} />
        )}
      </div>
    </div>
  );
}
