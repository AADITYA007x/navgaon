export default function TownHall({ info, busy, message, onAction }) {
  if (!info) return null;

  return (
    <div className="card townhall">
      <div className="card-title">
        Town hall ·{" "}
        {info.available
          ? "You can make one decision today"
          : "Decision made. Advance to the next day to act again."}
      </div>
      <div className="action-grid">
        {info.actions.map((a) => (
          <button
            key={a.key}
            className="action"
            disabled={busy || !info.available}
            onClick={() => onAction(a.key)}
          >
            <span className="action-name">{a.name}</span>
            <span className="muted action-desc">{a.description}</span>
          </button>
        ))}
      </div>
      {message && <div className="action-message">{message}</div>}
    </div>
  );
}