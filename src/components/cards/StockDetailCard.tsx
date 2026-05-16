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

export function StockDetailCard({
  asset, you, hinted, ordersEnabled, onTrade,
}: {
  asset: PublicAsset; you: PublicPlayer; hinted: boolean;
  ordersEnabled: boolean; onTrade: (a: TradeAction) => void;
}) {
  const [armed, setArmed] = useState<Armed>(1);
  const [customOpen, setCustomOpen] = useState(false);
  const [customVal, setCustomVal] = useState("");
  const [ordersOpen, setOrdersOpen] = useState(false);

  const owned = Math.floor(you.shares[asset.id] ?? 0);
  const change = asset.prevPrice ? (asset.price - asset.prevPrice) / asset.prevPrice : 0;
  const up = change >= 0;
  const profit = profitFor(you, asset);
  const maxBuy = asset.price > 0 ? Math.floor(you.cash / asset.price) : 0;
  const myOrders = you.restingOrders.filter(o => o.assetId === asset.id);
  const value = owned * asset.price;

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
    <div className={clsx("stock-card", up && "up", hinted && "hilite")}>
      <div className="scname">{asset.name}</div>
      {asset.sector && <div className="scsub">{asset.sector} · {asset.ticker}</div>}
      <div className="scprice-row">
        <span className="scprice">${asset.price.toFixed(2)}</span>
        <span className={clsx("scdelta", up ? "up" : "dn")}>{(Math.abs(change)*100).toFixed(2)}%</span>
      </div>
      <div className="scchart">
        <AnimatedSparkline
          data={asset.history} viewW={200} viewH={120}
          stroke={up ? "#736b1f" : "#9a4131"}
          fill={up ? "#9c9234" : "#cd6450"}
          strokeWidth={1.2}
        />
      </div>
      <div className="scfoot">
        <div className="row">
          <span className="lbl">Profit</span>
          <span className="v">
            <AnimatedNumber value={profit}
              format={(n) => `${n < 0 ? "-" : ""}$${Math.abs(Math.round(n)).toLocaleString()}`}
              flashOnChange={false} />
          </span>
        </div>
        <div className="row">
          <span className="lbl">Position</span>
          <span className="v">{owned} sh · ${Math.round(value).toLocaleString()}</span>
        </div>
      </div>
      <div className="scbtns">
        <button className="btn sm" disabled={owned <= 0} onClick={() => fire("sell")}>sell</button>
        <button className="btn sm" disabled={maxBuy <= 0} onClick={() => fire("buy")}>buy</button>
      </div>
      {customOpen ? (
        <div className="scqty">
          <input
            autoFocus type="number" min={1} value={customVal}
            onChange={(e) => setCustomVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") { setArmed("custom"); setCustomOpen(false); }
              if (e.key === "Escape") { setCustomOpen(false); setCustomVal(""); }
            }}
            placeholder="qty"
            style={{ width: "100%", border:"1px solid #8b7e3f", background:"rgba(255,250,210,0.6)", padding:"1px 4px", fontFamily:"IM Fell DW Pica,serif", fontSize:11, fontVariantNumeric:"tabular-nums" }}
          />
        </div>
      ) : (
        <div className="scqty">
          {PRESETS.map((p) => (
            <button key={p} className={clsx(armed === p && "armed")} onClick={() => setArmed(p)}>{p}</button>
          ))}
          <button className={clsx(armed === "custom" && "armed")} onClick={() => setCustomOpen(true)}>⋯</button>
          <button className={clsx(armed === "max" && "armed")} onClick={() => setArmed("max")}>ALL</button>
        </div>
      )}
      {ordersEnabled && (
        <div className="scorders">
          <button
            className={clsx("order-btn", myOrders.length > 0 && "has")}
            onClick={() => setOrdersOpen(!ordersOpen)}
          >
            orders {myOrders.length > 0 ? `(${myOrders.length})` : "▾"}
          </button>
        </div>
      )}
      {ordersOpen && (
        <OrderPanel asset={asset} you={you} onClose={() => setOrdersOpen(false)} onTrade={onTrade} />
      )}
    </div>
  );
}
