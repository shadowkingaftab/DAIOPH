import { useAppStore } from "../state";

export default function SystemStatus() {
  const { systemStatus } = useAppStore();

  if (!systemStatus) {
    return <div className="system-status">System status unavailable</div>;
  }

  const statusClass = `status-${systemStatus.status}`;

  return (
    <div className={`system-status ${statusClass}`}>
      <div className="status-indicator">
        <span className="status-dot" />
        <span className="status-label">{systemStatus.status.toUpperCase()}</span>
      </div>
      <div className="status-details">
        <span>Version: {systemStatus.version}</span>
        <span>Uptime: {Math.floor(systemStatus.uptime / 60)}m</span>
        <span>Models: {systemStatus.models.length} loaded</span>
      </div>
    </div>
  );
}