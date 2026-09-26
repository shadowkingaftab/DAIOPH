import { memoryApi } from "../api";
import type { MemoryEntry } from "../types";

export async function listMemory(type?: string): Promise<MemoryEntry[]> {
  return memoryApi.list(type);
}

export async function getMemoryEntry(id: string): Promise<MemoryEntry> {
  return memoryApi.get(id);
}

export async function deleteMemoryEntry(id: string): Promise<void> {
  return memoryApi.delete(id);
}

export async function searchMemory(query: string): Promise<MemoryEntry[]> {
  // Placeholder: implement semantic search when backend supports it
  const all = await memoryApi.list();
  const lower = query.toLowerCase();
  return all.filter(
    (entry) =>
      entry.content.toLowerCase().includes(lower) ||
      entry.type.toLowerCase().includes(lower)
  );
}