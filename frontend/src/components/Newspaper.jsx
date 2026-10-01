export default function Newspaper({ cityName, paper, currentDay, onChangeDay, busy }) {
  if (!paper) {
    return <div className="card">Loading newspaper...</div>;
  }

  return (
    <div className="card newspaper">
      <div className="masthead">The {cityName} Herald</div>
      <div className="paper-nav">
        <button disabled={busy || paper.day <= 1} onClick={() => onChangeDay(paper.day - 1)}>
          ← Older
        </button>
        <span>Day {paper.day}</span>
        <button disabled={busy || paper.day >= currentDay} onClick={() => onChangeDay(paper.day + 1)}>
          Newer →
        </button>
      </div>
      <h2 className="headline">{paper.headline}</h2>
      {paper.articles.map((a, i) => (
        <article key={i}>
          <h3>{a.title}</h3>
          <p>{a.body}</p>
        </article>
      ))}
    </div>
  );
}