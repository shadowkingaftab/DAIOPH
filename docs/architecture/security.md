# Security Architecture

## Overview

DAIOPH implements defense-in-depth security: local data protection, sandboxed execution, permission management, and privacy-preserving learning.

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Data theft from device | At-rest encryption |
| Malicious tool execution | Sandboxing + permissions |
| Prompt injection | Input sanitization, intent validation |
| Model poisoning (federated) | Update validation, norm clipping |
| Memory exfiltration | Encrypted memory stores |
| Unauthorized API access | Authentication middleware |

## Components

### Encryption (`memory/privacy/encryption.py`)
- AES-256 encryption for sensitive memories
- Keys derived from device identity
- Per-user key isolation

### Permissions (`security/`)
- Capability-based permission system
- Tools declare required permissions
- User grants/revokes per capability
- Least-privilege defaults

### Sandbox (`tests/security/test_sandbox.py` validates)
- Tool execution in isolated environments
- Filesystem restrictions (scoped paths)
- Network restrictions per tool
- Resource limits (CPU, memory, time)

### Identity (`core/identity/`)
- **Device Identity**: Unique per installation
- **User Identity**: Local user profiles
- **Session Identity**: Ephemeral session tokens
- **Installation Identity**: Ties updates to installations

## API Security (`APIs/rest/middleware.py`)

1. **Authentication**: Token-based auth for remote access
2. **Rate Limiting**: Per-endpoint request throttling
3. **Input Validation**: Schema validation on all inputs
4. **CORS**: Restricted origins in production
5. **Security Headers**: HSTS, CSP, X-Frame-Options

## Injection Defense (`tests/security/test_injection.py`)

- SQL injection: Parameterized queries only
- XSS: Output encoding in web interfaces
- Prompt injection: Intent schema validation, instruction hierarchy

## Federated Privacy (`federated/privacy/`)

- **Differential Privacy**: DP-SGD with configurable ε/δ
- **Secure Aggregation**: Server never sees individual updates
- **Privacy Accountant**: Tracks cumulative privacy budget

## Audit & Monitoring

- Structured logging of security events
- Permission grant/deny audit trail
- Anomaly detection on unusual patterns