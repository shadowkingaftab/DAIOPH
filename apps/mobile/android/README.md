# DAIOPH Android

Android platform configuration for the DAIOPH mobile app.

## Setup

1. Install Android Studio with Android SDK
2. Configure `ANDROID_HOME` environment variable
3. Run `npx react-native run-android` from `apps/mobile/`

## Requirements

- Android SDK 34+
- Java 17+
- Android Studio Hedgehog or newer

## Permissions

The app requires:
- `INTERNET` — API communication
- `RECORD_AUDIO` — voice input
- `CAMERA` — image capture (optional)