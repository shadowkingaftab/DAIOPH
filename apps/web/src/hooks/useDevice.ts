import { useCallback, useEffect } from "react";
import { useAppStore } from "../state";
import { deviceApi } from "../api";

export function useDevice() {
  const { systemStatus, setSystemStatus, setError } = useAppStore();

  const refresh = useCallback(async () => {
    try {
      const status = await deviceApi.status();
      setSystemStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load device status");
    }
  }, [setSystemStatus, setError]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { systemStatus, refresh };
}