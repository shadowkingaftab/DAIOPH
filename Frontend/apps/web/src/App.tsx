import { useEffect } from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import { useAppStore } from "./state";
import { deviceApi } from "./api";
import { chatApi } from "./api";
import Home from "./pages/Home";
import Memory from "./pages/Memory";
import Models from "./pages/Models";
import Device from "./pages/Device";
import Settings from "./pages/Settings";

export default function App() {
  const setSystemStatus = useAppStore((state) => state.setSystemStatus);
  const setError = useAppStore((state) => state.setError);
  const setMessages = useAppStore((state) => state.setMessages);
  useEffect(() => {
    deviceApi.status().then(setSystemStatus).catch(() => setError("API is offline. Start the DAIOPH API on port 8000."));
    chatApi.history().then(setMessages).catch(() => undefined);
  }, [setSystemStatus, setError, setMessages]);
  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">DAIOPH</div>
        <NavLink to="/" end>Home</NavLink>
        <NavLink to="/memory">Memory</NavLink>
        <NavLink to="/models">Models</NavLink>
        <NavLink to="/device">Device</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </nav>
      <main className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/memory" element={<Memory />} />
          <Route path="/models" element={<Models />} />
          <Route path="/device" element={<Device />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
