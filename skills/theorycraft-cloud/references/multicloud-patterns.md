# Multi-Cloud Patterns Reference

## Is Multi-Cloud Actually Warranted?

Be honest with the user. Multi-cloud is often aspirational, rarely necessary, and almost always more expensive to operate than single-cloud. Ask:

**Genuine reasons to go multi-cloud:**
- Regulatory requirement to avoid single-provider dependency (rare, usually financial services / critical national infrastructure)
- Specific best-of-breed service on a different provider (e.g. BigQuery on GCP for analytics + Azure for operational workloads)
- Existing M&A situation where two estates need to coexist
- Negotiation leverage — but this usually means dual-vendor contracts, not running workloads in both
- Disaster recovery on a different provider (active-passive only for most; active-active is extremely hard)

**Not good enough reasons:**
- "We don't want to be locked in" — abstraction layers create their own lock-in (to Kubernetes, Terraform, your abstraction code)
- "What if the provider goes down?" — major cloud providers have better uptime than most multi-cloud architectures
- "We might switch providers one day" — this almost never happens, and the cost of premature abstraction is real

**Verdict for most SME/mid-market SaaS:** single cloud, well-architected. Multi-region within that provider if HA is genuinely required.

---

## Abstraction Strategies (if multi-cloud is warranted)

### Infrastructure as Code
- **Terraform / OpenTofu**: provider-agnostic resource definition. Best option for multi-cloud IaC. Use modules to abstract provider-specific resources.
- **Pulumi**: same idea, code-first. Better for teams already writing Go/TypeScript/Python.
- **Don't**: use provider-native IaC (CloudFormation, ARM/Bicep) if multi-cloud is a goal — you'll rewrite everything.

### Container & Runtime Portability
- **Kubernetes**: the only widely-adopted runtime abstraction. Stick to core K8s APIs, avoid cloud-specific annotations/operators where possible.
- **Caution**: managed K8s services (AKS, EKS, GKE) diverge in: CNI, ingress controllers, load balancer annotations, managed identity integration. Your K8s manifests will still need provider-specific tuning.
- **Service mesh (Istio/Linkerd)**: useful for mTLS and traffic management in multi-cluster scenarios

### Data Portability
- The hardest part. Managed databases (Aurora, Azure Flexible Server, Cloud SQL) are not portable.
- Options: use open-source engines (PostgreSQL, MySQL, Redis) so you can run anywhere — but you lose managed service benefits.
- Object storage: S3-compatible APIs (Azure Blob via S3 compatibility layer, MinIO) help, but test compatibility before committing.

### Networking
- **Cloud interconnect / ExpressRoute / Direct Connect**: physical connectivity between clouds — expensive, complex, latency is still real
- **VPN tunnels**: cheaper, higher latency — fine for low-throughput control plane traffic
- **Avoid cross-cloud data gravity**: keep compute close to data. Cross-cloud egress is double the cost and latency.

---

## Provider Equivalents Quick Reference

| Capability | Azure | AWS | GCP |
|-----------|-------|-----|-----|
| Managed K8s | AKS | EKS | GKE |
| Serverless functions | Azure Functions | Lambda | Cloud Functions / Cloud Run |
| Managed PostgreSQL | Flexible Server | RDS / Aurora | Cloud SQL |
| Object storage | Blob Storage | S3 | Cloud Storage |
| Message queue | Service Bus | SQS/SNS | Pub/Sub |
| Event streaming | Event Hubs | Kinesis / MSK | Pub/Sub / Dataflow |
| Secrets | Key Vault | Secrets Manager | Secret Manager |
| Identity federation | Entra ID / Workload Identity | IAM + IRSA | Workload Identity |
| Container registry | ACR | ECR | Artifact Registry |
| CDN | Azure Front Door | CloudFront | Cloud CDN |
| Observability | Azure Monitor + Log Analytics | CloudWatch + X-Ray | Cloud Monitoring + Trace |
| IaC native | Bicep / ARM | CloudFormation | Deployment Manager |
| DNS | Azure DNS | Route 53 | Cloud DNS |
| WAF | Azure WAF (Front Door / App GW) | WAF (CloudFront / ALB) | Cloud Armor |

---

## Multi-Cloud DR Pattern (Active-Passive)

If the use case is DR rather than active-active multi-cloud:

1. **Primary cloud**: full production stack
2. **Secondary cloud**: infrastructure as code, deployed but idle (cold standby) or running minimum viable (warm standby)
3. **Data replication**: database streaming replication or periodic snapshot export/import to secondary
4. **DNS failover**: health-check-based failover in Route 53 / Azure Traffic Manager / Cloud DNS
5. **RTO/RPO tradeoffs**: cold standby = lower cost, higher RTO (~hours); warm standby = higher cost, lower RTO (~minutes); active-active = highest cost, near-zero RTO but extreme operational complexity

For most organisations: single-cloud + multi-region active-passive is the right answer for HA/DR, not true multi-cloud.
