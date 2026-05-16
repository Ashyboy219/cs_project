"use client";
// Queued-orders panel. Renders inside a card via absolute positioning.
// Shows existing resting orders for the asset + a small form to place new ones.

import { useState } from "react";
import clsx from "clsx";
import type { PublicAsset, PublicPlayer, RestingOrder, TradeAction } from "@/lib/types";

const KIND_LABEL: Record<RestingOrder["kind"], string> = {
  "limit-buy":   "BUY",
  "take-profit": "TP",
  "stop-loss":   "STOP",
};
const KIND_CHIP: Record<RestingOrder["kind"], string> = {
  "limit-buy":   "buy",
  "take-profit": "tp",
  "stop-loss":   "sl",
};

export function OrderPanel({
  asset, you, onClose, onTrade,
}: {
  asset: PublicAsset;
  you: PublicPlayer;
  onClose: () => void;
  onTrade: (a: TradeAction) => void;
}) {
  const orders = you.restingOrders.filter(o => o.assetId === asset.id);

  // Form state
  const [kind, setKind] = useState<RestingOrder["kind"]>("limit-buy");
  const [qtyStr, setQtyStr] = useState("1");
  // Default trigger nudges away from current by 5% in the appropriate direction
  const defaultTrigger = (k: RestingOrder["kind"]) => {
    const nudged = k === "limit-buy" ? asset.price * 0.95
                 : k === "take-profit" ? asset.price * 1.05
                 : asset.price * 0.95;
    return nudged.toFixed(2);
  };
  const [triggerStr, setTriggerStr] = useState(defaultTrigger("limit-buy"));

  const place = () => {
    const qty = Math.max(1, Math.floor(Number(qtyStr) || 0));
    const trigger = Number(triggerStr) || 0;
    if (qty <= 0 || trigger <= 0) return;
    onTrade({ type: "order:place", assetId: asset.id, kind, qty, trigger });
    // reset qty but keep trigger ballpark
    setQtyStr("1");
  };

  const cancel = (id: string) => onTrade({ type: "order:cancel", orderId: id });

  return (
    <div className="order-popover" onClick={(e) => e.stopPropagation()}>
      <div className="head">
        <span>QUEUED ORDERS · {asset.name}</span>
        <button className="x" onClick={onClose}>×</button>
      </div>
      {orders.length === 0 ? (
        <div className="empty">no orders queued</div>
      ) : (
        orders.map((o) => (
          <div key={o.id} className="row">
            <span className={clsx("kind-chip", KIND_CHIP[o.kind])}>{KIND_LABEL[o.kind]}</span>
            <span className="qty">{o.qty}</span>
            <span className="at">@</span>
            <span className="price">${o.trigger.toFixed(2)}</span>
            <button className="cancel" onClick={() => cancel(o.id)}>cancel</button>
          </div>
        ))
      )}
      <div className="form">
        <select
          value={kind}
          onChange={(e) => {
            const k = e.target.value as RestingOrder["kind"];
            setKind(k);
            setTriggerStr(defaultTrigger(k));
          }}
        >
          <option value="limit-buy">Buy @</option>
          <option value="take-profit">Sell @ ≥</option>
          <option value="stop-loss">Stop @ ≤</option>
        </select>
        <input
          type="number" min={1} value={qtyStr}
          onChange={(e) => setQtyStr(e.target.value)}
          placeholder="qty"
        />
        <input
          type="number" step={0.01} min={0} value={triggerStr}
          onChange={(e) => setTriggerStr(e.target.value)}
          placeholder="$ price"
        />
        <button className="place" onClick={place}>place</button>
      </div>
    </div>
  );
}

/** Compact list of order markers — to overlay on a sparkline. Returns absolute-positioned divs. */
export function OrderMarkers({
  orders, min, max,
}: { orders: RestingOrder[]; min: number; max: number }) {
  const range = Math.max(1e-6, max - min);
  return (
    <>
      {orders.map((o) => {
        // Render trigger relative to chart's min/max range
        if (o.trigger < min - range * 0.2 || o.trigger > max + range * 0.2) return null;
        const t = (o.trigger - min) / range; // 0..1
        const top = Math.max(0, Math.min(1, 1 - t)) * 100;
        const cls = o.kind === "limit-buy" ? "buy" : o.kind === "take-profit" ? "tp" : "sl";
        return (
          <div key={o.id} className={`order-marker ${cls}`} style={{ top: `${top}%`, left: "30%", right: 0 }}>
            <span className="label">${o.trigger.toFixed(2)}</span>
          </div>
        );
      })}
    </>
  );
}
