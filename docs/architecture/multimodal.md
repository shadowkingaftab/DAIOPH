# Multi-Modal Architecture

## Overview

The multi-modal subsystem handles input and output across text, voice, vision, video, documents, and sensors, fusing them into a unified understanding.

## Input Processing (`multi_modal/input/`)

### Input Router (`input_router.py`)
Routes incoming data to the appropriate processor based on modality detection.

### Processors
- **Text Processor**: Tokenization, normalization, language detection
- **Voice Processor**: Audio capture coordination
- **Image Processor**: Image loading, preprocessing
- **Video Processor**: Video stream handling
- **Document Processor**: Document type dispatch
- **Sensor Processor**: Sensor data ingestion
- **Screen Processor**: Screen capture analysis

## Speech (`multi_modal/speech/`)
- **Speech-to-Text**: Whisper-based transcription (local)
- **Text-to-Speech**: Voice synthesis
- **Audio Preprocessor**: Noise reduction, normalization
- **Voice Activity Detection**: Endpointing for streaming

## Vision (`multi_modal/vision/`)
- **Image Understanding**: Scene description via SigLIP/CLIP
- **Object Detection**: Bounding box detection
- **OCR**: Text extraction from images
- **Screenshot Analysis**: UI element recognition
- **Visual Context**: Visual context building

## Video (`multi_modal/video/`)
- **Frame Sampler**: Keyframe extraction strategies
- **Temporal Context**: Cross-frame reasoning
- **Video Understanding**: Summarization of video content

## Documents (`multi_modal/documents/`)
- **PDF Parser**: Text + layout extraction
- **DOCX Parser**: Word document processing
- **Spreadsheets**: Tabular data extraction
- **Presentations**: Slide content extraction

## Sensors (`multi_modal/sensors/`)
- **Sensor Manager**: Unified sensor API
- **Device Sensors**: Battery, location, motion
- **Sensor Fusion**: Combining multiple sensor streams

## Fusion (`multi_modal/fusion/`)

Cross-modal integration:
- **Modality Fusion**: Early/late fusion strategies
- **Cross-Modal Attention**: Attention across modalities
- **Temporal Fusion**: Time-aligned multi-modal context
- **Context Alignment**: Aligning modalities to shared context

## Hardware Considerations

On edge devices:
- Whisper-tiny for STT (quantized)
- SigLIP-base for vision (quantized)
- Frame sampling reduces video processing cost
- Multimodal features can be disabled per config