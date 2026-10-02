import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import CityMap from "./components/CityMap";
import Newspaper from "./components/Newspaper";
import SidePanel from "./components/SidePanel";
import TownHall from "./components/TownHall";
import "./App.css";

export default function App() {
  const [city, setCity] = useState(null);
  const [stats, setStats] = useState(null);
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [residents, setResidents] = useState([]);
  const [events, setEvents] = useState([]);
  const [paper, setPaper] = useState(null);
  const [actionsInfo, setActionsInfo] = useState(null);
  const [actionMessage, setActionMessage] = useState("");
  const [autorun, setAutorun] = useState(null);
  const [now, setNow] = useState(0);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [selectedResident, setSelectedResident] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const dayRef = useRef(null);

  async function loadAll() {
    try {
      const [c, s, n, b, r, e, a, au] = await Promise.all([
        api.city(),
        api.stats(),
        api.neighborhoods(),
        api.buildings(),
        api.residents(),
        api.events(40),
        api.actions(),
        api.autorun(),
      ]);
      setCity(c);
      setStats(s);
      dayRef.current = s.day;
      setNeighborhoods(n);
      setBuildings(b);
      setResidents(r);
      setEvents(e);
      setActionsInfo(a);
      setAutorun(au);
      setError("");
      setSelectedBuilding((prev) => (prev ? b.find((x) => x.id === prev.id) || null : null));
      setSelectedResident((prev) => (prev ? r.find((x) => x.id === prev.id) || null : null));
      setPaper(await api.newspaper());
    } catch {
      setError("Can't reach the backend. Make sure uvicorn is running on port 8000.");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAll();

    const poll = setInterval(async () => {
      try {
        const s = await api.stats();
        if (s.day !== dayRef.current) loadAll();
      } catch {
        // backend not reachable, try again next time
      }
    }, 15000);

    const tick = setInterval(() => setNow(Date.now()), 1000);

    return () => {
      clearInterval(poll);
      clearInterval(tick);
    };
  }, []);

  async function run(action) {
    setBusy(true);
    setActionMessage("");
    try {
      await action();
      await loadAll();
    } catch {
      setError("Something went wrong. Check the backend terminal for errors.");
    }
    setBusy(false);
  }

  async function handleAction(key) {
    setBusy(true);
    try {
      const res = await api.doAction(key);
      setActionMessage(res.error || `${res.message} Tomorrow's newspaper will report it.`);
      await loadAll();
    } catch {
      setError("Something went wrong. Check the backend terminal for errors.");
    }
    setBusy(false);
  }

  async function changePaperDay(day) {
    setBusy(true);
    try {
      setPaper(await api.newspaper(day));
    } catch {
      setError("Couldn't load that newspaper.");
    }
    setBusy(false);
  }

  function selectBuilding(b) {
    setSelectedResident(null);
    setSelectedBuilding(b);
  }

  function selectResident(r) {
    setSelectedResident(r);
  }

  function countdown() {
    if (!autorun?.enabled || !autorun.next_run || !now) return null;
    const ms = new Date(autorun.next_run).getTime() - now;
    if (ms <= 0) return "any moment";
    const m = Math.floor(ms / 60000);
    const s = Math.floor((ms % 60000) / 1000);
    return `${m}m ${s}s`;
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <div className="title">
            {city?.name || "Navgaon"}
            {stats && <span className="day-badge">Day {stats.day}</span>}
          </div>
          {stats && (
            <div className="stats">
              <span>Population <b>{stats.population}</b></span>
              <span>Married <b>{stats.married}</b></span>
              <span>Unemployed <b>{stats.unemployed}</b></span>
              <span>Open shops <b>{stats.open_shops}</b></span>
            </div>
          )}
          {autorun?.enabled && (
            <div className="auto-badge">
              Auto-run on · next day in <b>{countdown()}</b>
            </div>
          )}
        </div>
        <div className="actions">
          <button className="primary" disabled={busy} onClick={() => run(api.nextDay)}>
            {busy ? "Working..." : "Next day"}
          </button>
          <button disabled={busy} onClick={() => run(() => api.simulate(10))}>
            Skip 10 days
          </button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      <TownHall info={actionsInfo} busy={busy} message={actionMessage} onAction={handleAction} />

      <div className="grid">
        <CityMap
          neighborhoods={neighborhoods}
          buildings={buildings}
          selectedId={selectedBuilding?.id}
          onSelect={selectBuilding}
        />
        <Newspaper
          cityName={city?.name || "Navgaon"}
          paper={paper}
          currentDay={stats?.day || 1}
          onChangeDay={changePaperDay}
          busy={busy}
        />
      </div>

      <div className="grid">
        <SidePanel
          building={selectedBuilding}
          resident={selectedResident}
          residents={residents}
          buildings={buildings}
          onSelectResident={selectResident}
          onSelectBuilding={selectBuilding}
        />
        <div className="card">
          <div className="card-title">Recent history</div>
          <ul className="timeline">
            {events.map((e) => (
              <li key={e.id}>
                <span className="muted">Day {e.day}</span>
                <span>{e.description}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}