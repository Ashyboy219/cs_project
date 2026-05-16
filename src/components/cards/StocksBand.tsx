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

export function StocksBand({
  stocks, you, hintedIds, ordersEnabled = false, onTrade,
}: {
  stocks: PublicAsset[];
  you: PublicPlayer;
  hintedIds?: Set<string>;
  ordersEnabled?: boolean;
  onTrade: (a: TradeAction) => void;
}) {
  const [openOrders, setOpenOrders] = useState<string | null>(null);
  return (
    <div className={clsx("card stocks-band", openOrders && "has-popover")}>
      <span className="help">?</span>
      <div className="title">Individual Stocks</div>
      <div className="stocks-grid">
        {stocks.map((s) => (
          <MiniStock
            key={s.id}
            asset={s}
            you={you}
            hinted={!!hintedIds?.has(s.id)}
            ordersEnabled={ordersEnabled}
            ordersOpen={openOrders === s.id}
            onToggleOrders={() => setOpenOrders(openOrders === s.id ? null : s.id)}
            onTrade={onTrade}
          />
        ))}
        {Array.from({ length: Math.max(0, 5 - stocks.length) }).map((_, i) => (
          <div key={`empty-${i}`} style={{ visibility: "hidden" }} />
        ))}
      </div>
    </div>
  );
}

function MiniStock({
  asset, you, hinted, ordersEnabled, ordersOpen, onToggleOrders, onTrade,
}: {
  asset: PublicAsset; you: PublicPlayer; hinted: boolean;
  ordersEnabled: boolean; ordersOpen: boolean;
  onToggleOrders: () => void;
  onTrade: (a: TradeAction) => void;
}) {
  const [armed, setArmed] = useState<Armed>(1);
  const [customOpen, setCustomOpen] = useState(false);
  const [customVal, setCustomVal] = useState("");

  const owned = Math.floor(you.shares[asset.id] ?? 0);
  const change = asset.prevPrice ? (asset.price - asset.prevPrice) / asset.prevPrice : 0;
  const up = change >= 0;
  const profit = profitFor(you, asset);
  const maxBuy = asset.price > 0 ? Math.floor(you.cash / asset.price) : 0;

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

  const myOrders = you.restingOrders.filter(o => o.assetId === asset.id);

  return (
    <div className={clsx("ministock", up && "up", hinted && "hilite", ordersOpen && "has-popover")}>
      <div className="mname" title={asset.name}>{asset.name}</div>
      <div className="pr">
        <span className="price">${asset.price.toFixed(2)}</span>
        <span className={clsx("delta", up ? "up" : "dn")}>{(Math.abs(change)*100).toFixed(2)}%</span>
      </div>
      <div className="plbl"><span className="lbl-sort">PROFIT</span></div>
      <div className="pval">
        <AnimatedNumber value={profit} format={(n) => `${n < 0 ? "-" : ""}$${Math.abs(Math.round(n)).toLocaleString()}`} flashOnChange={false} />
      </div>
      <div className="chartbox">
        <span className="shares">shares:<br/>{owned.toLocaleString()}</span>
        <AnimatedSparkline
          data={asset.history} viewW={120} viewH={30}
          stroke={up ? "#736b1f" : "#9a4131"}
          fill={up ? "#9c9234" : "#cd6450"}
          strokeWidth={1}
        />
      </div>
      <div className="btns">
        <button className="btn sm" disabled={owned <= 0} onClick={() => fire("sell")}>sell</button>
        <button className="btn sm" disabled={maxBuy <= 0} onClick={() => fire("buy")}>buy</button>
      </div>
      {customOpen ? (
        <div className="qty">
          <input
            autoFocus type="number" min={1} value={customVal}
            onChange={(e) => setCustomVal(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { setArmed("custom"); setCustomOpen(false); } if (e.key === "Escape") { setCustomOpen(false); setCustomVal(""); } }}
            placeholder="qty"
            style={{ width: "100%", border:"1px solid #8b7e3f", background:"rgba(255,250,210,0.6)", padding:"1px 4px", fontFamily:"IM Fell DW Pica,serif", fontSize:11, fontVariantNumeric:"tabular-nums" }}
          />
        </div>
      ) : (
        <div className="qty">
          {PRESETS.map((p) => (
            <button key={p} className={clsx(armed === p && "armed")} onClick={() => setArmed(p)}>{p}</button>
          ))}
          <button className={clsx(armed === "custom" && "armed")} onClick={() => setCustomOpen(true)}>⋯</button>
          <button className={clsx("max", armed === "max" && "armed")} onClick={() => setArmed("max")}>ALL</button>
        </div>
      )}
      {ordersEnabled && (
        <button
          className={clsx("order-btn", myOrders.length > 0 && "has")}
          style={{ marginTop: 2 }}
          onClick={onToggleOrders}
        >
          orders {myOrders.length > 0 ? `(${myOrders.length})` : "▾"}
        </button>
      )}
      {ordersOpen && (
        <OrderPanel asset={asset} you={you} onClose={onToggleOrders} onTrade={onTrade} />
      )}
    </div>
  );
}
