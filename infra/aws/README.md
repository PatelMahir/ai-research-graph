# AWS Deployment Notes

> Guidance only — nothing here provisions infrastructure. Wire these into your IaC
> (Terraform/CDK) and apply through the GitLab CI review gate.

## Target topology

| Concern        | AWS service                                   |
|----------------|-----------------------------------------------|
| Containers     | ECS on Fargate (backend + frontend services)  |
| Load balancing | Application Load Balancer (HTTPS, ACM cert)   |
| Database       | RDS for PostgreSQL (Multi-AZ in prod)         |
| Cache/queue    | ElastiCache for Redis                         |
| Vector DB      | Qdrant on ECS/EC2, or Qdrant Cloud            |
| Object storage | S3 (raw PDFs / ingest artifacts)              |
| Secrets        | AWS Secrets Manager (DB creds, API keys)      |
| Registry       | ECR (images pushed by GitLab CI)              |
| Observability  | CloudWatch Logs + Container Insights          |

## Deployment strategy

- **Blue/green** via CodeDeploy for the backend service (zero-downtime, fast rollback).
- Health gate on `/api/health` and `/api/ready` before shifting traffic.
- Canary option: shift 10% → 50% → 100% with CloudWatch alarm rollback.

## Security baseline (PCI-DSS / SOC 2)

- No secrets in images or env files committed to git — pull from Secrets Manager at runtime.
- TLS in transit (ALB + RDS/ElastiCache in-transit encryption); encryption at rest on
  RDS, ElastiCache, S3, and EBS.
- Least-privilege task roles; security groups scoped to service-to-service traffic only.
- RDS/Redis in private subnets; no public ingress except through the ALB.
- Structured audit logging without PII (see `app/core/logging.py`).

## CI/CD

`.gitlab-ci.yml` builds and pushes images to ECR and triggers an ECS rollout on the
`main` branch behind a manual approval gate.
