# Cloud Deployment

## Overview

DAIOPH can be deployed to cloud infrastructure for multi-user, high-availability operation. Kubernetes is the recommended platform.

## Deployment Options

### Docker Compose (Single Server)

Best for small deployments:

```bash
cd deployment/docker
docker compose up -d
```

Includes: API server, worker, PostgreSQL, Redis.

### Kubernetes (Recommended)

Using raw manifests:
```bash
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/
```

Or Helm (recommended):
```bash
helm install daioph deployment/helm \
  --set ingress.hosts[0].host=daioph.yourdomain.com \
  --set config.database.url=postgresql://... \
  --set config.redis.url=redis://...
```

### Terraform (AWS)

Provisions EKS cluster and networking:

```bash
cd deployment/terraform
terraform init
terraform plan -var environment=prod
terraform apply
```

Then deploy the Helm chart to the created cluster.

## Architecture in Cloud

```
                    ┌─────────────┐
                    │   Ingress   │
                    └──────┬──────┘
              ┌────────────┼────────────┐
        ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
        │ API Pods  │ │ API Pods │ │ API Pods │
        └─────┬─────┘ └────┬─────┘ └────┬─────┘
              └────────────┼────────────┘
                    ┌──────┴──────┐
              ┌─────▼─────┐ ┌─────▼─────┐
              │  Workers  │ │  Memory   │
              └─────┬─────┘ └─────┬─────┘
                    └──────┬──────┘
              ┌────────────┼────────────┐
        ┌─────▼─────┐ ┌────▼─────┐
        │PostgreSQL │ │  Redis   │
        └───────────┘ └──────────┘
```

## Scaling

### Horizontal Pod Autoscaler
Enabled by default in the Helm chart:
- Min replicas: 2
- Max replicas: 10
- Target CPU: 80%

### Database Scaling
- Use managed PostgreSQL (RDS, Cloud SQL) for production
- Connection pooling configured via `pool_size`

## Configuration

Production settings via environment variables or `configs/production/config.yaml`:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `DAIOPH_MODE` | Set to `production` |
| `DAIOPH_LOG_LEVEL` | Logging verbosity |

Secrets should be stored in Kubernetes Secrets or a secrets manager.

## Monitoring

- Prometheus metrics at `:9090/metrics`
- Health probes: `/health` (liveness), `/ready` (readiness)
- Structured logs to stdout (collect with your log aggregator)

## Security Checklist

- [ ] TLS enabled via cert-manager / load balancer
- [ ] Secrets in Kubernetes Secrets (not env files)
- [ ] Network policies restricting pod communication
- [ ] Rate limiting enabled
- [ ] Non-root containers (default in chart)
- [ ] Regular image updates for CVEs

## Backup & Recovery

- PostgreSQL: automated snapshots + point-in-time recovery
- Memory data: persistent volumes with backup policies
- Model cache: reproducible from registry (re-downloadable)

## Cost Optimization

- Use spot/preemptible nodes for workers
- Scale down during off-hours if traffic is predictable
- Cache model weights in a shared volume to avoid re-downloads