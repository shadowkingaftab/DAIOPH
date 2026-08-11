import { useState } from "react";
import { useAppStore } from "../state";
import { chatApi } from "../api";
import type { ChatMessage } from "../types";

export default function Chat() {
  const { messages, addMessage, setLoading, loading, setError } = useAppStore();
  const [input, setInput] = useState("");
  const [route, setRoute] = useState<"ODA" | "Hybrid" | "Cloud">("Hybrid");

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
      timestamp: Date.now(),
      route,
    };
    addMessage(userMessage);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const response = await chatApi.sendMessage(input, route);
      addMessage(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat">
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            {msg.route && <div className="message-route">Route: {msg.route}</div>}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <select value={route} onChange={(e) => setRoute(e.target.value as typeof route)}>
          <option value="ODA">ODA (Edge)</option>
          <option value="Hybrid">Hybrid</option>
          <option value="Cloud">Cloud</option>
        </select>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}