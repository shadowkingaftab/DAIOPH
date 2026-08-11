import Chat from "../components/Chat";
import SystemStatus from "../components/SystemStatus";

export default function Home() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>DAIOPH Chat</h1>
        <SystemStatus />
      </header>
      <Chat />
    </div>
  );
}