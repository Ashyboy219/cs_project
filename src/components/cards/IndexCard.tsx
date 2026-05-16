"use client";
import { useState } from "react";
import clsx from "clsx";
import type { PublicAsset, PublicPlayer, TradeAction } from "@/lib/types";
import { profitFor } from "@/lib/profit";
import { AnimatedSparkline } from "../AnimatedSparkline";
import { AnimatedNumber } from "../AnimatedNumber";
import { OrderPanel } from "../OrderPanel";

export function IndexCard({
  asset, you, hinted, ordersEnabled = false, onTrade,
}: { asset: PublicAsset; you: PublicPlayer; hinted: boolean; ordersEnabled?: boolean; onTrade: (a: TradeAction) => void }) {
  const change = asset.prevPrice ? (asset.price - asset.prevPrice) / asset.prevPrice : 0;
  const up = change >= 0;
  const owned = Math.floor(you.shares[asset.id] ?? 0);
  const profit = profitFor(you, asset);
  const maxBuy = asset.price > 0 ? Math.floor(you.cash / asset.price) : 0;

  const [side, setSide] = useState<null | "buy" | "sell">(null);
  const [val, setVal] = useState("");
  const [ordersOpen, setOrdersOpen] = useState(false);
  const myOrders = you.restingOrders.filter(o => o.assetId === asset.id);

  const submit = () => {
    const n = Math.max(0, Math.floor(Number(val) || 0));
    if (n > 0) {
      if (side === "buy") onTrade({ type: "buy", assetId: asset.id, qty: Math.min(n, maxBuy) });
      else if (side === "sell") onTrade({ type: "sell", assetId: asset.id, qty: Math.min(n, owned) });
    }
    setSide(null); setVal("");
  };

  return (
    <div className={clsx("card index peach", hinted && "hilite", ordersOpen && "has-popover")}>
      <span className="help">?</span>
      <div className="title">{asset.name}</div>
      <div className="body">
        <div className="big-chart">
          <AnimatedSparkline
            data={asset.history} viewW={300} viewH={90}
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
        {side ? (
          <div className="numpad">
            <input
              autoFocus type="number" min={1} value={val}
              onChange={(e) => setVal(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") submit(); if (e.key === "Escape") { setSide(null); setVal(""); } }}
              placeholder={`${side} qty (max ${side === "buy" ? maxBuy : owned})`}
            />
            <button className="btn sm" onClick={() => setVal(String(side === "buy" ? maxBuy : owned))}>all</button>
            <button className="btn sm" onClick={submit}>ok</button>
            <button className="btn sm" onClick={() => { setSide(null); setVal(""); }}>×</button>
          </div>
        ) : (
          <div className="btn-row" style={{ alignItems: "center" }}>
            <button className="btn" disabled={owned <= 0} onClick={() => setSide("sell")}>sell</button>
            <button className="btn" disabled={maxBuy <= 0} onClick={() => setSide("buy")}>buy</button>
            {ordersEnabled && (
              <button
                className={clsx("order-btn", myOrders.length > 0 && "has")}
                onClick={() => setOrdersOpen(!ordersOpen)}
                style={{ marginLeft: "auto" }}
              >
                orders {myOrders.length > 0 ? `(${myOrders.length})` : "▾"}
              </button>
            )}
          </div>
        )}
        {ordersOpen && (
          <OrderPanel asset={asset} you={you} onClose={() => setOrdersOpen(false)} onTrade={onTrade} />
        )}
      </div>
    </div>
  );
}
