// Shared TypeScript types for the DAIOPH web client

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  route?: "ODA" | "Hybrid" | "Cloud";
  dag?: unknown;
  results?: Record<string, unknown>;
}

export interface MemoryEntry {
  id: string;
  type: "short-term" | "episodic" | "semantic" | "procedural" | "preference";
  content: string;
  metadata: Record<string, unknown>;
  timestamp: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  type: "local" | "remote" | "liquid";
  status: "loaded" | "unloaded" | "error" | "downloading";
  size?: string;
  quantized?: string;
  progress?: number;
}

export interface DeviceInfo {
  cpu: string;
  cores: number;
  ram: { total: number; used: number; free: number };
  gpu?: { name: string; vram: number };
  platform: string;
  python: string;
  uptime: number;
}

export interface SystemStatus {
  status: "ok" | "degraded" | "error";
  version: string;
  uptime: number;
  models: ModelInfo[];
  device: DeviceInfo;
}