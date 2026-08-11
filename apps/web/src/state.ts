import { create } from "zustand";
import type { ChatMessage, MemoryEntry, ModelInfo, SystemStatus } from "./types";

interface AppState {
  messages: ChatMessage[];
  memory: MemoryEntry[];
  models: ModelInfo[];
  systemStatus: SystemStatus | null;
  loading: boolean;
  error: string | null;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  setMemory: (memory: MemoryEntry[]) => void;
  setModels: (models: ModelInfo[]) => void;
  setSystemStatus: (status: SystemStatus) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  memory: [],
  models: [],
  systemStatus: null,
  loading: false,
  error: null,
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setMemory: (memory) => set({ memory }),
  setModels: (models) => set({ models }),
  setSystemStatus: (systemStatus) => set({ systemStatus }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));