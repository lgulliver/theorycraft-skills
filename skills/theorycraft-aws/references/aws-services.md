# AWS Service Selection Guide

## Compute

| Need | Service | Config guidance |
|---|---|---|
| Containerised workloads, K8s | Amazon EKS | Managed node groups (m6i/m7i); Graviton (m7g) for Linux workloads; Fargate for serverless nodes |
| Containers without K8s | Amazon ECS | Fargate (serverless) for variable; EC2 launch type for cost-optimised steady workloads |
| Serverless functions | AWS Lambda | Node.js/Python for cold-start sensitivity; SnapStart for Java; Graviton2 ARM for 20% better price/perf |
| Web apps / APIs | AWS Elastic Beanstalk or App Runner | App Runner for simple containerised HTTP apps; Beanstalk for more control |
| General VMs | Amazon EC2 | t3/t4g burstable dev; m6i/m7i general prod; r6i/r7i memory-intensive; Graviton (g suffix) where possible |
| Windows VMs | EC2 Windows | m7i.large+ for CCaaS-style workloads; License Included or BYOL on Dedicated Hosts |
| Batch processing | AWS Batch | Managed compute environments with Spot for cost; or EKS + KEDA |
| GPU / ML inference | EC2 Inf2 / G5 | Inf2 for Inferentia (cheaper inference); G5 for NVIDIA A10G; use SageMaker for managed MLOps |

## Data

| Need | Service | Config guidance |
|---|---|---|
| Relational (PostgreSQL) | Amazon RDS for PostgreSQL or Aurora PostgreSQL | RDS: db.t3.micro dev, db.r6g.large prod; Aurora: Serverless v2 for variable, provisioned for steady |
| Relational (MySQL) | Amazon RDS for MySQL or Aurora MySQL | Same tiering as PostgreSQL |
| Relational (SQL Server) | Amazon RDS for SQL Server | SE or EE edition; Multi-AZ for prod |
| Document / NoSQL | Amazon DynamoDB | On-demand (dev/variable); provisioned + Auto Scaling (steady prod); DynamoDB Accelerator (DAX) for microsecond cache |
| Analytical / data warehouse | Amazon Redshift | Serverless for variable query loads; RA3 provisioned for sustained heavy analytics |
| Search | Amazon OpenSearch Service | t3.small.search dev; m6g.large.search+ prod |
| Cache | Amazon ElastiCache | Redis (ElastiCache for Redis) preferred over Memcached for persistence/replication; cache.t3.micro dev, cache.r6g.large prod |
| Object storage | Amazon S3 | Standard default; Intelligent-Tiering for unknown access patterns; Glacier for archive |
| Time series | Amazon Timestream | Serverless, pay per query/write — good for IoT/telemetry |

## Messaging & Integration

| Need | Service | Config guidance |
|---|---|---|
| Message queue (reliable) | Amazon SQS | Standard (high throughput, at-least-once); FIFO (exactly-once, ordered, 3k msg/s) |
| Pub/Sub fan-out | Amazon SNS | Pairs with SQS for fan-out pattern (SNS → multiple SQS queues) |
| Event bus / routing | Amazon EventBridge | Default event bus for AWS service events; custom bus for app events; schema registry for event contracts |
| Event streaming | Amazon Kinesis Data Streams or MSK | Kinesis: managed, simpler ops; MSK (managed Kafka): better for existing Kafka ecosystem or very high throughput |
| API management | Amazon API Gateway | REST API (full features); HTTP API (lower cost, lower latency for simple proxy); WebSocket API for real-time |
| Workflow orchestration | AWS Step Functions | Standard (long-running, audit trail); Express (high-volume, short-duration) |

## Networking

| Need | Service | Notes |
|---|---|---|
| Load balancing (L7 / HTTP) | Application Load Balancer (ALB) | Path/host-based routing, WAF integration, gRPC support |
| Load balancing (L4 / TCP) | Network Load Balancer (NLB) | Ultra-low latency, static IPs, PrivateLink target |
| Global HTTP + CDN | Amazon CloudFront | WAF integration, Lambda@Edge / CloudFront Functions for edge compute |
| DNS | Amazon Route 53 | Public + private hosted zones; health-check-based failover; latency routing |
| Private connectivity to AWS services | VPC Interface Endpoints (PrivateLink) | Key services: S3, Secrets Manager, SSM, ECR, CloudWatch Logs |
| On-prem connectivity (low latency) | AWS Direct Connect | 1Gbps / 10Gbps dedicated; use with Transit Gateway for multi-VPC |
| On-prem connectivity (VPN) | AWS Site-to-Site VPN | Up to 1.25Gbps; dual tunnels by default; cheaper than Direct Connect |
| Multi-VPC connectivity | AWS Transit Gateway | Hub for VPC-to-VPC and on-prem; replaces VPC peering mesh at scale |
| Firewall / egress control | AWS Network Firewall | Stateful packet inspection, domain filtering; attach to VPC |
| DDoS | AWS Shield | Standard (free, automatic); Advanced (~£2,500/mo) for L7 DDoS with WAF |

## Identity & Security

| Need | Service | Notes |
|---|---|---|
| Identity provider | AWS IAM Identity Center (SSO) | Federate with Entra ID/Okta via SAML; assign permissions sets to accounts |
| Workload identity (EKS) | IRSA (IAM Roles for Service Accounts) | Pod-level IAM via OIDC federation; no long-lived credentials |
| Workload identity (EC2) | Instance Profile (IAM Role attached to EC2) | Metadata service v2 (IMDSv2) only — hop limit 1 |
| Secrets management | AWS Secrets Manager | Automatic rotation built-in; ~£0.35/secret/month + API calls |
| Config management | AWS Systems Manager Parameter Store | SecureString for non-rotated config; free tier for standard parameters |
| Threat detection | Amazon GuardDuty | Enable in all regions; ~£1–3/million events; low cost, high value |
| Posture management | AWS Security Hub | Aggregates GuardDuty, Inspector, Macie; CIS and AWS Foundational Security standard |
| Compliance monitoring | AWS Config | Rules for compliance checks; conformance packs for CIS/PCI |
| API audit | AWS CloudTrail | Enable in all regions with S3 + CloudWatch Logs; 90-day free event history |
| Container scanning | Amazon ECR + Inspector | Enable ECR enhanced scanning (Inspector v2); continuous CVE scanning |
| Account guardrails | AWS Organizations + SCPs | Deny root account usage, deny leaving org, require CloudTrail, deny public S3 |

## Observability

| Need | Service | Notes |
|---|---|---|
| Metrics | Amazon CloudWatch Metrics | Platform metrics free; custom metrics ~£0.28/metric/month |
| Logs | CloudWatch Logs | ~£0.50/GB ingested; use log groups with retention policies (don't leave at Never Expire) |
| Tracing | AWS X-Ray | Automatic for Lambda/API Gateway; SDK for custom instrumentation |
| Dashboards | CloudWatch Dashboards or Grafana Cloud | Grafana Cloud with CloudWatch datasource gives better dashboards |
| Alerting | CloudWatch Alarms + SNS | Composite alarms for multi-condition alerting |

---

## Service Selection Decision Rules

**Aurora vs RDS:**
- Aurora PostgreSQL Serverless v2: variable/unpredictable workloads, dev/staging, cost-sensitive
- Aurora PostgreSQL Provisioned: high-throughput prod, read replicas needed, Global Database for multi-region
- RDS PostgreSQL: simpler ops, lower cost for small steady workloads, when Aurora features aren't needed

**SQS vs Kinesis vs MSK:**
- SQS: job queues, task distribution, decoupling services — simple, cheap, managed
- Kinesis: ordered event streams, replay capability, multiple consumers of same stream — more complex, more powerful
- MSK: Kafka-compatible ecosystem, very high throughput, existing Kafka producers/consumers

**Step Functions Standard vs Express:**
- Standard: long-running (up to 1 year), exactly-once, full audit history — use for business workflows
- Express: high-volume (100k/s), at-least-once, 5-minute max, cheaper — use for event processing pipelines
