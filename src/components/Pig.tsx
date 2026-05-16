"use client";

export function Pig() {
  return (
    <svg
      viewBox="0 0 240 180"
      width="205"
      height="155"
      style={{ position: "absolute", left: 18, top: 14 }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="pigGrad" cx="50%" cy="55%" r="60%">
          <stop offset="0" stopColor="#e89497" />
          <stop offset="1" stopColor="#cb6c70" />
        </radialGradient>
        <pattern id="pigDots" x="0" y="0" width="6" height="6" patternUnits="userSpaceOnUse">
          <circle cx="3" cy="3" r="0.6" fill="#b65d62" opacity={0.5} />
        </pattern>
      </defs>

      {/* hat */}
      <g transform="translate(46,2)">
        <rect x="0" y="42" width="68" height="6" fill="#1f2014" />
        <rect x="14" y="0" width="44" height="42" fill="#1f2014" />
        <rect x="14" y="32" width="44" height="6" fill="#7a3e2a" />
      </g>

      {/* back legs */}
      <rect x="156" y="138" width="14" height="22" rx="3" fill="#a85055" />
      <rect x="84" y="138" width="14" height="22" rx="3" fill="#a85055" />

      {/* body */}
      <ellipse cx="128" cy="110" rx="80" ry="42" fill="url(#pigGrad)" />
      <ellipse cx="128" cy="110" rx="80" ry="42" fill="url(#pigDots)" />

      {/* front legs */}
      <rect x="106" y="138" width="14" height="22" rx="3" fill="#b65d62" />
      <rect x="178" y="138" width="14" height="22" rx="3" fill="#b65d62" />
      <ellipse cx="125" cy="120" rx="55" ry="22" fill="#e89497" opacity={0.4} />

      {/* tail */}
      <path d="M 205 100 q 18 -10 14 -24 q -3 -10 -14 -7" stroke="#b65d62" strokeWidth={5} fill="none" strokeLinecap="round" />

      {/* head */}
      <ellipse cx="64" cy="88" rx="42" ry="36" fill="url(#pigGrad)" />
      <ellipse cx="64" cy="88" rx="42" ry="36" fill="url(#pigDots)" />
      <ellipse cx="55" cy="98" rx="34" ry="22" fill="#e89497" opacity={0.35} />

      {/* ear */}
      <path d="M 78 56 L 100 50 L 92 76 Z" fill="#b65d62" />
      <path d="M 82 58 L 95 54 L 90 70 Z" fill="#d57b7e" />

      {/* snout */}
      <ellipse cx="28" cy="92" rx="20" ry="16" fill="#c66c70" />
      <ellipse cx="28" cy="92" rx="20" ry="16" fill="url(#pigDots)" />
      <ellipse cx="22" cy="89" rx="2.2" ry="3" fill="#2a1212" />
      <ellipse cx="22" cy="97" rx="2.2" ry="3" fill="#2a1212" />
      <path d="M 24 102 q 6 4 14 2" stroke="#7a3839" strokeWidth={1.5} fill="none" strokeLinecap="round" />

      {/* eye */}
      <circle cx="62" cy="78" r="3" fill="#2a1212" />
      <circle cx="63" cy="77" r="0.9" fill="#fff" opacity={0.9} />

      {/* $ frame */}
      <circle cx="130" cy="104" r="22" fill="none" stroke="#8a2a2c" strokeWidth={2} opacity={0.55} />
      <text x="130" y="115" textAnchor="middle" fontFamily="IM Fell DW Pica, serif" fontWeight={400} fontSize={32} fill="#7a2426" opacity={0.8}>$</text>
    </svg>
  );
}

export function MoneyStack() {
  return (
    <svg className="moneystack" viewBox="0 0 180 100" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="42" width="82" height="36" fill="#6f8246" stroke="#2f3a18" strokeWidth={1.5} />
      <rect x="10" y="42" width="82" height="7" fill="#56682f" />
      <rect x="10" y="49" width="82" height="2" fill="#2f3a18" />
      <rect x="10" y="71" width="82" height="2" fill="#2f3a18" />
      <circle cx="51" cy="60" r="9" fill="#6f8246" stroke="#2f3a18" strokeWidth={1.2} />
      <text x="51" y="64" textAnchor="middle" fontFamily="IM Fell DW Pica,serif" fontSize={11} fill="#2f3a18">$</text>

      <rect x="62" y="56" width="86" height="36" fill="#85986a" stroke="#2f3a18" strokeWidth={1.5} />
      <rect x="62" y="56" width="86" height="7" fill="#6f8246" />
      <rect x="62" y="63" width="86" height="2" fill="#2f3a18" />
      <rect x="62" y="85" width="86" height="2" fill="#2f3a18" />
      <circle cx="105" cy="74" r="9" fill="#85986a" stroke="#2f3a18" strokeWidth={1.2} />
      <text x="105" y="78" textAnchor="middle" fontFamily="IM Fell DW Pica,serif" fontSize={11} fill="#2f3a18">$</text>

      <g transform="rotate(-8 35 90)">
        <rect x="4" y="80" width="62" height="20" fill="#9ab47a" stroke="#2f3a18" strokeWidth={1.4} />
        <circle cx="35" cy="90" r="7" fill="#9ab47a" stroke="#2f3a18" strokeWidth={1.2} />
      </g>
    </svg>
  );
}
