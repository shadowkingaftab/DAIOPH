import type { ChatMessage } from "../types";

interface ResponseProps {
  message: ChatMessage;
}

export default function Response({ message }: ResponseProps) {
  return (
    <div className="response">
      <div className="response-content">{message.content}</div>
      {message.dag && (
        <details className="response-dag">
          <summary>View DAG</summary>
          <pre>{JSON.stringify(message.dag, null, 2)}</pre>
        </details>
      )}
      {message.results && (
        <details className="response-results">
          <summary>View Results</summary>
          <pre>{JSON.stringify(message.results, null, 2)}</pre>
        </details>
      )}
    </div>
  );
}