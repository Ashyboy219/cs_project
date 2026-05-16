"use client";
// Tweens between numeric values smoothly. Use for prices, profits, balances.
// Briefly flashes color (green/red) to signal direction of change.

import { useEffect, useRef, useState } from "react";
import clsx from "clsx";

export function AnimatedNumber({
  value,
  format,
  className,
  duration = 350,
  flashOnChange = true,
}: {
  value: number;
  format: (n: number) => string;
  className?: string;
  duration?: number;
  flashOnChange?: boolean;
}) {
  const [displayed, setDisplayed] = useState(value);
  const fromRef = useRef(value);
  const startRef = useRef(0);
  const lastVal = useRef(value);
  const [flash, setFlash] = useState<null | "up" | "down">(null);

  useEffect(() => {
    if (value === lastVal.current) return;
    if (flashOnChange) {
      const dir = value > lastVal.current ? "up" : "down";
      setFlash(dir);
      const t = setTimeout(() => setFlash(null), 500);
      // capture for cleanup
      var flashTimer = t;
    }
    fromRef.current = displayed;
    startRef.current = performance.now();
    lastVal.current = value;

    let raf = 0;
    const step = (t: number) => {
      const k = Math.min(1, (t - startRef.current) / duration);
      const e = 1 - Math.pow(1 - k, 3);
      setDisplayed(fromRef.current + (value - fromRef.current) * e);
      if (k < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => {
      cancelAnimationFrame(raf);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      if (typeof flashTimer !== "undefined") clearTimeout(flashTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <span className={clsx(className, flash === "up" && "flash-up", flash === "down" && "flash-down")}>
      {format(displayed)}
    </span>
  );
}
