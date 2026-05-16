"use client";
import clsx from "clsx";
import type { PublicNews } from "@/lib/types";

const SLOTS = 3;

const CRED_LABEL = { wire: "WIRE", analyst: "ANALYST", rumor: "RUMOR" } as const;
const CAT_LABEL = { macro: "MACRO", sector: "SECTOR", earnings: "EARNINGS", whisper: "WHISPER" } as const;

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

/** Pro-mode news strip. Shows up to 3 most-recent items as horizontal chips. */
export function NewsStrip({
  items, pinnedId, onPin,
}: {
  items: PublicNews[];
  pinnedId: string | null;
  onPin: (id: string | null) => void;
}) {
  const slots: (PublicNews | null)[] = items.slice(0, SLOTS);
  while (slots.length < SLOTS) slots.push(null);

  return (
    <div className="news-strip">
      {slots.map((n, i) => {
        if (!n) {
          return <div key={`empty-${i}`} className="news-chip empty">— quiet on the wire —</div>;
        }
        const tint = n.aboutSector === "tech" || n.aboutSector === "pharma" ? "peach"
                   : n.aboutSector === "utilities" || n.aboutSector === "consumer" ? "blush"
                   : n.aboutAssetId === "wheat" ? "blue"
                   : "";
        return (
          <button
            key={n.id}
            className={clsx("news-chip", tint, pinnedId === n.id && "pinned")}
            onClick={() => onPin(pinnedId === n.id ? null : n.id)}
            title={n.text}
          >
            <div className="meta">
              <span className={clsx("cred", n.credibility)}>{CRED_LABEL[n.credibility]}</span>
              <span>{CAT_LABEL[n.category]}</span>
              <span className="when">· Y{n.year} {MONTHS[(n.month - 1) % 12]}</span>
            </div>
            <div className="text">{n.text}</div>
          </button>
        );
      })}
    </div>
  );
}
