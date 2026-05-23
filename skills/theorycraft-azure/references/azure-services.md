# Azure Service Selection Guide

## Compute

| Need | Service | Tier guidance |
|---|---|---|
| Containerised workloads, K8s | AKS | System pool: D4s_v5; User pools: size to workload; Spot pools for batch |
| Simple containers, no K8s | Azure Container Apps | Consumption (scale-to-zero) or Dedicated (predictable workloads) |
| Serverless functions | Azure Functions | Consumption (true serverless) or Premium EP1+ (VNet integration, no cold start) |
| Web apps / APIs | Azure App Service | B-series dev/test; P-series prod; use deployment slots for blue/green |
| Windows IaaS | Azure Virtual Machines | B-series burstable dev/test; D-series general prod; E-series memory-intensive |
| GPU / HPC | NC/ND/NV series VMs | NC for inference, ND for training, NV for visualisation |
| Batch processing | Azure Batch | Pool-based, Spot VMs for cost; or use AKS + KEDA for K8s-native batch |

## Data

| Need | Service | Tier guidance |
|---|---|---|
| Relational (PostgreSQL) | Azure Database for PostgreSQL Flexible Server | Burstable B2ms dev; General Purpose D4s_v3+ prod; Business Critical for HA |
| Relational (MySQL) | Azure Database for MySQL Flexible Server | Same tiering as PostgreSQL |
| Relational (SQL Server) | Azure SQL Database | Serverless (auto-pause) dev; General Purpose vCore prod; Business Critical for HA+replicas |
| Document / NoSQL | Azure Cosmos DB | Serverless for dev/variable; Provisioned RU/s for prod; Free tier for small workloads |
| Analytical | Azure Synapse Analytics / Fabric | Synapse for existing Azure estate; Fabric for new greenfield analytics |
| Search | Azure AI Search | Basic dev; Standard S1+ prod; Storage Optimised for large indices |
| Cache | Azure Cache for Redis | Basic dev (no SLA); Standard C1+ prod; Premium for persistence/clustering |
| Object storage | Azure Blob Storage | Hot tier default; Cool for infrequent access; Archive for long-term retention |
| Time series / IoT | Azure Data Explorer (ADX) | Dev cluster (1 node) for testing; Standard prod clusters; use for high-volume telemetry |

## Messaging & Integration

| Need | Service | Tier guidance |
|---|---|---|
| Message queue (reliable delivery) | Azure Service Bus | Standard for basic queuing; Premium for VNet integration, sessions, large messages |
| Event streaming (high throughput) | Azure Event Hubs | Basic dev; Standard prod; Premium/Dedicated for compliance or extreme throughput |
| Event routing / pub-sub | Azure Event Grid | Consumption-based; no tiers to choose; use for event-driven serverless patterns |
| API management | Azure API Management | Developer (no SLA, dev only); Basic/Standard prod; Premium for multi-region |
| Workflow orchestration | Azure Logic Apps | Consumption (serverless); Standard (VNet, stateful, higher throughput) |

## Networking

| Need | Service | Notes |
|---|---|---|
| Load balancing (L4) | Azure Load Balancer | Standard tier (Basic deprecated); zone-redundant by default |
| Load balancing (L7 / HTTP) | Azure Application Gateway | v2 SKU; WAF_v2 if WAF needed; integrates with AKS as AGIC |
| Global HTTP routing + WAF | Azure Front Door | Standard (CDN + routing); Premium (WAF + Private Link origins) |
| DNS | Azure DNS | Public and private zones; use Private DNS zones for Private Endpoint resolution |
| Private connectivity to PaaS | Private Endpoints | Required for: Key Vault, Storage, PostgreSQL, Service Bus in production |
| On-prem connectivity (low latency) | ExpressRoute | Global Reach for site-to-site via Microsoft backbone |
| On-prem connectivity (VPN) | Azure VPN Gateway | VpnGw1 basic; VpnGw2+ for higher throughput; zone-redundant SKUs for HA |
| Firewall / egress control | Azure Firewall | Standard; Premium for TLS inspection and IDPS |
| DDoS protection | Azure DDoS Protection | Network protection plan (~£2,500/mo) — only for public-facing high-value workloads |

## Identity & Security

| Need | Service | Notes |
|---|---|---|
| Identity provider | Entra ID (Azure AD) | Free tier for basic; P1 for Conditional Access; P2 for PIM and Identity Protection |
| Workload identity (AKS) | Workload Identity (UAMI + federation) | Replaces pod-managed identity; no secret rotation needed |
| Managed identity (VMs/App Service) | System-assigned or User-assigned MI | User-assigned preferred for shared identity across multiple resources |
| Secrets management | Azure Key Vault | Standard tier (software-protected keys); Premium (HSM-protected) for compliance |
| Cloud security posture | Microsoft Defender for Cloud | CSPM free; paid Defender plans per resource type (~£10-15/node/mo for containers) |
| SIEM / SOAR | Microsoft Sentinel | Log Analytics workspace backend; cost based on data ingestion volume |
| Policy enforcement | Azure Policy | Built-in initiatives: CIS, ISO 27001, PCI-DSS; custom policies via JSON/Bicep |

## Observability

| Need | Service | Notes |
|---|---|---|
| Metrics + dashboards | Azure Monitor + Metrics Explorer | Built-in; free for platform metrics |
| Log aggregation | Log Analytics Workspace | Pay-per-GB ingestion; commitment tiers at 100GB+/day |
| Application tracing | Application Insights | Auto-instrumentation for .NET, Java, Node.js; connects to Log Analytics |
| Alerting | Azure Monitor Alerts | Metric, log, and activity log alert types; action groups for notifications |
| External observability stack | Grafana Cloud | Azure Monitor + Log Analytics as datasources; better dashboards than Azure Portal |

---

## Service Tier Decision Rules

**When to use Premium/Business Critical tiers:**
- SLA requirement > 99.9%
- VNet integration required (Service Bus Premium, Functions Premium)
- Zone redundancy needed (PostgreSQL Business Critical, SQL Business Critical)
- Dedicated capacity required for compliance (Event Hubs Premium/Dedicated)

**When Burstable / Consumption tiers are fine:**
- Development and staging environments
- Workloads with genuinely low or variable traffic
- Internal tooling without strict SLAs
- Early-stage production (upgrade when you have real load data)

**Never use Basic tiers in production:**
- Azure Load Balancer Basic — deprecated, no SLA, no zone support
- Azure Cache for Redis Basic — no SLA, single node
- API Management Developer — no SLA
