# Cluster Design Reference

## Managed K8s Provider Trade-offs

| | AKS | EKS | GKE |
|---|---|---|---|
| **Control plane cost** | Free | ~$73/mo | Free (Standard), ~$73/mo (Enterprise) |
| **Windows nodes** | ✅ First-class | ✅ Supported | ⚠️ Limited |
| **Autopilot / Fargate** | ⚠️ No autopilot; Spot pools available | ✅ Fargate (serverless nodes) | ✅ Autopilot (best-in-class) |
| **Managed identity integration** | ✅ Workload Identity (UAMI + federation) | ✅ IRSA (IAM Roles for Service Accounts) | ✅ Workload Identity |
| **Default CNI** | Azure CNI / Azure CNI Overlay / Kubenet | AWS VPC CNI | Dataplane V2 (Cilium-based) |
| **Upgrade experience** | Node pool rotation or in-place | Managed node groups in-place | Managed; Autopilot auto-upgrades |
| **Ecosystem maturity** | Strong Azure integration; good enterprise adoption | Broadest ecosystem; most StackOverflow answers | Best built-in observability; Autopilot is the hands-off gold standard |

**Rule of thumb:** AKS for Azure-first shops; EKS for AWS-first or broadest ecosystem needs; GKE Autopilot for teams that want to minimise cluster ops overhead and are on GCP.

---

## Node Pool Design

### Separate system and user node pools (AKS / EKS node groups)
- **System pool:** reserved for kube-system, monitoring, ingress controllers. Taint with `CriticalAddonsOnly=true:NoSchedule` so workloads don't land here.
- **User pools:** one or more, sized and tainted for workload types. Allows independent scaling and upgrades.

### Node pool topology patterns
- **Single pool:** fine for small clusters (<10 nodes, single team). Operationally simple.
- **Multi-pool by workload class:** recommended for production. Separate pools for: general workloads, memory-intensive workloads, spot/preemptible (batch/non-critical), GPU (if needed), Windows (if needed).
- **Multi-pool by team (hard tenancy):** separate node pools with taints per team namespace. Higher cost, stronger noisy-neighbour isolation.

### Spot / Preemptible nodes
- 60–80% cheaper. Use for: CI runners, batch jobs, background processing, non-critical async workloads.
- Never use spot for: stateful workloads without checkpointing, workloads without graceful shutdown on SIGTERM, anything with strict availability SLOs.
- Implement a spot termination handler (AWS Node Termination Handler, AKS Spot eviction handler) to drain gracefully on 2-minute eviction notice.

### Sizing guidance
- Start with fewer, larger nodes rather than many small ones — fewer nodes = less overhead, better bin-packing, lower control plane pressure.
- Rule of thumb: 4–8 vCPU, 16–32GB RAM nodes for general workloads. Adjust based on pod density targets.
- Target 60–70% average resource utilisation across the pool — headroom for burst and rolling upgrades.

---

## CNI Selection

### AKS
- **Azure CNI Overlay** (recommended for new clusters): pods get IPs from a separate overlay space, not your VNet subnet. Eliminates IP exhaustion problems at scale. Minor performance overhead vs. native Azure CNI — negligible for most workloads.
- **Azure CNI (native):** pods get VNet IPs. Required if pods need to be directly addressable from outside the cluster (rare). Subnet sizing must account for max pods per node × max nodes — can exhaust large subnets quickly.
- **Kubenet:** avoid for new clusters. Limited NetworkPolicy support, extra hop for pod networking.
- **Cilium (BYO CNI on AKS):** if you need advanced NetworkPolicy (L7), eBPF-based observability, or service mesh without sidecar injection. Higher operational complexity.

### EKS
- **AWS VPC CNI (default):** pods get VPC IPs. Same IP exhaustion concern as Azure CNI native — use prefix delegation mode to multiply available IPs per node.
- **Cilium:** increasingly common on EKS for eBPF performance and advanced NetworkPolicy. Requires disabling AWS VPC CNI.

### GKE
- **Dataplane V2 (Cilium-based, default on new clusters):** use this. Good NetworkPolicy, eBPF observability built in.

---

## Storage Classes

### AKS
- **Azure Disk (Premium SSD v2):** best IOPS/throughput for stateful workloads (databases, message brokers). `ReadWriteOnce` only — one pod per disk.
- **Azure Files:** `ReadWriteMany` — multiple pods can mount simultaneously. Lower IOPS than Disk. Good for shared config, assets, legacy NFS patterns.
- **Default storage class:** points to Azure Disk Standard SSD. Override to Premium SSD v2 for production stateful workloads.
- **ZRS disks:** zone-redundant storage — use if your stateful pods may reschedule across zones. ~25% more expensive than LRS.

### EKS
- **gp3 EBS:** default choice. Better IOPS/price than gp2. `ReadWriteOnce`.
- **EFS:** `ReadWriteMany`, managed NFS. Higher latency than EBS — only when `RWX` is genuinely needed.

### GKE
- **Balanced persistent disk (pd-balanced):** default, good all-round.
- **Hyperdisk Extreme / Balanced:** for high-IOPS stateful workloads.
- **Filestore:** managed NFS, `ReadWriteMany`.

### General storage principles
- Always set explicit `storageClassName` in PVCs — don't rely on default class behaviour being consistent across environments.
- For databases: prefer managed cloud database services (Azure Flexible Server, RDS, Cloud SQL) over running databases inside Kubernetes unless you have a strong reason. Running databases in K8s adds operational complexity that most teams underestimate.
- `VolumeBindingMode: WaitForFirstConsumer` in storage classes — ensures disk is provisioned in the same AZ as the pod. Critical for multi-AZ clusters.

---

## DNS

- CoreDNS is the standard in-cluster DNS for all managed K8s providers. Rarely needs manual tuning.
- **Common issue:** CoreDNS becoming a bottleneck under high pod-to-pod DNS query load. Mitigate with `ndots:5` → `ndots:2` in pod DNS config to reduce unnecessary upstream lookups, or use NodeLocal DNSCache for large clusters (1000+ pods).
- **External DNS:** use the ExternalDNS operator to automatically manage DNS records in Azure DNS / Route 53 / Cloud DNS from Service/Ingress/HTTPRoute annotations. Avoid manually managing external DNS for Kubernetes services.

---

## Multi-Cluster Patterns

- **Single cluster:** right for most teams up to ~200 nodes and ~10 teams. Simpler to operate.
- **Multiple clusters by environment:** prod / staging / dev in separate clusters. Standard approach — different blast radius, different upgrade cadence.
- **Multiple clusters by region:** for multi-region HA or data residency. Needs a fleet management approach (Argo CD ApplicationSets, Fleet, GKE Fleet).
- **Avoid:** one cluster per team (namespace isolation is sufficient for most tenancy requirements and far cheaper to operate).
