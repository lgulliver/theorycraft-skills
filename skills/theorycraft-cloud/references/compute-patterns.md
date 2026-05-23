# Compute Patterns Reference

## Decision Framework: Serverless vs Containers vs VMs

### Use Serverless (FaaS / managed runtimes) when:
- Highly variable or unpredictable traffic (bursty, event-driven)
- Event processing, async workflows, lightweight APIs
- Team wants zero infra management and operational overhead is a constraint
- Sub-minute execution (AWS Lambda <15min, Azure Functions <10min, GCF <60min)
- Cost model: paying for idle is unacceptable (pure consumption billing preferred)

**Watch out for**: cold start latency (mitigate with provisioned concurrency / min instances), vendor lock-in on triggers/bindings, poor fit for long-running or stateful workloads, observability gaps in pure serverless.

### Use Containers (Kubernetes / managed container services) when:
- Consistent, predictable workloads with stable throughput
- Long-running services, stateful workloads, WebSocket / streaming
- Multi-tenant SaaS with namespace/network isolation requirements
- Team can absorb K8s operational overhead (or uses a managed plane: AKS, EKS, GKE)
- You need portability between environments (local → CI → prod)

**Key managed K8s trade-offs:**
- **AKS (Azure)**: deepest Azure integration (Workload Identity, AAD, Azure CNI, ESO, Azure Policy). Good default for Azure-first shops. Free control plane. Watch: node pool upgrades, ingress controller complexity.
- **EKS (AWS)**: most mature ecosystem, most enterprise adoption, most operational surface. Control plane costs ~$73/mo. Fargate option removes node management.
- **GKE (GCP)**: best autopilot mode for hands-off scaling, best built-in observability integration with Cloud Monitoring. Autopilot billing per pod resource request, not node.

### Use VMs (IaaS) when:
- Legacy workloads that can't be containerised easily
- Specific OS/kernel requirements (GPU, custom drivers, licensed software)
- Lift-and-shift migration as a first step
- Windows workloads with complex dependencies

**Anti-pattern**: long-term VM sprawl. VMs should be a migration stepping stone or exception, not the default for new workloads.

---

## Sizing Guidance

### Kubernetes right-sizing
- Set resource requests accurately (what the pod normally uses), limits conservatively (max burst)
- Use VPA (Vertical Pod Autoscaler) in recommendation mode first — observe, then act
- Use HPA (Horizontal Pod Autoscaler) for stateless services, KEDA for event-driven scaling (queue depth, message lag, etc.)
- Cluster autoscaler: ensure node pools have appropriate min/max; watch scale-down aggressiveness vs cold start cost

### Serverless right-sizing
- Memory is the primary lever — CPU scales proportionally on Lambda/Functions
- Start higher than you think, then tune down based on profiling (AWS Lambda Power Tuning tool)
- Timeout: set to 2x your p99 execution time in production
