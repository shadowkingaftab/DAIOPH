import { useState } from "react";

export default function Settings() {
  const [route, setRoute] = useState("Hybrid");
  const [apiKey, setApiKey] = useState("");
  const [notifications, setNotifications] = useState(true);

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

        <div className="settings-group">
          <label>Grok API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Paste your xAI Grok API key"
          />
        </div>

        <div className="settings-group">
          <label>
            <input
              type="checkbox"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
            />
            Enable notifications
          </label>
        </div>

        <button className="save-button">Save Settings</button>
      </div>
    </div>
  );
}