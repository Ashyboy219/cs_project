import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Colors only. No backgroundImage keys with the same names — that's what
      // broke `bg-paper`/`bg-felt` last time (Tailwind picked the image, not the color).
      colors: {
        paper:     "#f1e7d0",
        paperDark: "#e6d8b8",
        paperLite: "#f7eedc",
        ink:       "#1a1f2b",
        inkSoft:   "#2c3242",
        inkFaded:  "#5a5f6e",
        brick:     "#9c3a2c",   // down
        forest:    "#2f6b3c",   // up
        brass:     "#b08a3e",
        ochre:     "#c9a23d",
        teal:      "#2e5d6a",
        felt:      "#1f2a26",
        feltDark:  "#15201d",
      },
      fontFamily: {
        slab:  ['"Roboto Slab"', "Georgia", "serif"],
        serif: ['"Source Serif Pro"', "Georgia", "serif"],
        mono:  ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        card:    "0 1px 0 rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.18), inset 0 0 0 1px rgba(0,0,0,0.06)",
        cardHint:"0 0 0 1.5px #c9a23d, 0 0 12px rgba(201,162,61,0.30)",
      },
    },
  },
  plugins: [],
};
export default config;
