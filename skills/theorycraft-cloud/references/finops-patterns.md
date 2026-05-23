# FinOps & Cost Patterns Reference

## FinOps Maturity Model (Quick Reference)

| Stage | What it looks like | Key actions |
|-------|-------------------|-------------|
| **Crawl** | No cost visibility, reactive to bills | Enable cost tags, set budgets + alerts, assign ownership |
| **Walk** | Teams see their costs, some optimisation | Unit economics, right-sizing, reservation coverage >50% |
| **Run** | Cost is a design constraint, continuous optimisation | Automated anomaly detection, showback/chargeback, FinOps in CI/CD |

Most SME/mid-market orgs are at Crawl–Walk. Don't recommend Run-stage tooling to a Crawl-stage org.

---

## Azure Cost Levers

### Compute
- **Reserved Instances (RIs)**: 1-year ~40% savings, 3-year ~60% vs on-demand for predictable workloads. Commit at the subscription or shared scope.
- **Savings Plans**: Azure equivalent — more flexible than RIs, applies across compute families
- **Spot VMs / Spot node pools (AKS)**: 60-80% cheaper; tolerate eviction. Use for batch, CI runners, non-critical background jobs. Never for stateful workloads without checkpointing.
- **Dev/Test pricing**: ~50% off many VM SKUs for non-production via Dev/Test subscriptions

### Kubernetes (AKS) cost optimisation
- Right-size requests/limits — over-provisioned requests waste node capacity
- **KEDA** for scale-to-zero on event-driven workloads (message queues, NATS subjects)
- **Cluster autoscaler** with aggressive scale-down (scale-down-delay-after-add, scale-down-unneeded-time)
- Use **Azure CNI Overlay** to reduce IP wastage and associated subnet sizing overhead
- Stop/start AKS clusters in non-prod outside business hours (saves compute, not PVCs)
- Consider **Azure Container Apps** for simpler workloads where K8s overhead isn't justified

### Storage
- **Storage tiering**: Hot → Cool → Cold → Archive. Automate lifecycle policies for blob storage.
- **Managed disk SKUs**: Premium SSD v2 > Premium SSD > Standard SSD > Standard HDD. Right-size IOPS.
- **PostgreSQL Flexible Server**: size storage carefully — Azure charges for provisioned storage, not used. Burstable tier for dev/test.

### Networking (biggest surprise bills)
- **Egress**: ~£0.07/GB leaving Azure (first 100GB free/month). Minimise cross-region and internet egress.
- **NAT Gateway**: ~£0.032/hour + £0.004/GB processed. Consider whether needed vs public IP on nodes.
- **Private Endpoints**: small per-hour cost but saves egress costs for high-volume PaaS access
- **VNet Peering**: charged per GB both directions across peering. Centralise shared services to reduce peering traffic.

---

## AWS Cost Levers

### Compute
- **Reserved Instances / Savings Plans**: 1-year ~30-40%, 3-year ~50-60% for EC2/Fargate/Lambda
- **Spot Instances**: 70-90% cheaper. Use Spot Interruption Handler in EKS. Karpenter preferred over Cluster Autoscaler for Spot-heavy AKS/EKS.
- **Graviton (ARM) instances**: 10-20% better price/performance for most workloads on compatible runtimes

### Serverless (Lambda)
- **ARM/Graviton2 Lambda**: ~20% cheaper, ~19% better performance
- **Memory right-sizing**: use Lambda Power Tuning tool before committing to memory config
- **Provisioned concurrency**: costs ~65% of on-demand but eliminates cold starts — only use where latency matters

### Data Transfer
- Egress to internet: ~$0.09/GB. Cross-AZ: ~$0.02/GB each way — keep hot-path services in same AZ where possible.
- **S3 Transfer Acceleration**, **CloudFront** to reduce origin egress costs at scale

---

## GCP Cost Levers

- **Committed Use Discounts (CUDs)**: 1-year ~37%, 3-year ~55% for Compute Engine
- **Sustained Use Discounts**: automatic ~30% for instances running >25% of month — no commitment needed
- **Preemptible / Spot VMs**: 60-91% cheaper
- **GKE Autopilot**: billing per pod resource request, not node — can be cheaper than Standard mode for variable workloads; always cheaper than over-provisioned Standard clusters
- **BigQuery**: on-demand billing per TB scanned; use partitioning + clustering to reduce scan volume. Flat-rate slots for predictable query volumes.

---

## Tagging Strategy (Required for FinOps)

Minimum tag set for cost allocation:
```
environment:   prod | staging | dev | sandbox
team:          platform | product | data | security
service:       crucible | blacksmith | ca | ddi-service | etc
cost-centre:   [business unit or project code]
managed-by:    terraform | manual | helm
```

Enforce via Azure Policy (deny untagged resources) or AWS Config Rules. Without tagging, you can't do showback/chargeback or identify waste.

---

## Cost Anomaly Detection

- **Azure**: Cost Management + Budgets with email/webhook alerts at 80%/100% of budget; Anomaly Alerts in Cost Management
- **AWS**: Cost Anomaly Detection (ML-based, free to enable)
- **GCP**: Budgets with Pub/Sub notifications for programmatic response

Set alerts before you need them. A runaway workload or misconfigured autoscaler can generate thousands in hours.

---

## FinOps Anti-Patterns

1. **No tagging** — can't attribute costs, can't identify waste
2. **Oversized reserved capacity** — committing too much too early before workload patterns are known
3. **Forgotten resources** — unattached managed disks, idle load balancers, unused public IPs, orphaned snapshots. Run monthly cleanup.
4. **Cross-region data transfer** — often accidental; log and alert on unexpected egress patterns
5. **Development in production sizing** — dev environments at prod tier. Use burstable/smaller SKUs and shut down out of hours.
6. **NAT Gateway for everything** — often added by default without considering whether internet egress is actually needed
