import axios from "axios";
import { useState } from "react";
import { useAppStore } from "../state";
import { chatApi } from "../api";
import type { ChatMessage } from "../types";

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data: unknown = error.response?.data;
    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }
  }
  return error instanceof Error ? error.message : "Failed to send message";
}

export default function Chat() {
  const { messages, addMessage, setLoading, loading, error, setError } = useAppStore();
  const [input, setInput] = useState("");
  const [route, setRoute] = useState<"ODA" | "Hybrid" | "Cloud">(() => {
    const saved = localStorage.getItem("daiph-default-route");
    return saved === "ODA" || saved === "Cloud" ? saved : "Hybrid";
  });

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const content = input.trim();
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: Date.now(),
      route,
    };
    addMessage(userMessage);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const response = await chatApi.sendMessage(content, route);
      addMessage(response);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat">
      <div className="privacy-notice"><span className="privacy-icon">◈</span><span><strong>Private by default</strong> · Email addresses, phone numbers, payment card numbers, and common API keys are redacted before cloud inference. Redacted text is not restored.</span></div>
      <div className="chat-messages">
        {messages.length === 0 && <div className="chat-empty"><span>✳</span><h2>What are you working on?</h2><p>Choose a local or cloud route and start a conversation.</p></div>}
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            {msg.route && <div className="message-route">Route: {msg.route}{msg.redacted_count ? ` · ${msg.redacted_count} sensitive item(s) redacted` : ""}</div>}
          </div>
        ))}
        {loading && <div className="message assistant typing">Thinking…</div>}
      </div>
      {error && <div className="error-banner" role="alert">{error}</div>}
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
          disabled={loading}
          maxLength={8000}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>{loading ? "Sending…" : "Send"}</button>
      </div>
      <div className="input-hint">Enter to send · Cloud requests are redacted on the server</div>
    </div>
  );
}
