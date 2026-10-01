function initials(name) {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("");
}

export default function SidePanel({ building, resident, residents, buildings, onSelectResident, onSelectBuilding }) {
  const buildingById = Object.fromEntries(buildings.map((b) => [b.id, b]));
  const residentById = Object.fromEntries(residents.map((r) => [r.id, r]));

  if (resident) {
    const home = buildingById[resident.home_id];
    const work = resident.workplace_id ? buildingById[resident.workplace_id] : null;
    const partner = resident.partner_id ? residentById[resident.partner_id] : null;

    return (
      <div className="card">
        <div className="card-title">Resident</div>
        <div className="person">
          <div className="avatar">{initials(resident.name)}</div>
          <div>
            <div className="person-name">
              {resident.name}, {resident.age}
            </div>
            <div className="muted">{resident.job}</div>
          </div>
        </div>
        <div className="tags">
          {resident.traits.split(",").map((t) => (
            <span key={t} className="tag">{t}</span>
          ))}
        </div>
        <dl className="details">
          <dt>Home</dt>
          <dd>
            {home ? <button className="link" onClick={() => onSelectBuilding(home)}>{home.name}</button> : "—"}
          </dd>
          <dt>Works at</dt>
          <dd>
            {work ? <button className="link" onClick={() => onSelectBuilding(work)}>{work.name}</button> : "—"}
          </dd>
          <dt>Partner</dt>
          <dd>
            {partner ? (
              <button className="link" onClick={() => onSelectResident(partner)}>{partner.name}</button>
            ) : (
              "Single"
            )}
          </dd>
        </dl>
      </div>
    );
  }

  if (building) {
    const livesHere = residents.filter((r) => r.home_id === building.id);
    const worksHere = residents.filter((r) => r.workplace_id === building.id);
    const closed = building.kind === "shop" && !building.is_open;

    return (
      <div className="card">
        <div className="card-title">Building</div>
        <div className="person-name">{building.name}</div>
        <div className="muted">
          {building.kind}
          {closed ? " · closed" : ""}
        </div>

        {livesHere.length > 0 && (
          <>
            <div className="card-title" style={{ marginTop: 12 }}>Lives here</div>
            <ul className="list">
              {livesHere.map((r) => (
                <li key={r.id}>
                  <button className="link" onClick={() => onSelectResident(r)}>{r.name}</button>
                  <span className="muted"> · {r.age}, {r.job}</span>
                </li>
              ))}
            </ul>
          </>
        )}

        {worksHere.length > 0 && (
          <>
            <div className="card-title" style={{ marginTop: 12 }}>Works here</div>
            <ul className="list">
              {worksHere.map((r) => (
                <li key={r.id}>
                  <button className="link" onClick={() => onSelectResident(r)}>{r.name}</button>
                  <span className="muted"> · {r.job}</span>
                </li>
              ))}
            </ul>
          </>
        )}

        {livesHere.length === 0 && worksHere.length === 0 && (
          <p className="muted">Nobody lives or works here right now.</p>
        )}
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-title">Explore</div>
      <p className="muted">Click a building on the map to see who lives or works there.</p>
    </div>
  );
}