# CNCF Tool Selection Guide

Use this file when a tool choice needs to be made. For each category, the right answer depends on: managed provider, existing tooling, team experience, air-gap requirements, and operational overhead tolerance.

---

## CNI (Container Network Interface)

| Tool | Managed provider fit | Highlights | Avoid when |
|---|---|---|---|
| **Azure CNI / Azure CNI Overlay** | AKS native | Deep Azure integration; Overlay avoids IP exhaustion | Non-Azure |
| **AWS VPC CNI** | EKS native | Pods get VPC IPs; prefix delegation for scale | Non-AWS; needs Calico/Cilium for NetworkPolicy |
| **GKE Dataplane V2 (Cilium)** | GKE native | eBPF-based; built-in NetworkPolicy and observability | Non-GKE |
| **Cilium** | Any | eBPF performance; L7 NetworkPolicy; Hubble for network observability; replaces kube-proxy | Small teams unfamiliar with eBPF |
| **Calico** | Any | Mature; good NetworkPolicy; BGP routing option | Prefer Cilium for new clusters where eBPF is viable |
| **Flannel** | Self-hosted / simple setups | Minimal, easy to operate | Any workload needing NetworkPolicy |
| **Weave Net** | Legacy | Avoid for new clusters | — |

**Decision guide:**
- Managed cluster → use the provider's native CNI unless you have specific reasons not to
- Self-hosted, need advanced NetworkPolicy or eBPF observability → Cilium
- Self-hosted, simple setup → Calico
- Need BGP routing for on-prem integration → Calico

---

## Ingress / Gateway

| Tool | Highlights | Avoid when |
|---|---|---|
| **Envoy Gateway** | Gateway API native; modern; Envoy-based; rich traffic management | Team needs simple config fast |
| **NGINX Ingress Controller** | Widely understood; simple config; large community | Need advanced traffic management, L7 routing features |
| **Traefik** | Dynamic config; good for dynamic environments; built-in Let's Encrypt | Large enterprise clusters; prefer declarative-only |
| **HAProxy Ingress** | High performance L4/L7; good for TCP workloads | — |
| **AWS ALB Ingress / Load Balancer Controller** | EKS native; integrates with AWS ALB/NLB | Non-AWS |
| **Azure AGIC** | AKS native; integrates with Azure Application Gateway + WAF | Non-Azure; complexity vs benefit for simple setups |
| **Istio Gateway** | Use if Istio service mesh already present | Don't adopt Istio just for ingress |

**Decision guide:**
- New cluster, no existing investment → Envoy Gateway (Gateway API) or NGINX (simpler)
- EKS → AWS Load Balancer Controller for cloud-native integration
- AKS with WAF requirement → AGIC
- Already running Istio → use Istio Gateway
- Gateway API is the future standard; prefer it for new implementations

---

## Service Mesh

Service mesh adds significant operational complexity. Only adopt if you have a clear need.

**Genuine reasons to adopt a service mesh:**
- mTLS between services is a hard compliance requirement
- Fine-grained traffic management (circuit breaking, retries, canary) at mesh level
- Observability of east-west traffic without code changes

**Don't adopt a service mesh because:** it sounds good, or for basic ingress, or if your team hasn't operated one before.

| Tool | Highlights | Operational overhead | Avoid when |
|---|---|---|---|
| **Istio** | Most feature-rich; ambient mode (sidecar-less) now stable | High | Small teams; no dedicated platform engineer |
| **Linkerd** | Lighter than Istio; easier to operate; Rust-based proxies (low overhead) | Medium | Need Istio-specific features |
| **Cilium Service Mesh** | eBPF-based; no sidecars; if Cilium CNI already present, low incremental cost | Low (if Cilium already used) | Non-Cilium clusters |
| **Consul Connect** | Good for hybrid K8s + VM environments | Medium-High | Pure K8s environments |

**Decision guide:**
- Already on Cilium CNI → Cilium Service Mesh is lowest overhead addition
- Need full service mesh features, have a dedicated platform team → Istio (ambient mode preferred)
- Want service mesh with lower complexity than Istio → Linkerd
- Hybrid K8s + VM → Consul Connect

---

## GitOps Controllers

| Tool | Highlights | Avoid when |
|---|---|---|
| **Argo CD** | Strong UI; ApplicationSet for multi-cluster/tenant; mature RBAC; large community | Want minimal UI / pure GitOps |
| **Flux** | Lighter; more GitOps-native; OCI registry support; good Helm/Kustomize support | Team wants UI visibility |
| **Fleet (Rancher)** | Multi-cluster at scale; good for large fleet management | Not running Rancher/SUSE ecosystem |

**Decision guide:**
- Default for most teams → Argo CD (visibility, RBAC, ApplicationSets)
- Pure GitOps purists, minimal tooling preference → Flux
- Managing 10s–100s of clusters → Fleet or Argo CD with ApplicationSets

---

## Secrets Management

**The pattern is consistent regardless of backend:** External Secrets Operator (ESO) or Secrets Store CSI Driver as the Kubernetes-side bridge; the choice of backend depends on existing infrastructure.

| Backend | Use when |
|---|---|
| **Azure Key Vault** | Azure / AKS; use with ESO + Workload Identity or CSI driver |
| **AWS Secrets Manager** | AWS / EKS; use with ESO + IRSA |
| **GCP Secret Manager** | GCP / GKE; use with ESO + Workload Identity |
| **HashiCorp Vault** | Multi-cloud, self-hosted, or existing Vault investment; ESO Vault provider |
| **Infisical** | Open-source Vault alternative; self-hosted option |
| **Kubernetes Secrets (plain)** | Only for non-sensitive config; never for credentials |

**ESO vs Secrets Store CSI Driver:**
- **ESO** (preferred): creates K8s Secrets from external store; works with all env var / volume patterns; easier to manage
- **CSI Driver**: mounts secrets as volumes directly; better for large secrets or frequent rotation without pod restart; more complex

---

## Policy / Admission Control

| Tool | Highlights | Avoid when |
|---|---|---|
| **Kyverno** | Policy as K8s resources (no Rego); validate, mutate, generate; easier onboarding | Need complex policy logic across large orgs |
| **OPA Gatekeeper** | Policies in Rego; powerful constraint templates; widely adopted in enterprise | Team doesn't know Rego; small-medium clusters |
| **Kubewarden** | Policies as WebAssembly; write in Rust/Go/Python; newer | Immature ecosystem vs Kyverno/Gatekeeper |
| **Pod Security Standards (built-in)** | No extra tooling; enforce/audit/warn via namespace labels | Insufficient alone for complex policy requirements |
| **Managed provider policies** | Azure Policy for AKS, AWS Config + Security Hub for EKS | Locked to single provider |

**Decision guide:**
- New to policy enforcement, small-medium cluster → Kyverno (easier onboarding, no Rego)
- Large org, dedicated platform team, complex policy requirements → OPA Gatekeeper
- All clusters → enable Pod Security Standards as a baseline regardless of policy engine choice
- Managed clusters with compliance requirements → layer provider-native policy (Azure Policy, AWS Config) on top of in-cluster engine

---

## Observability

### Collectors / Agents

| Tool | Highlights | Avoid when |
|---|---|---|
| **OpenTelemetry Collector** | Vendor-neutral; OTLP native; can replace multiple agents; CNCF graduated | Need agent-specific features not yet in OTEL |
| **Grafana Alloy** | OTel-compatible; good Grafana stack integration; replaces Grafana Agent | Not using Grafana stack |
| **Fluent Bit** | Lightweight log forwarder; low resource usage; widely deployed | Need full processing pipeline (use Fluentd then) |
| **Fluentd** | More processing capability than Fluent Bit; heavier | Resource-constrained nodes |
| **Prometheus (scrape model)** | Pull-based metrics; de-facto standard; vast exporter ecosystem | High-cardinality or push-only environments |
| **Vector** | High-performance; Rust-based; logs, metrics, traces | Newer; smaller community than Fluent Bit |

**Decision guide:**
- New observability stack → OpenTelemetry Collector as the unified agent (logs, metrics, traces)
- Grafana-centric stack → Alloy (OTel-compatible + Grafana-native features)
- Logs only, resource-constrained → Fluent Bit

### Metrics Backends

| Tool | Highlights | Avoid when |
|---|---|---|
| **Prometheus** | De-facto standard; pull model; vast ecosystem; local storage only | Long-term retention at scale (use Thanos/Mimir) |
| **Thanos** | Long-term Prometheus storage; multi-cluster query; object storage backend | Small single-cluster setups |
| **Mimir (Grafana)** | Horizontally scalable Prometheus; multi-tenant; managed via Grafana Cloud | Self-hosting at small scale (overhead not worth it) |
| **Victoria Metrics** | High-performance Prometheus-compatible; efficient storage | Prefer Grafana ecosystem |
| **Managed (AWS CloudWatch, Azure Monitor, GCP Cloud Monitoring)** | Zero ops; native provider integration | Need cross-provider unified view; prefer open standards |

**Decision guide:**
- Single cluster, short retention → Prometheus
- Multi-cluster or long retention, self-hosted → Thanos or Victoria Metrics
- Want managed, Grafana ecosystem → Grafana Cloud Mimir
- Already on managed provider and don't need cross-cloud → native provider metrics

### Logging Backends

| Tool | Highlights | Avoid when |
|---|---|---|
| **Loki (Grafana)** | Label-based; low cost; good K8s integration; pairs with Grafana | Need full-text search at petabyte scale |
| **Elasticsearch / OpenSearch** | Powerful full-text search; high operational overhead | Simple structured log queries (Loki is sufficient) |
| **OpenSearch** | Open-source Elasticsearch fork; AWS manages it on OpenSearch Service | — |
| **Managed (CloudWatch Logs, Azure Log Analytics, GCP Cloud Logging)** | Zero ops; native integration | Cross-provider; open-source preference |
| **Splunk** | Enterprise; compliance-friendly; expensive | Cost-sensitive environments |

**Decision guide:**
- New self-hosted stack → Loki (low ops overhead, pairs with Grafana/Prometheus)
- Need powerful full-text search or existing investment → OpenSearch/Elasticsearch
- Managed, provider-native → CloudWatch / Log Analytics / Cloud Logging
- Air-gapped or compliance-driven → OpenSearch self-hosted

### Tracing Backends

| Tool | Highlights | Avoid when |
|---|---|---|
| **Tempo (Grafana)** | OTLP native; scales well; integrates with Loki/Prometheus in Grafana | Need search by tag/attribute (Tempo's query model is trace-ID first) |
| **Jaeger** | CNCF graduated; widely understood; good UI for trace exploration | Large-scale retention (use object storage backend) |
| **Zipkin** | Simple; widely supported; older | Prefer OTLP-native tools for new deployments |
| **Managed (AWS X-Ray, Azure App Insights, GCP Cloud Trace)** | Zero ops; native instrumentation | Cross-provider; open-source preference |

**Decision guide:**
- Grafana-centric stack → Tempo
- Standalone tracing, good UI → Jaeger
- Managed, provider-native → X-Ray / App Insights / Cloud Trace

### Observability Stack Combinations

| Deployment model | Recommended stack | Notes |
|---|---|---|
| **Managed, Grafana ecosystem** | Grafana Cloud (Mimir + Loki + Tempo) + Alloy/OTel Collector | Lowest ops overhead; free tier for small clusters |
| **Self-hosted, Grafana ecosystem** | kube-prometheus-stack + Loki + Tempo + OTel Collector | More ops overhead; full control; air-gap friendly |
| **Self-hosted, CNCF-native** | Prometheus + Thanos + Jaeger + Fluent Bit + OpenSearch | All CNCF graduated projects; no vendor affinity |
| **AWS-native** | CloudWatch Container Insights + X-Ray + CloudWatch Logs | Zero ops; provider lock-in |
| **Azure-native** | Azure Monitor + Container Insights + Application Insights | Zero ops; provider lock-in |
| **GCP-native** | Cloud Monitoring + Cloud Trace + Cloud Logging | Zero ops; provider lock-in |
| **Air-gapped / regulated** | Victoria Metrics + OpenSearch + Jaeger + Fluent Bit | All self-hostable; no external dependencies |

---

## Storage (CSI Drivers)

| Provider | Native CSI driver | Notes |
|---|---|---|
| **AKS** | Azure Disk CSI, Azure Files CSI | Use Azure Disk for RWO; Azure Files for RWX |
| **EKS** | EBS CSI, EFS CSI | EBS for RWO; EFS for RWX |
| **GKE** | GCE Persistent Disk CSI, Filestore CSI | PD for RWO; Filestore for RWX |
| **Self-hosted** | Rook/Ceph, Longhorn, OpenEBS | Rook/Ceph for distributed storage; Longhorn for simpler setups |
| **Multi-cloud / portable** | Rook/Ceph | Overkill for most managed cluster setups |

**Self-hosted storage decision:**
- Simple, small cluster → Longhorn (easy to operate, good UI)
- Production, distributed, performance matters → Rook/Ceph (more complex, more capable)
- Stateful workloads on managed K8s → always prefer cloud-native CSI over self-hosted storage solutions
