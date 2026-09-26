import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Memory from "./pages/Memory";
import Models from "./pages/Models";
import Device from "./pages/Device";
import Settings from "./pages/Settings";

export default function App() {
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