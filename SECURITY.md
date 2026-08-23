# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Security fixes |
| < 0.1   | ❌ Not supported |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

1. Use the private
   [security report template](.github/ISSUE_TEMPLATE/security_report.md)
   (GitHub routes it to the maintainers listed in `.github/CODEOWNERS`), or
2. Contact the repository owner directly through GitHub.

Include:

- A description of the vulnerability and its impact.
- Affected version/commit and reproduction steps (a minimal proof of concept is ideal).
- Any known mitigations.

You will receive an acknowledgment within **72 hours**. We aim to triage within
7 days and will keep you informed of progress. Once a fix is released, we will
credit reporters in the release notes unless anonymity is requested.

## Scope

### In scope

- Authentication, authorization, and session handling (`security/`).
- Sandbox escapes or unsafe filesystem/process tool execution
  (`tools/filesystem/`, `tools/system/`, `os_layer/`).
- Prompt-injection and threat-detection bypasses (`security/threat_detection/`).
- Secret leakage via logs, telemetry, exports, or Docker images.
- Insecure defaults in API endpoints (`APIs/rest/`, `APIs/websocket/`).
- Supply-chain issues in dependencies or CI workflows (`.github/workflows/`).

### Out of scope

- Vulnerabilities in third-party model weights or upstream llama.cpp/xAI services
  (report those upstream).
- Social engineering, physical attacks, or denial-of-service by volume.
- Issues requiring a malicious operator with local shell access on a trusted host.

## Secure Defaults in This Project

- **Secrets**: provided only via environment variables (`.env`, never committed;
  excluded from Docker build context via `.dockerignore`). No key material is
  hardcoded anywhere in the codebase.
- **Least privilege**: tools declare required permissions; destructive actions
  require explicit authorization before execution.
- **Sandboxing**: filesystem and process policies under `security/sandbox/`
  constrain what tool executions may touch.
- **Audit trail**: security-relevant events emit structured audit records
  (`security/audit/`) with correlation IDs; user content is redacted before
  export (`observability/telemetry/privacy_filter.py`).
- **Cryptography**: only established libraries are used; no custom crypto is
  implemented anywhere in this repository.
- **Containers**: production images run as a non-root user with minimal runtime
  dependencies and health checks.
- **CI hardening**: dependency auditing and security scanning run on every PR
  (`.github/workflows/security.yml`, `dependency-audit.yml`).

## Deployment Hardening Recommendations

1. Run the container with the bundled non-root user; do not override `USER`.
2. Restrict exposed ports to what you actually use (default: `8501` / `8000`).
3. Set resource limits as shown in `docker-compose.yml` (`deploy.resources`).
4. Mount model weights and logs as volumes rather than baking them into images.
5. Rotate `GROK_API_KEY` regularly and scope it to the minimum necessary rights.
6. Keep dependencies updated; Dependabot configuration is included
   (`.github/dependabot.yml`).

## Known Limitations

- The REST/WebSocket API layer is under active development; do not expose it
  directly to the public internet without an authenticating reverse proxy.
- Local GGUF inference executes native code; only load model files from sources
  you trust.