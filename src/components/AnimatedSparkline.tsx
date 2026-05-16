"use client";
// Sparkline that smoothly tweens between data sets via requestAnimationFrame.
// On each new data array, it animates from the current displayed values to the
// target over `duration` ms. New endpoints appear by interpolating from the
// previous last-value to their real value, so there's no shape-snap.

import { useEffect, useRef, useState } from "react";

const DURATION = 350;

function useAnimatedData(target: number[]): number[] {
  const [displayed, setDisplayed] = useState<number[]>(() => target.slice());
  const lastTickKey = useRef<string>("");
  const fromRef = useRef<number[]>(target);
  const targetRef = useRef<number[]>(target);
  const startRef = useRef<number>(0);

  useEffect(() => {
    // cheap stability check: only restart anim when length changes or last value changes
    const key = `${target.length}|${target[target.length - 1] ?? 0}`;
    if (key === lastTickKey.current) return;
    lastTickKey.current = key;

    fromRef.current = displayed.slice();
    targetRef.current = target;
    startRef.current = performance.now();

    let raf = 0;
    const step = (t: number) => {
      const k = Math.min(1, (t - startRef.current) / DURATION);
      const e = 1 - Math.pow(1 - k, 3);
      const tgt = targetRef.current;
      const fr = fromRef.current;
      const out = new Array(tgt.length);
      for (let i = 0; i < tgt.length; i++) {
        const fromVal = fr[i] !== undefined
          ? fr[i]
          : (fr[fr.length - 1] ?? tgt[i]);
        out[i] = fromVal + (tgt[i] - fromVal) * e;
      }
      setDisplayed(out);
      if (k < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return displayed;
}

export function AnimatedSparkline({
  data, viewW = 300, viewH = 90, stroke, fill, strokeWidth = 1.2,
}: {
  data: number[]; viewW?: number; viewH?: number;
  stroke: string; fill: string; strokeWidth?: number;
}) {
  const animated = useAnimatedData(data);
  if (!animated || animated.length < 2) {
    return <svg viewBox={`0 0 ${viewW} ${viewH}`} preserveAspectRatio="none" aria-hidden />;
  }
  const min = Math.min(...animated);
  const max = Math.max(...animated);
  const range = Math.max(1e-6, max - min);
  const stepX = viewW / (animated.length - 1);
  const pts: string[] = [];
  for (let i = 0; i < animated.length; i++) {
    const x = i * stepX;
    const y = viewH - ((animated[i] - min) / range) * (viewH - 4) - 2;
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  const area = `0,${viewH} ${pts.join(" ")} ${viewW},${viewH}`;
  return (
    <svg viewBox={`0 0 ${viewW} ${viewH}`} preserveAspectRatio="none" aria-hidden>
      <polygon points={area} fill={fill} />
      <polyline points={pts.join(" ")} fill="none" stroke={stroke} strokeWidth={strokeWidth} strokeLinejoin="round" />
    </svg>
  );
}
