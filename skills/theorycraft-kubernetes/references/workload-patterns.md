# Workload Patterns Reference

## Workload Type Selection

| Type | Use when | Don't use when |
|---|---|---|
| **Deployment** | Stateless services, APIs, web frontends | You need stable network identity or ordered rollout |
| **StatefulSet** | Stateful apps needing stable hostname, ordered start/stop, stable PVCs (databases, message brokers, search) | The app is truly stateless — adds unnecessary complexity |
| **DaemonSet** | One pod per node: log collectors (Alloy, Fluent Bit), node exporters, CNI plugins | Variable pod count per node is needed |
| **Job** | One-off tasks: migrations, data processing, batch runs | Long-running or recurring work |
| **CronJob** | Scheduled recurring tasks | Sub-minute scheduling (K8s CronJob resolution is 1 min) — use KEDA or an in-app scheduler instead |

---

## Resource Requests and Limits

### The single most common misconfiguration in Kubernetes

**Requests** = what the scheduler uses for bin-packing. Set this to what the pod *normally* uses (p75 of steady-state consumption).

**Limits** = the hard cap. CPU limits cause throttling; memory limits cause OOMKill.

### Recommended patterns by workload class

**Latency-sensitive services (APIs, real-time processing):**
```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    memory: "512Mi"  # Set memory limit
    # No CPU limit — CPU throttling is worse than occasional over-use for latency-sensitive workloads
```
Omitting CPU limits is intentional for latency-sensitive workloads. CPU throttling at the cgroup level happens even when the node has spare capacity, causing p99 latency spikes. Set requests accurately so the scheduler places pods correctly.

**Batch / background workloads:**
```yaml
resources:
  requests:
    cpu: "250m"
    memory: "128Mi"
  limits:
    cpu: "2"       # Limit CPU for batch to protect neighbours
    memory: "256Mi"
```

**Never do:**
- No requests set (scheduler treats as zero — terrible bin-packing)
- Limits set much higher than requests (allows massive burst, noisy neighbour)
- requests == limits (Guaranteed QoS class — fine for critical pods, wasteful for others)

### QoS classes (set implicitly by requests/limits)
- **Guaranteed:** requests == limits. First to get resources, last to be evicted. Use for critical stateful pods.
- **Burstable:** requests < limits. Standard for most workloads.
- **BestEffort:** no requests or limits. First to be evicted under pressure. Don't use in production.

---

## Autoscaling

### HPA (Horizontal Pod Autoscaler)
- Scales pod count based on metrics (CPU, memory, custom metrics via Metrics Server or KEDA)
- Best for: stateless services with variable traffic
- Gotcha: CPU-based HPA is reactive — scale-out happens after CPU is already high. For latency-sensitive workloads, use a leading indicator (queue depth, request rate) via KEDA instead.
- Always set `minReplicas >= 2` for production workloads — HPA can scale to 1 under low load, removing your redundancy.

### VPA (Vertical Pod Autoscaler)
- Adjusts resource requests/limits based on observed usage
- **Recommendation mode only** for production — VPA in Auto mode evicts pods to resize, which can cause unexpected restarts. Use it as an advisor.
- Workflow: run VPA in `Off` or `Initial` mode, observe recommendations for 1–2 weeks, apply manually.
- Cannot be used alongside HPA on CPU/memory metrics simultaneously — use KEDA for HPA and VPA for right-sizing independently.

### KEDA (Kubernetes Event-Driven Autoscaler)
- Scale on any external metric: queue depth (Service Bus, SQS, NATS JetStream), Prometheus query, cron schedule, HTTP request rate, and 60+ other scalers.
- Enables **scale-to-zero** — pods fully removed when queue is empty, provisioned on first message. Excellent for cost-efficiency on event-driven workloads.
- Replaces HPA for event-driven patterns. KEDA creates its own HPA under the hood.
- Key config: `pollingInterval` (how often KEDA checks the scaler, default 30s), `cooldownPeriod` (how long to wait before scaling to zero after last event).

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: queue-consumer-scaler
spec:
  scaleTargetRef:
    name: queue-consumer
  minReplicaCount: 0   # scale to zero
  maxReplicaCount: 20
  pollingInterval: 15
  cooldownPeriod: 60
  triggers:
    - type: azure-servicebus
      metadata:
        queueName: my-queue
        messageCount: "5"  # target messages per replica
```

---

## Multi-Tenancy Patterns

### Namespace-per-team (soft tenancy)
- Standard approach. Namespaces provide RBAC isolation, NetworkPolicy scope, and resource quota boundaries.
- Add: ResourceQuotas per namespace, LimitRanges to set default requests/limits, NetworkPolicies for default-deny.
- Workloads from different teams share nodes — noisy neighbour is possible but manageable with resource requests.

### Node pool per team (hard tenancy)
- Dedicated node pools tainted per team. Workloads only land on their team's nodes.
- Stronger isolation, no noisy neighbour on compute. ~2–3× more expensive due to underutilisation.
- Use when: compliance requires compute isolation, teams have very different workload characteristics, or a team's workloads are disruptive.

### vCluster (virtual clusters)
- Full Kubernetes API per tenant, running inside namespaces on a host cluster.
- Teams get their own CRDs, admission webhooks, RBAC models without affecting others.
- Good for: platform teams offering self-service K8s to internal teams; CI/CD ephemeral environments.
- Overhead: each vcluster runs a lightweight control plane (~50–100MB RAM).

### Resource Quotas
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.memory: 40Gi
    pods: "50"
    persistentvolumeclaims: "10"
```

---

## StatefulSet Patterns

### Key properties that matter
- **Stable network identity:** `pod-name.service-name.namespace.svc.cluster.local` — essential for leader election, peer discovery in clustered databases.
- **Ordered rollout:** pods start/stop in order (0, 1, 2...). Critical for databases with leader/follower topology.
- **Stable PVCs:** each pod gets its own PVC that survives pod deletion. PVCs are NOT deleted when a StatefulSet is scaled down — manual cleanup required.

### Headless service (required for StatefulSet DNS)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-statefulset
spec:
  clusterIP: None   # headless
  selector:
    app: my-statefulset
```

### PodDisruptionBudgets for StatefulSets
Always set a PDB to prevent all replicas being evicted simultaneously during node drain:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-statefulset-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: my-statefulset
```
