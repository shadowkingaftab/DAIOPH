import { deviceApi } from "../api";
import type { DeviceInfo, SystemStatus } from "../types";

export async function getSystemStatus(): Promise<SystemStatus> {
  return deviceApi.status();
}

export async function getDeviceInfo(): Promise<DeviceInfo> {
  const status = await deviceApi.status();
  return status.device;
}

export async function getModelHealth(): Promise<SystemStatus["models"]> {
  const status = await deviceApi.status();
  return status.models;
}