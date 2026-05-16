"use client";
import { useState } from "react";
import clsx from "clsx";
import type { PublicAsset, PublicPlayer, TradeAction } from "@/lib/types";
import { profitFor } from "@/lib/profit";
import { AnimatedNumber } from "../AnimatedNumber";

export function BondsCard({
  asset, you, onTrade,
}: { asset: PublicAsset; you: PublicPlayer; onTrade: (a: TradeAction) => void }) {
  const units = you.shares["bonds"] ?? 0;
  const value = units * asset.price;
  const profit = profitFor(you, asset);
  const [side, setSide] = useState<null | "buy" | "sell">(null);
  const [val, setVal] = useState("");

  const submit = () => {
    const n = Math.max(0, Math.floor(Number(val) || 0));
    if (n > 0) {
      if (side === "buy") onTrade({ type: "bonds:buy", amount: Math.min(n, Math.floor(you.cash)) });
      else if (side === "sell") onTrade({ type: "bonds:sell", amount: Math.min(n, Math.floor(value)) });
    }
    setSide(null); setVal("");
  };

  // Two pies show holding split visually. Each represents half the value.
  const pieAmount = Math.round(value / 2);
  const showPies = value > 1;

  return (
    <div className="card bonds blush">
      <span className="help">?</span>
      <div className="title">{asset.name}</div>
      <div className="body">
        {showPies ? (
          <div className="pie-row">
            <div className="pie-wrap">
              <span className="pie-amt">${pieAmount.toLocaleString()}</span>
              <div className="pie" style={{ background: "conic-gradient(#9c9234 0% 60%, #c4b75e 60% 100%)" }} />
            </div>
            <div className="pie-wrap">
              <span className="pie-amt">${(Math.round(value) - pieAmount).toLocaleString()}</span>
              <div className="pie" style={{ background: "conic-gradient(#9c9234 0% 78%, #c4b75e 78% 100%)" }} />
            </div>
          </div>
        ) : (
          <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center",
                        fontFamily:"IM Fell English, serif", fontStyle:"italic", fontSize:13, color:"#4a4732" }}>
            ${asset.price.toFixed(2)} par · yield {asset.bondYieldAnnual ? (asset.bondYieldAnnual * 100).toFixed(2) : "–"}%
          </div>
        )}

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
              placeholder={`${side} $ (max ${side === "buy" ? Math.floor(you.cash) : Math.floor(value)})`}
            />
            <button className="btn sm" onClick={() => setVal(String(side === "buy" ? Math.floor(you.cash) : Math.floor(value)))}>all</button>
            <button className="btn sm" onClick={submit}>ok</button>
            <button className="btn sm" onClick={() => { setSide(null); setVal(""); }}>×</button>
          </div>
        ) : (
          <div className="single-buy">
            {value > 0 && <button className="btn" onClick={() => setSide("sell")}>sell</button>}
            <button className="btn" disabled={you.cash < 1} onClick={() => setSide("buy")}>buy</button>
          </div>
        )}
      </div>
    </div>
  );
}
