# DAIOPH Mobile Application

React Native mobile client for the DAIOPH Edge AI platform.

## Overview

The mobile app provides on-the-go access to DAIOPH's edge AI orchestration:
- Chat with edge/cloud AI models
- Device & model monitoring
- Memory browsing
- Voice input support

## Structure

```
apps/mobile/
├── android/          # Android platform config
├── ios/              # iOS platform config
├── src/
│   ├── App.tsx       # Root component
│   ├── api.ts        # API client
│   └── device.ts     # Device utilities
└── README.md
```

## Setup

```bash
# Install dependencies
npm install

# Run on Android
npx react-native run-android

# Run on iOS
npx react-native run-ios
```

## Requirements

- Node.js 18+
- React Native CLI
- Android Studio / Xcode (platform-specific)