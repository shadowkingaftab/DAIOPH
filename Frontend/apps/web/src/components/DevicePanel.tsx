import { useEffect } from "react";
import { useAppStore } from "../state";
import { deviceApi } from "../api";

export default function DevicePanel() {
  const { systemStatus, setSystemStatus, setError } = useAppStore();

  useEffect(() => {
    deviceApi
      .status()
      .then(setSystemStatus)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load device status"));
  }, [setSystemStatus, setError]);

  if (!systemStatus) {
    return <div className="device-panel">Loading device status...</div>;
  }

  const { device } = systemStatus;

  return (
    <div className="device-panel">
      <h3>Device</h3>
      <div className="device-info">
        <div className="device-row">
          <span>CPU</span>
          <span>{device.cpu}</span>
        </div>
        <div className="device-row">
          <span>Cores</span>
          <span>{device.cores}</span>
        </div>
        <div className="device-row">
          <span>RAM</span>
          <span>
            {(device.ram.used / 1024).toFixed(1)} / {(device.ram.total / 1024).toFixed(1)} GB
          </span>
        </div>
        {device.gpu && (
          <div className="device-row">
            <span>GPU</span>
            <span>{device.gpu.name}</span>
          </div>
        )}
        <div className="device-row">
          <span>Platform</span>
          <span>{device.platform}</span>
        </div>
        <div className="device-row">
          <span>Python</span>
          <span>{device.python}</span>
        </div>
      </div>
    </div>
  );
}