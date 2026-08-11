import { chatApi } from "../api";
import type { ChatMessage } from "../types";

export interface ChatRequest {
  message: string;
  route: "ODA" | "Hybrid" | "Cloud";
}

export interface ChatResponse {
  message: ChatMessage;
  dag?: unknown;
  results?: Record<string, unknown>;
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const message = await chatApi.sendMessage(request.message, request.route);
  return { message };
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  // Placeholder: fetch from API when endpoint exists
  return [];
}