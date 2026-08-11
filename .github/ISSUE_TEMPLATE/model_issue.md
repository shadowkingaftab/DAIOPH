---
name: Model issue
about: Report an issue with a model in DAIOPH
title: "[MODEL] "
labels: model
assignees: ''
---

## Model Information
- **Model name**: [e.g., Qwen2-0.5B, DistilBERT, Grok]
- **Model type**: [Local GGUF / HuggingFace / Cloud API]
- **Model version**: 
- **Quantization**: [e.g., Q4_K_M, FP16, None]

## Issue Type
- [ ] Model fails to load
- [ ] Model produces incorrect output
- [ ] Model performance issue (slow)
- [ ] Model memory issue (OOM)
- [ ] Model download issue
- [ ] Model accuracy issue
- [ ] Model compatibility issue
- [ ] Other: _________

## Description
A clear and concise description of the model issue.

## Reproduction Steps
1. 
2. 
3. 

## Expected Behavior
What should the model do?

## Actual Behavior
What does the model actually do?

## Error Log
```
<!-- Paste error logs here -->
```

## Environment
- **OS**: 
- **Python version**: 
- **RAM**: 
- **GPU**: [None / NVIDIA / AMD / Apple Silicon]
- **VRAM**: 
- **llama-cpp-python version**: 
- **transformers version**: 

## Model Configuration
```yaml
# Paste relevant model config here
```

## Additional Context
- [ ] Model was working before (regression)
- [ ] Model is newly added
- [ ] Model requires special setup

## Checklist
- [ ] I have checked the model exists and is accessible
- [ ] I have verified the model path/ID is correct
- [ ] I have checked available memory
- [ ] I have searched for existing model issues