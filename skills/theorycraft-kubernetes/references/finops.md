# Kubernetes FinOps Reference

## Cost Model Fundamentals

Kubernetes cluster costs break down into four buckets:
1. **Control plane** — free (AKS, GKE Standard) or ~$73/mo (EKS, GKE Enterprise)
2. **Node compute** — the dominant cost; VM SKU × node count × hours
3. **Storage** — managed disks/PVCs, object storage for backups/logs
4. **Networking** — egress, load balancers, NAT gateway, inter-zone traffic

Node compute is typically 70–85% of total cluster cost. Right-sizing nodes and using Spot/Reserved capacity are the highest-leverage levers.

---

## Reserved Instances / Committed Use by Provider

### AKS (Azure)
- **Reserved VM Instances:** commit to 1 or 3 years on specific VM family + region. ~40% saving (1yr) / ~60% saving (3yr) vs on-demand.
- **Azure Savings Plans:** more flexible — applies across VM families in a region. ~35% saving (1yr). Better if you plan to change SKUs.
- **Dev/Test pricing:** ~50% off many SKUs for non-production clusters via Dev/Test subscription.
- **Spot node pools:** 60–80% cheaper. Eviction notice: 30 seconds (Azure Spot). Use for: batch jobs, CI runners, KEDA scale-to-zero workloads. Never for: stateful workloads, ingress controllers, monitoring stack.

### EKS (AWS)
- **EC2 Reserved Instances:** 1yr ~35–40%, 3yr ~50–60% vs on-demand. Windows adds ~40% to base Linux price.
- **Compute Savings Plans:** flexible across instance families, ~35% (1yr). Good if you use Karpenter and instance flexibility is high.
- **Spot Instances:** 70–90% cheaper. 2-minute termination notice. Use AWS Node Termination Handler for graceful drain. Karpenter handles Spot natively with fallback to on-demand.
- **Fargate (EKS):** per-vCPU/GB-hour billing, no node management. More expensive per unit than right-sized EC2 but zero node overhead. Good for variable/bursty workloads where node management cost exceeds Fargate premium.

### GKE (GCP)
- **Committed Use Discounts (CUDs):** 1yr ~37%, 3yr ~55%. Applies to Compute Engine (underlying GKE nodes).
- **Sustained Use Discounts:** automatic ~20–30% for instances running >25% of month. No commitment needed — GKE nodes typically qualify automatically.
- **Spot VMs:** 60–91% cheaper. 30-second eviction notice.
- **Autopilot:** billing per pod resource request (vCPU + memory), not per node. Eliminates wasted node headroom. Often cheaper than a poorly-utilised Standard cluster. More expensive than a well-optimised Standard cluster. Recommended default for teams that don't want to manage node pools.

---

## Node Right-Sizing

### Common waste patterns
- **Over-provisioned requests:** pods requesting 2 CPU / 4GB but using 0.3 CPU / 500MB. Scheduler treats requests as reserved — wasted node capacity.
- **Under-utilised node pools:** cluster autoscaler won't scale down a node if any pod can't be evicted (no PDB, local storage, etc.)
- **Fixed-size node pools:** no autoscaler configured — nodes run 24/7 regardless of actual load.

### Right-sizing process
1. Run VPA in recommendation mode for 1–2 weeks: `kubectl describe vpa -n <namespace>` → check `Target` recommendations
2. Use `kubectl top pods -A` to spot outliers
3. Adjust requests to match p75 of actual usage (not p99 — that's what limits are for)
4. After adjusting requests, cluster autoscaler can bin-pack more efficiently and scale down more aggressively

### Target utilisation
- Aim for 60–70% average node utilisation (CPU and memory). Below 50% = wasteful. Above 80% = risky (no headroom for burst or rolling upgrades).

---

## Spot / Preemptible Best Practices

### Workload requirements for Spot
- Graceful shutdown on SIGTERM within `terminationGracePeriodSeconds` (typically 30–60s)
- No local state that can't be reconstructed (use PVCs or external storage for anything that matters)
- Tolerates `node.kubernetes.io/not-ready` and spot eviction taints
- PodDisruptionBudget set so eviction of one node doesn't take down the whole workload

### Taint/toleration pattern for Spot node pools
```yaml
# Node pool taint (set on the node pool, not manually)
# node.kubernetes.io/spot:NoSchedule

# Pod toleration to allow scheduling on spot
tolerations:
  - key: "node.kubernetes.io/spot"
    operator: "Exists"
    effect: "NoSchedule"

# Prefer spot but fall back to on-demand
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
            - key: kubernetes.azure.com/scalesetpriority  # AKS
              operator: In
              values: ["spot"]
```

---

## KEDA Scale-to-Zero Savings

Scale-to-zero eliminates idle compute cost for event-driven workloads entirely. The saving is 100% of the pod's resource cost during idle periods.

**Typical use cases and savings profile:**
- Queue consumers processing overnight batch jobs: ~16hrs/day idle → ~67% compute saving
- Webhook processors with bursty traffic: depends on traffic pattern
- Scheduled jobs (replace CronJob for complex scaling): savings vary

**Gotcha:** scale-to-zero has a cold start penalty (pod scheduling + container start time, typically 10–30s). Not suitable for latency-sensitive synchronous paths. Fine for async queue consumers.

---

## Cost Estimate Benchmarks (UK, GBP, mid-2025 pricing)

Use these as directional benchmarks. Verify with provider pricing calculator before committing.

### AKS node pool (Linux, on-demand, UK South)
| SKU | vCPU | RAM | On-demand/hr | On-demand/mo | 1yr RI/mo |
|---|---|---|---|---|---|
| Standard_D2s_v5 | 2 | 8GB | ~£0.087 | ~£63 | ~£38 |
| Standard_D4s_v5 | 4 | 16GB | ~£0.174 | ~£126 | ~£76 |
| Standard_D8s_v5 | 8 | 32GB | ~£0.348 | ~£252 | ~£151 |
| Standard_E4s_v5 | 4 | 32GB | ~£0.252 | ~£183 | ~£110 |

### EKS node pool (Linux, on-demand, eu-west-2 London)
| SKU | vCPU | RAM | On-demand/hr | On-demand/mo | 1yr RI/mo |
|---|---|---|---|---|---|
| m6i.large | 2 | 8GB | ~£0.088 | ~£64 | ~£39 |
| m6i.xlarge | 4 | 16GB | ~£0.176 | ~£128 | ~£78 |
| m6i.2xlarge | 8 | 32GB | ~£0.352 | ~£256 | ~£157 |
| r6i.xlarge | 4 | 32GB | ~£0.265 | ~£193 | ~£118 |

### Cluster fixed costs (approximate monthly)
| Component | AKS | EKS | GKE Standard |
|---|---|---|---|
| Control plane | Free | ~£58 | Free |
| Load balancer (per LB) | ~£15 | ~£15 | ~£15 |
| NAT Gateway | ~£30+ | ~£30+ | ~£25+ |

**Rule of thumb for a small production cluster (3–5 nodes, D4s_v5 / m6i.xlarge):**
- On-demand: ~£400–650/mo
- With 1yr Reserved Instances: ~£250–400/mo
- With mixed on-demand + 50% Spot: ~£250–350/mo
