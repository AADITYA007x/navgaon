const ROOF_COLORS = ["#D85A30", "#993C1D", "#BA7517", "#A32D2D", "#712B13"];
const GROUND = ["#C0DD97", "#B3D58A", "#C9E3A6", "#B9D990", "#C4E09E", "#B0D386"];
const ROAD = "#D3D1C7";
const RIVER = "M-12 100 C 30 90, 70 110, 110 100 S 180 90, 220 100 S 285 110, 312 100";

const MOVERS = [
  { path: "M0 0 H300 V200 H0 Z", dur: 40, color: "#E24B4A", begin: 0 },
  { path: "M0 0 H300 V200 H0 Z", dur: 40, color: "#185FA5", begin: -20 },
  { path: "M300 200 H0 V0 H300 Z", dur: 50, color: "#FAC775", begin: -10 },
  { path: "M100 0 V200 V0", dur: 18, color: "#F1EFE8", begin: 0 },
  { path: "M200 200 V0 V200", dur: 22, color: "#5DCAA5", begin: -7 },
];

function place(b, n) {
  if (!n) return { x: b.x, y: b.y };
  return {
    x: n.x + 14 + ((b.x - n.x - 5) * 72) / 85,
    y: n.y + 18 + ((b.y - n.y - 5) * 66) / 85,
  };
}

function Home({ id }) {
  const roof = ROOF_COLORS[id % ROOF_COLORS.length];
  return (
    <>
      <rect x="-3.5" y="-1" width="7" height="5" fill="#F1EFE8" stroke="#5F5E5A" strokeWidth="0.3" />
      <polygon points="-4.6,-1 0,-5.2 4.6,-1" fill={roof} />
      <rect x="-0.8" y="1.6" width="1.6" height="2.4" fill="#5F5E5A" />
    </>
  );
}

function Shop({ closed }) {
  const awning = closed ? "#888780" : "#EF9F27";
  return (
    <>
      <rect x="-4" y="-2" width="8" height="6" fill={closed ? "#D3D1C7" : "#FAEEDA"} stroke="#5F5E5A" strokeWidth="0.3" />
      <path d="M-4.6 -2 L4.6 -2 L4 -4.6 L-4 -4.6 Z" fill={awning} />
      {[-3, -1, 1, 3].map((x) => (
        <rect key={x} x={x - 0.45} y="-4.6" width="0.9" height="2.6" fill="#ffffff" opacity="0.55" />
      ))}
      <rect x="-2.6" y="0" width="5.2" height="2" fill={closed ? "#888780" : "#85B7EB"} opacity="0.85" />
    </>
  );
}

function Civic() {
  return (
    <>
      <rect x="-6" y="-2" width="12" height="7" fill="#EEEDFE" stroke="#534AB7" strokeWidth="0.4" />
      <polygon points="-7,-2 0,-7 7,-2" fill="#7F77DD" />
      {[-4, -1.3, 1.3, 4].map((x) => (
        <rect key={x} x={x - 0.5} y="-1" width="1" height="5" fill="#AFA9EC" />
      ))}
    </>
  );
}

function Park() {
  return (
    <>
      <rect x="-9" y="-7" width="18" height="13" rx="4" fill="#97C459" opacity="0.75" />
      <circle cx="-4" cy="-1" r="3.2" fill="#3B6D11" />
      <circle cx="3" cy="-2.5" r="3.6" fill="#27500A" />
      <circle cx="1" cy="2.8" r="2.6" fill="#639922" />
    </>
  );
}

function Icon({ b }) {
  if (b.kind === "home") return <Home id={b.id} />;
  if (b.kind === "shop") return <Shop closed={!b.is_open} />;
  if (b.kind === "civic") return <Civic />;
  return <Park />;
}

function Roads({ stroke, width, dash }) {
  return (
    <g stroke={stroke} strokeWidth={width} strokeDasharray={dash} fill="none">
      <rect x="0" y="0" width="300" height="200" />
      <line x1="100" y1="0" x2="100" y2="200" />
      <line x1="200" y1="0" x2="200" y2="200" />
    </g>
  );
}

export default function CityMap({ neighborhoods, buildings, selectedId, onSelect }) {
  const hoodById = Object.fromEntries(neighborhoods.map((n) => [n.id, n]));
  const placed = buildings
    .map((b) => ({ b, ...place(b, hoodById[b.neighborhood_id]) }))
    .sort((p, q) => p.y - q.y);

  return (
    <div className="card">
      <div className="card-title">City map · hover and click any building</div>
      <div className="map-wrap">
        <svg viewBox="-12 -12 324 224" className="map">
          <rect x="-12" y="-12" width="324" height="224" fill="#A9CF7E" />

          {neighborhoods.map((n, i) => (
            <rect key={n.id} x={n.x} y={n.y} width="100" height="100" fill={GROUND[i % GROUND.length]} />
          ))}

          <path d={RIVER} stroke="#378ADD" strokeWidth="9" fill="none" strokeLinecap="round" />
          <path d={RIVER} stroke="#85B7EB" strokeWidth="1.6" fill="none" strokeDasharray="4 6" className="river-flow" />

          <g>
            <rect x="-3.2" y="-1.3" width="6.4" height="2.6" rx="1.3" fill="#F1EFE8" stroke="#444441" strokeWidth="0.3" />
            <rect x="-1" y="-0.8" width="2" height="1.6" fill="#D85A30" />
            <animateMotion path={RIVER} dur="70s" repeatCount="indefinite" rotate="auto" />
          </g>

          <Roads stroke={ROAD} width="5" />
          <Roads stroke="#F1EFE8" width="0.5" dash="2 2" />

          {MOVERS.map((m, i) => (
            <circle key={i} r="1.8" fill={m.color} stroke="#2C2C2A" strokeWidth="0.3">
              <animateMotion path={m.path} dur={`${m.dur}s`} begin={`${m.begin}s`} repeatCount="indefinite" />
            </circle>
          ))}

          {placed.map(({ b, x, y }) => {
            const closed = b.kind === "shop" && !b.is_open;
            const selected = b.id === selectedId;
            return (
              <g
                key={b.id}
                transform={`translate(${x} ${y})`}
                className="building"
                onClick={() => onSelect(b)}
              >
                <title>
                  {b.name}
                  {closed ? " (closed)" : ""}
                </title>
                {selected && <circle r="9" className="pulse" />}
                {selected && <circle r="8" fill="none" stroke="#E24B4A" strokeWidth="0.8" />}
                {b.kind !== "park" && (
                  <ellipse cx="0" cy="4.6" rx={b.kind === "civic" ? 7 : 4.6} ry="1.2" fill="#000000" opacity="0.15" />
                )}
                <g className="bicon">
                  <Icon b={b} />
                </g>
              </g>
            );
          })}

          {neighborhoods.map((n) => {
            const w = n.name.length * 3 + 8;
            return (
              <g key={`label-${n.id}`} pointerEvents="none">
                <rect x={n.x + 5} y={n.y + 5} width={w} height="9" rx="4.5" fill="#ffffff" opacity="0.88" />
                <text x={n.x + 5 + w / 2} y={n.y + 11.3} textAnchor="middle" fontSize="5.5" fontWeight="600" fill="#444441">
                  {n.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="legend">
        <span><span className="dot" style={{ background: "#D85A30" }} />Homes</span>
        <span><span className="dot" style={{ background: "#EF9F27" }} />Shops</span>
        <span><span className="dot" style={{ background: "#7F77DD" }} />Civic</span>
        <span><span className="dot" style={{ background: "#3B6D11" }} />Parks</span>
        <span><span className="dot" style={{ background: "#888780" }} />Closed</span>
        <span><span className="dot" style={{ background: "#378ADD" }} />River</span>
      </div>
    </div>
  );
}