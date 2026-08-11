import { useState } from "react";

interface InputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function Input({ onSend, disabled }: InputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <div className="input-container">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
          }
        }}
        placeholder="Type your message... (Enter to send, Shift+Enter for newline)"
        rows={1}
        disabled={disabled}
      />
      <button onClick={handleSubmit} disabled={disabled || !value.trim()}>
        Send
      </button>
    </div>
  );
}