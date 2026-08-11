# DAIOPH iOS

iOS platform configuration for the DAIOPH mobile app.

## Setup

1. Install Xcode 15+
2. Run `cd ios && pod install`
3. Run `npx react-native run-ios` from `apps/mobile/`

## Requirements

- Xcode 15+
- CocoaPods
- iOS 15+ deployment target

## Permissions

The app requires:
- `NSMicrophoneUsageDescription` — voice input
- `NSCameraUsageDescription` — image capture (optional)
- `NSPhotoLibraryUsageDescription` — image upload (optional)