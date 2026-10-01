const COLORS = {
  home: "#F0997B",
  shop: "#FAC775",
  civic: "#AFA9EC",
  park: "#5DCAA5",
};

export default function CityMap({ neighborhoods, buildings, selectedId, onSelect }) {
  return (
    <div className="card">
      <div className="card-title">City map · click any building</div>
      <svg viewBox="-4 -4 308 208" className="map">
        {neighborhoods.map((n) => (
          <g key={n.id}>
            <rect x={n.x} y={n.y} width="100" height="100" className="hood" />
            <text x={n.x + 4} y={n.y + 8} className="hood-label">
              {n.name}
            </text>
          </g>
        ))}
        {buildings.map((b) => {
          const size = b.kind === "park" ? 10 : 6;
          const closed = b.kind === "shop" && !b.is_open;
          return (
            <rect
              key={b.id}
              x={b.x - size / 2}
              y={b.y - size / 2}
              width={size}
              height={size}
              rx="1"
              fill={closed ? "#B4B2A9" : COLORS[b.kind]}
              stroke={b.id === selectedId ? "#E24B4A" : "none"}
              strokeWidth="1.5"
              className="building"
              onClick={() => onSelect(b)}
            >
              <title>{b.name}{closed ? " (closed)" : ""}</title>
            </rect>
          );
        })}
      </svg>
      <div className="legend">
        <span><span className="dot" style={{ background: COLORS.home }} />Homes</span>
        <span><span className="dot" style={{ background: COLORS.shop }} />Shops</span>
        <span><span className="dot" style={{ background: COLORS.civic }} />Civic</span>
        <span><span className="dot" style={{ background: COLORS.park }} />Parks</span>
        <span><span className="dot" style={{ background: "#B4B2A9" }} />Closed</span>
      </div>
    </div>
  );
}