import { Platform } from "react-native";

export interface DeviceInfo {
  platform: string;
  osVersion: string;
  deviceModel: string | null;
  isTablet: boolean;
  screenWidth: number;
  screenHeight: number;
}

/**
 * Retrieve basic device information.
 */
export function getDeviceInfo(): DeviceInfo {
  return {
    platform: Platform.OS,
    osVersion: Platform.Version as string,
    deviceModel: null, // Requires extra native module for precise model
    isTablet: false,
    screenWidth: 0,
    screenHeight: 0,
  };
}

/**
 * Determine the appropriate API base URL for the current platform.
 */
export function getApiBaseUrl(): string {
  return Platform.OS === "android"
    ? "http://10.0.2.2:8000"
    : "http://localhost:8000";
}