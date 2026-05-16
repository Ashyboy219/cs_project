"use client";

import { Suspense, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useStackMatch } from "@/lib/useStackMatch";
import { Stage } from "@/components/Stage";
import { Sidebar } from "@/components/Sidebar";
import { NewsStrip } from "@/components/NewsStrip";
import { PhaseTimer } from "@/components/PhaseTimer";
import { TabBar, type TabId } from "@/components/TabBar";
import { SavingsCard } from "@/components/cards/SavingsCard";
import { CDCard } from "@/components/cards/CDCard";
import { IndexCard } from "@/components/cards/IndexCard";
import { BondsCard } from "@/components/cards/BondsCard";
import { WheatCard } from "@/components/cards/WheatCard";
import { GoldCard } from "@/components/cards/GoldCard";
import { StocksBand } from "@/components/cards/StocksBand";
import { StockDetailCard } from "@/components/cards/StockDetailCard";
import { EndScreen } from "@/components/EndScreen";
import type { Sector } from "@/lib/types";

export default function GamePage() {
  return (
    <Suspense fallback={<Booting />}>
      <GameInner />
    </Suspense>
  );
}

function Booting() {
  return (
    <Stage>
      <div className="layout">
        <aside className="sidebar" />
        <section className="main" style={{ display: "grid", placeItems: "center" }}>
          <div style={{ color: "#cfc89a", fontFamily: "IM Fell English SC,serif", letterSpacing: ".18em" }}>
            SHUFFLING THE TAPE…
          </div>
        </section>
      </div>
    </Stage>
  );
}

function GameInner() {
  const router = useRouter();
  const params = useSearchParams();
  const name = params.get("name") || "Player";
  const avatar = params.get("avatar") || "🎩";
  const length = (params.get("length") as "quick" | "full") || "full";
  const reveal = (params.get("reveal") as "story" | "pro") || "story";

  const { match, you, ended, error, visible, phase, phaseEndsAt, trade, rematch }
    = useStackMatch({ name, avatar, length, reveal });
  const [pinnedNewsId, setPinnedNewsId] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("floor");

  const pinnedHighlight = useMemo(() => {
    if (!match || !pinnedNewsId) return { assetIds: new Set<string>(), sector: null as Sector | null };
    const item = match.news.find(n => n.id === pinnedNewsId);
    if (!item) return { assetIds: new Set<string>(), sector: null as Sector | null };
    const ids = new Set<string>();
    if (item.aboutAssetId) ids.add(item.aboutAssetId);
    if (item.aboutSector) for (const a of match.assets) if (a.sector === item.aboutSector) ids.add(a.id);
    return { assetIds: ids, sector: item.aboutSector ?? null };
  }, [match, pinnedNewsId]);

  if (!match || !you) return <Booting />;

  const isVisible = (id: string) => visible.has(id);
  const stocksAll = match.assets.filter(a => a.kind === "stock");
  const stocks = stocksAll.filter(a => isVisible(a.id));

  const savings = match.assets.find(a => a.kind === "savings" && isVisible(a.id));
  const cd      = match.assets.find(a => a.kind === "cd"      && isVisible(a.id));
  const index   = match.assets.find(a => a.kind === "index"   && isVisible(a.id));
  const bonds   = match.assets.find(a => a.kind === "bonds"   && isVisible(a.id));
  const wheat   = match.assets.find(a => a.kind === "wheat"   && isVisible(a.id));
  const gold    = match.assets.find(a => a.kind === "gold"    && isVisible(a.id));

  const isHinted = (id: string) => match.hintedAssetId === id || pinnedHighlight.assetIds.has(id);
  const hintedStockIds = new Set<string>();
  if (match.hintedAssetId) hintedStockIds.add(match.hintedAssetId);
  for (const id of pinnedHighlight.assetIds) hintedStockIds.add(id);

  const showNews = reveal === "pro";
  const mainCls = `main with-tabs ${showNews ? "with-news" : ""}`;

  return (
    <Stage>
      <div className="layout">
        <Sidebar match={match} you={you} onLobby={() => router.push("/")} />

        <section className={mainCls}>
          <TabBar
            active={tab}
            onChange={setTab}
            rightSlot={<PhaseTimer phase={phase} endsAt={phaseEndsAt} />}
          />

          {showNews && (
            <NewsStrip
              items={match.news}
              pinnedId={pinnedNewsId}
              onPin={setPinnedNewsId}
            />
          )}

          {tab === "floor" && (
            <>
              {savings ? <SavingsCard asset={savings} you={you} onTrade={trade} /> : <LockedCard slot="savings" />}
              {cd      ? <CDCard      asset={cd}      you={you} onTrade={trade} /> : <LockedCard slot="cd" />}
              {index   ? <IndexCard   asset={index}   you={you} hinted={isHinted(index.id)} ordersEnabled={showNews} onTrade={trade} /> : <LockedCard slot="index" />}
              <StocksBand stocks={stocks} you={you} hintedIds={hintedStockIds} ordersEnabled={showNews} onTrade={trade} />
              {bonds ? <BondsCard asset={bonds} you={you} onTrade={trade} /> : <LockedCard slot="bonds" />}
              {wheat ? <WheatCard asset={wheat} you={you} hinted={isHinted(wheat.id)} ordersEnabled={showNews} onTrade={trade} /> : <LockedCard slot="wheat" />}
              {gold  ? <GoldCard  asset={gold}  you={you} hinted={isHinted(gold.id)}  ordersEnabled={showNews} onTrade={trade} /> : <LockedCard slot="gold" />}
            </>
          )}

          {tab === "stocks" && (
            <div className="stocks-page">
              {stocks.map((s) => (
                <StockDetailCard
                  key={s.id}
                  asset={s} you={you}
                  hinted={isHinted(s.id)}
                  ordersEnabled={showNews}
                  onTrade={trade}
                />
              ))}
              {Array.from({ length: Math.max(0, 5 - stocks.length) }).map((_, i) => (
                <div key={`empty-${i}`} className="stock-card" style={{ opacity: 0.18 }}>
                  <div className="scname">— Locked —</div>
                  <div className="scsub" style={{ marginTop: 12 }}>revealed soon</div>
                </div>
              ))}
            </div>
          )}

          {tab === "metals" && (
            <Placeholder text="Metals & commodities will land here next push." />
          )}
          {tab === "cash" && (
            <Placeholder text="Detailed cash instruments coming next push." />
          )}
          {tab === "research" && (
            <Placeholder text="News history, sector heat, macro indicators — coming next push." />
          )}
          {tab === "orders" && (
            <Placeholder text="Order book overview — coming next push." />
          )}
        </section>
      </div>

      {error && (
        <div style={{
          position:"absolute", left:"50%", bottom:18, transform:"translateX(-50%)",
          background:"#7c2e23", color:"#f5edcd",
          fontFamily:"IM Fell English SC,serif", letterSpacing:".18em", fontSize:11,
          padding:"6px 14px", borderRadius:3, zIndex:10,
        }}>{error.toUpperCase()}</div>
      )}

      {ended && (
        <EndScreen
          finalRanking={ended.finalRanking}
          you={you}
          onRematch={rematch}
          onLobby={() => router.push("/")}
        />
      )}
    </Stage>
  );
}

function LockedCard({ slot }: { slot: string }) {
  const cls = `card ${slot}`;
  return (
    <div className={cls} style={{ opacity: 0.18, pointerEvents: "none" }}>
      <div className="title">— Locked —</div>
      <div className="body" style={{ display: "grid", placeItems: "center" }}>
        <div style={{ fontFamily: "IM Fell English, serif", fontStyle: "italic", color: "#4a4732" }}>
          revealed soon
        </div>
      </div>
    </div>
  );
}

function Placeholder({ text }: { text: string }) {
  return (
    <div style={{
      gridColumn: "1 / span 3",
      display: "grid", placeItems: "center",
      padding: 60,
      background: "rgba(255,255,255,.04)",
      border: "1px dashed rgba(207,200,154,.25)",
      borderRadius: 5,
      fontFamily: "IM Fell English, serif", fontStyle: "italic",
      color: "rgba(207,200,154,.55)", fontSize: 14, textAlign: "center",
    }}>
      {text}
    </div>
  );
}
