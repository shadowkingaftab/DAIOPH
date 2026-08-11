import { Platform } from "react-native";

// Determine API base URL based on platform
const API_BASE =
  Platform.OS === "android"
    ? "http://10.0.2.2:8000" // Android emulator loopback
    : "http://localhost:8000"; // iOS simulator

export interface ChatResponse {
  final_output: string;
  route: string;
  times?: {
    edge_ai: number;
    traditional: number;
    savings: number;
    savings_percent: number;
  };
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function sendChat(
  message: string,
  route: "ODA" | "Hybrid" | "Cloud"
): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, route }),
  });
}

export async function getSystemStatus(): Promise<unknown> {
  return request("/api/device/status");
}

export { API_BASE };