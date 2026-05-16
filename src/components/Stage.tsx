"use client";
// 1280×720 frame that scales to viewport, preserving aspect.
import { useEffect, useRef } from "react";

export function Stage({ children }: { children: React.ReactNode }) {
  const frameRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const fit = () => {
      const f = frameRef.current;
      if (!f) return;
      const sw = window.innerWidth;
      const sh = window.innerHeight;
      const k = Math.min(sw / 1280, sh / 720);
      f.style.transform = `scale(${k})`;
    };
    fit();
    window.addEventListener("resize", fit);
    return () => window.removeEventListener("resize", fit);
  }, []);
  return (
    <div className="stage">
      <div className="frame" ref={frameRef}>
        {children}
      </div>
    </div>
  );
}
