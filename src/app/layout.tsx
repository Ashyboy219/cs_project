import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stack — A Mid-Century Market",
  description: "A 20-year market game. Position, time, survive.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
