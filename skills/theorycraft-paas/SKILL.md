---
name: theorycraft-paas
description: PaaS (Platform as a Service) architecture extension. Produces deep PaaS design recommendations, managed service selection guidance, and architecture diagrams (Mermaid for topology, SVG for detailed component diagrams). Extends theorycraft-cloud — run that skill's analysis first, then this skill adds PaaS-specific depth: managed database selection (RDS, Azure Flexible Server, Cloud SQL), managed application platforms (App Service, Elastic Beanstalk, App Engine), managed messaging (Service Bus, SQS, Pub/Sub), API management, managed caching, and the key trade-offs between PaaS control vs operational simplicity. Use this skill whenever a user asks about managed cloud services, PaaS architecture, App Service, Elastic Beanstalk, App Engine, managed databases, managed queues, API gateway design, or wants to understand the right level of managed service abstraction for their workload. Trigger for any question about using managed services over self-managed alternatives.
---

# TheoryCraft PaaS

A PaaS architecture extension. Assumes theorycraft-cloud has produced or will produce the high-level analysis. This skill adds depth on managed service selection, the control-vs-simplicity trade-off, and PaaS-specific design patterns.

---

## Behaviour

### Step 1 — Confirm or run theorycraft-cloud analysis
Build on theorycraft-cloud analysis if available. If not, proceed — self-sufficient.

### Step 2 — PaaS Abstraction Level Assessment
Before recommending services, assess the right abstraction level for this workload:

| Level | What you manage | What provider manages | Examples |
|---|---|---|---|
| **IaaS** | OS, runtime, app, data | Hardware, virtualisation | VMs |
| **CaaS** | App, data | OS, runtime, container orchestration | AKS, EKS, GKE |
| **PaaS** | App, data | OS, runtime, scaling, patching | App Service, Elastic Beanstalk, App Engine |
| **FaaS** | Function code | Everything else | Lambda, Azure Functions, Cloud Functions |
| **SaaS / DBaaS** | Data and config | Everything | Azure SQL, RDS, Cosmos DB |

The right level depends on: team size, operational maturity, customisation needs, and compliance requirements. Smaller teams should default to higher abstraction. Be explicit about the trade-off.

### Step 3 — PaaS Service Mapping
Map each component to the most appropriate managed service. Be specific about tier and configuration — not "a managed platform" but "Azure App Service Premium P2v3 with deployment slots and VNet integration."

### Step 4 — Produce Diagrams
Always produce at least one diagram.

**Mermaid** — for service topology and request flows
**SVG** — for component detail showing managed service boundaries, VNet integration points, and data flows

---

## Output Structure

### ☁️ PaaS Service Selection

For each component, justify the abstraction level choice:

| Component | Service | Tier | Why PaaS over IaaS/containers here |
|---|---|---|---|
| App runtime | ... | ... | ... |
| Database | ... | ... | ... |
| Cache | ... | ... | ... |
| Queue / messaging | ... | ... | ... |
| API layer | ... | ... | ... |
| Search | ... | ... | ... |

### 🔒 Managed Service Security

PaaS has different security considerations to IaaS:
- **VNet integration:** most PaaS services can be injected into a VNet or accessed via Private Endpoint — always configure this for prod
- **Managed Identity:** no connection strings with passwords; use managed identity / workload identity for service-to-service auth
- **Private Endpoints:** for databases, queues, key vaults — no public endpoint exposure in prod
- **TLS enforcement:** enforce TLS 1.2+ minimum; disable older protocols on managed services
- **Firewall rules:** restrict PaaS service access to known VNet CIDRs; deny public internet where not needed

### 🔄 Deployment and Scaling

- **Deployment slots** (App Service) / **Blue/green** (Elastic Beanstalk) / **Traffic splitting** (App Engine, Cloud Run): zero-downtime deployments
- **Auto-scaling:** managed platform scaling rules vs manual; always configure both scale-out AND scale-in to avoid stranded capacity
- **Config management:** environment variables via Key Vault references (Azure) / Secrets Manager (AWS) / Secret Manager (GCP) — not hardcoded in app settings

### 📊 Observability for PaaS

- **Application Insights** (Azure) / **X-Ray + CloudWatch** (AWS) / **Cloud Trace + Cloud Monitoring** (GCP): auto-instrumentation available for most PaaS runtimes
- **Platform metrics:** managed services emit health metrics automatically — configure alerts on: error rate, response time, queue depth, DB connection pool, cache hit rate
- **Dependency mapping:** use distributed tracing to understand PaaS service-to-service call patterns and identify latency hotspots

### 💰 PaaS FinOps

PaaS billing is more complex than IaaS — address the specific model for each service:
- **App platforms:** hourly per instance (App Service Plan, Beanstalk environment); contrast with scale-to-zero options (Container Apps, App Service Consumption, App Engine automatic scaling)
- **Managed databases:** hourly per vCore/DTU + storage; reserved capacity (1-year ~35–40% saving); right-size instance before reserving
- **Messaging:** per message or per operation; volume pricing tiers
- **Concrete estimates** in GBP at stated scale: summary total + per-service breakdown

### 🆚 PaaS vs Containers vs Serverless Decision

Always include a brief recommendation on whether PaaS is the right level or whether the user should consider containers or serverless instead:

**Stay with PaaS when:**
- Small team, low operational overhead budget
- Standard runtimes (.NET, Java, Node.js, Python) without exotic dependencies
- Rapid iteration matters more than infrastructure control
- No need for custom networking configurations or sidecar patterns

**Move to containers (K8s) when:**
- Multiple services with complex inter-service networking
- Custom runtimes, sidecar patterns, or service mesh needed
- Multi-tenant isolation at namespace level
- Team has or is building platform engineering capability

**Move to serverless when:**
- Event-driven, variable/bursty workloads
- Scale-to-zero cost model preferred
- Stateless functions without complex startup requirements

### 🚫 Anti-Patterns

- **PaaS sprawl:** dozens of App Service Plans each running one small app — consolidate onto shared plans for cost efficiency
- **Ignoring VNet integration:** PaaS services with public endpoints in prod — every managed service should be private-endpoint or VNet-injected
- **Connection strings in app config:** use Managed Identity + Key Vault references; never plaintext credentials in environment variables or app settings UI
- **Always-on for dev/staging:** managed databases and app platforms running at prod tier 24/7 for non-prod; use Basic/Burstable tiers and auto-pause for dev

### 📐 Architecture Diagrams

Always produce:
1. **Service topology** (Mermaid) — all managed services, their relationships, request flows
2. **Component detail** (SVG) — VNet integration, Private Endpoints, managed service boundaries, data flow directions

---

## Reference Files

- `references/app-platforms.md` — App Service vs Elastic Beanstalk vs App Engine vs Container Apps; deployment slot patterns; scaling config
- `references/managed-databases.md` — Azure Flexible Server vs RDS vs Cloud SQL; tier guidance; connection pooling; read replicas; private endpoint patterns
- `references/managed-messaging.md` — Service Bus vs SQS vs Pub/Sub vs Cloud Tasks; tier selection; DLQ configuration; VNet integration
- `references/paas-finops.md` — reserved capacity for managed databases, App Service Plan consolidation, dev/staging cost reduction, GBP benchmarks
