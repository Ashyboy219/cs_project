"use client";
import clsx from "clsx";

export type TabId = "floor" | "stocks" | "metals" | "cash" | "research" | "orders";

const TABS: { id: TabId; label: string }[] = [
  { id: "floor",    label: "Floor"    },
  { id: "stocks",   label: "Stocks"   },
  { id: "metals",   label: "Metals"   },
  { id: "cash",     label: "Cash"     },
  { id: "research", label: "Research" },
  { id: "orders",   label: "Orders"   },
];

export function TabBar({
  active, onChange, rightSlot,
}: {
  active: TabId;
  onChange: (id: TabId) => void;
  rightSlot?: React.ReactNode;
}) {
  return (
    <div className="tab-bar">
      {TABS.map((t) => (
        <button
          key={t.id}
          className={clsx("tab", active === t.id && "active")}
          onClick={() => onChange(t.id)}
        >
          {t.label}
        </button>
      ))}
      {rightSlot && <div className="right">{rightSlot}</div>}
    </div>
  );
}
