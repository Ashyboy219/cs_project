"use client";
import { useState } from "react";
import type { PublicAsset, PublicPlayer, TradeAction } from "@/lib/types";
import { AnimatedNumber } from "../AnimatedNumber";

export function SavingsCard({
  asset, you, onTrade,
}: { asset: PublicAsset; you: PublicPlayer; onTrade: (a: TradeAction) => void }) {
  const balance = you.shares["savings"] ?? 0;
  return (
    <div className="card savings">
      <span className="help">?</span>
      <div className="title">{asset.name}</div>
      <div className="body">
        <div className="bank-wrap">
          <BankIcon />
        </div>
        <div className="meta-row">
          <div className="label lbl-sort">BALANCE</div>
          <div className="value">
            <AnimatedNumber value={balance} format={(n) => `$${n.toFixed(2)}`} flashOnChange={false} />
          </div>
        </div>
        <ActionRow
          inLabel="deposit"
          outLabel="withdraw"
          inMax={Math.floor(you.cash)}
          outMax={Math.floor(balance)}
          onIn={(amt) => onTrade({ type: "savings:deposit", amount: amt })}
          onOut={(amt) => onTrade({ type: "savings:withdraw", amount: amt })}
        />
      </div>
    </div>
  );
}

function BankIcon() {
  return (
    <svg className="bank" width={92} height={72} viewBox="0 0 100 78" xmlns="http://www.w3.org/2000/svg">
      <polygon points="50,3 96,20 4,20" fill="#6e6418" stroke="#48420f" strokeWidth={1} />
      <rect x="2" y="20" width="96" height="3" fill="#48420f" />
      <g fill="#6e6418">
        <rect x="8"  y="26" width="5" height="32" />
        <rect x="22" y="26" width="5" height="32" />
        <rect x="36" y="26" width="5" height="32" />
        <rect x="50" y="26" width="5" height="32" />
        <rect x="64" y="26" width="5" height="32" />
        <rect x="78" y="26" width="5" height="32" />
        <rect x="88" y="26" width="5" height="32" />
      </g>
      <rect x="2" y="58" width="96" height="3" fill="#48420f" />
      <rect x="0" y="61" width="100" height="6" fill="#6e6418" stroke="#48420f" strokeWidth={1} />
      <rect x="-2" y="67" width="104" height="3" fill="#48420f" />
    </svg>
  );
}

export function ActionRow({
  inLabel, outLabel, inMax, outMax, onIn, onOut,
}: {
  inLabel: string; outLabel?: string;
  inMax: number; outMax: number;
  onIn: (amt: number) => void;
  onOut?: (amt: number) => void;
}) {
  const [side, setSide] = useState<null | "in" | "out">(null);
  const [val, setVal] = useState("");

  const submit = () => {
    const n = Math.max(0, Math.floor(Number(val) || 0));
    if (n > 0) {
      if (side === "in") onIn(Math.min(n, inMax));
      else if (side === "out" && onOut) onOut(Math.min(n, outMax));
    }
    setSide(null);
    setVal("");
  };

  if (side) {
    const cap = side === "in" ? inMax : outMax;
    return (
      <div className="numpad">
        <input
          autoFocus type="number" min={1} value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") submit(); if (e.key === "Escape") { setSide(null); setVal(""); } }}
          placeholder={`${(side === "in" ? inLabel : outLabel)} $ (max ${cap})`}
        />
        <button className="btn sm" onClick={() => setVal(String(cap))}>all</button>
        <button className="btn sm" onClick={submit}>ok</button>
        <button className="btn sm" onClick={() => { setSide(null); setVal(""); }}>×</button>
      </div>
    );
  }

  return (
    <div className="btn-row">
      {onOut && (
        <button className="btn" disabled={outMax <= 0} onClick={() => setSide("out")}>{outLabel}</button>
      )}
      <button className="btn" disabled={inMax <= 0} onClick={() => setSide("in")}>{inLabel}</button>
    </div>
  );
}
