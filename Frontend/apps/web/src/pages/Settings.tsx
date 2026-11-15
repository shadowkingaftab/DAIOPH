import { useState } from "react";

export default function Settings() {
  const [route, setRoute] = useState(() => localStorage.getItem("daiph-default-route") || "Hybrid");
  const [saved, setSaved] = useState(false);

  return (
    <div className="page">
      <header className="page-header">
        <h1>Settings</h1>
      </header>
      <div className="settings-form">
        <div className="settings-group">
          <label>Default Route</label>
          <select value={route} onChange={(e) => setRoute(e.target.value)}>
            <option value="ODA">ODA (Edge)</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Cloud">Cloud</option>
          </select>
        </div>

        <p className="settings-note">Cloud credentials stay on the server. Set <code>GROK_API_KEY</code> in your local <code>.env</code> file; never paste it into this browser.</p>
        <p className="settings-note">Cloud and hybrid messages are automatically screened for common personal identifiers and credentials before they leave this machine.</p>
        <button className="save-button" onClick={() => { localStorage.setItem("daiph-default-route", route); setSaved(true); }}>Save default route</button>
        {saved && <p className="success-note">Default route saved on this device.</p>}
      </div>
    </div>
  );
}
