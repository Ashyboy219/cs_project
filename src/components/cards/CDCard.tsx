"use client";
import { useState } from "react";
import type { PublicAsset, PublicPlayer, TradeAction } from "@/lib/types";
import { cdProfit } from "@/lib/profit";
import { AnimatedNumber } from "../AnimatedNumber";

const SLOTS = 3;

export function CDCard({
  asset, you, onTrade,
}: { asset: PublicAsset; you: PublicPlayer; onTrade: (a: TradeAction) => void }) {
  const profit = cdProfit(you);
  const [openSlot, setOpenSlot] = useState<number | null>(null);
  const [val, setVal] = useState("");

  const submit = () => {
    const n = Math.max(0, Math.floor(Number(val) || 0));
    if (n >= 100) onTrade({ type: "cd:open", amount: n });
    setOpenSlot(null); setVal("");
  };

  const matured = you.cdMatured ?? [];
  const active = you.cds ?? [];
  type Slot =
    | { kind: "matured"; payout: number; principal: number; idx: number }
    | { kind: "active"; principal: number; mr: number }
    | { kind: "empty" };
  const slots: Slot[] = [
    ...matured.map((m, i) => ({ kind: "matured" as const, payout: m.payout, principal: m.principal, idx: i })),
    ...active.map((cd) => ({ kind: "active" as const, principal: cd.principal, mr: cd.monthsRemaining })),
  ].slice(0, SLOTS);
  while (slots.length < SLOTS) slots.push({ kind: "empty" });

  return (
    <div className="card cd">
      <span className="help">?</span>
      <div className="title">{asset.name}</div>
      <div className="body">
        <div className="cd-coins">
          {slots.map((s, i) => {
            if (s.kind === "matured") {
              return (
                <button key={`m-${i}`} className="coin" onClick={() => onTrade({ type: "cd:collect", index: s.idx })} title={`Principal $${s.principal}`}>
                  <div className="amt">${Math.round(s.payout).toLocaleString()}</div>
                  <div className="collect">collect</div>
                </button>
              );
            }
            if (s.kind === "active") {
              return (
                <div key={`a-${i}`} className="coin pending">
                  <div className="amt">${Math.round(s.principal).toLocaleString()}</div>
                  <div className="collect">{s.mr}mo</div>
                </div>
              );
            }
            return (
              <button key={`e-${i}`} className="coin empty" onClick={() => setOpenSlot(i)}>
                <div className="amt">open</div>
                <div className="collect">+</div>
              </button>
            );
          })}
        </div>

        {openSlot !== null && (
          <div className="numpad">
            <input
              autoFocus type="number" min={100} value={val}
              onChange={(e) => setVal(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") submit(); if (e.key === "Escape") { setOpenSlot(null); setVal(""); } }}
              placeholder={`open CD $ (≥100, max ${Math.floor(you.cash)})`}
            />
            <button className="btn sm" onClick={() => setVal(String(Math.floor(you.cash)))}>all</button>
            <button className="btn sm" onClick={submit}>ok</button>
            <button className="btn sm" onClick={() => { setOpenSlot(null); setVal(""); }}>×</button>
          </div>
        )}

        <div className="meta-row">
          <div className="label lbl-sort">PROFIT</div>
          <div className="value">
            <AnimatedNumber value={profit} format={(n) => `${n < 0 ? "-" : ""}$${Math.abs(Math.round(n)).toLocaleString()}`} flashOnChange={false} />
          </div>
        </div>
      </div>
    </div>
  );
}
