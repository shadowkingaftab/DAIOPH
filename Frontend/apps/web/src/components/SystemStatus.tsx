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
      <div className="status-details"><span>API v{systemStatus.version}</span><span>Online · {Math.floor(systemStatus.uptime / 60)}m uptime</span></div>
    </div>
  );
}
