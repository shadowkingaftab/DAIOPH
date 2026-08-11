import { useCallback, useEffect } from "react";
import { useAppStore } from "../state";
import { memoryApi } from "../api";

export function useMemory() {
  const { memory, setMemory, setError } = useAppStore();

  const refresh = useCallback(async () => {
    try {
      const entries = await memoryApi.list();
      setMemory(entries);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memory");
    }
  }, [setMemory, setError]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const deleteEntry = useCallback(
    async (id: string) => {
      try {
        await memoryApi.delete(id);
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete memory entry");
      }
    },
    [refresh, setError]
  );

  return { memory, refresh, deleteEntry };
}