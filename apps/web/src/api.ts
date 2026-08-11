import axios from "axios";
import type { ChatMessage, MemoryEntry, ModelInfo, SystemStatus } from "./types";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

export const chatApi = {
  async sendMessage(message: string, route: string): Promise<ChatMessage> {
    const { data } = await api.post("/chat", { message, route });
    return data;
  },
};

export const memoryApi = {
  async list(type?: string): Promise<MemoryEntry[]> {
    const { data } = await api.get("/memory", { params: { type } });
    return data;
  },
  async get(id: string): Promise<MemoryEntry> {
    const { data } = await api.get(`/memory/${id}`);
    return data;
  },
  async delete(id: string): Promise<void> {
    await api.delete(`/memory/${id}`);
  },
};

export const modelsApi = {
  async list(): Promise<ModelInfo[]> {
    const { data } = await api.get("/models");
    return data;
  },
  async load(id: string): Promise<void> {
    await api.post(`/models/${id}/load`);
  },
  async unload(id: string): Promise<void> {
    await api.post(`/models/${id}/unload`);
  },
};

export const deviceApi = {
  async status(): Promise<SystemStatus> {
    const { data } = await api.get("/device/status");
    return data;
  },
};

export default api;