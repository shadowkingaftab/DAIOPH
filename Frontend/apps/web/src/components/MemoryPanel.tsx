import { useEffect } from "react";
import { useAppStore } from "../state";
import { memoryApi } from "../api";

export default function MemoryPanel() {
  const { memory, setMemory, setError } = useAppStore();

  useEffect(() => {
    memoryApi
      .list()
      .then(setMemory)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load memory"));
  }, [setMemory, setError]);

  return (
    <div className="memory-panel">
      <h3>Memory</h3>
      {memory.length === 0 ? (
        <p className="empty">No memory entries yet.</p>
      ) : (
        <ul>
          {memory.map((entry) => (
            <li key={entry.id}>
              <span className="memory-type">{entry.type}</span>
              <span className="memory-content">{entry.content}</span>
              <span className="memory-time">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}