import { useCallback } from "react";
import { useAppStore } from "../state";
import { chatApi } from "../api";
import type { ChatMessage } from "../types";

export function useChat() {
  const { messages, addMessage, setLoading, setError } = useAppStore();

  const sendMessage = useCallback(
    async (content: string, route: "ODA" | "Hybrid" | "Cloud" = "Hybrid") => {
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: Date.now(),
        route,
      };
      addMessage(userMessage);
      setLoading(true);
      setError(null);
      try {
        const response = await chatApi.sendMessage(content, route);
        addMessage(response);
        return response;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
        return null;
      } finally {
        setLoading(false);
      }
    },
    [addMessage, setLoading, setError]
  );

  return { messages, sendMessage };
}