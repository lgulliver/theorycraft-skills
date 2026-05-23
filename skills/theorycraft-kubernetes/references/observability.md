# Kubernetes Observability Reference

## The Four Signals

| Signal | What it tells you | CNCF / standard tool category |
|---|---|---|
| **Logs** | What happened, errors, request details | Collector → logging backend |
| **Metrics** | System health, resource utilisation, SLIs | Prometheus scrape or OTLP → metrics backend |
| **Traces** | Request latency breakdown, service dependencies | OTLP → tracing backend |
| **Profiles** | CPU/memory hotspots, continuous profiling | eBPF-based or SDK → profiling backend |

For tool selection across all four signals, see `cncf-landscape.md` — the right stack depends on managed provider, existing tooling, air-gap requirements, and operational overhead tolerance.

---

## Stack Selection by Deployment Model

Before recommending specific tools, establish:
1. **Managed or self-hosted?** Managed providers have native observability integrations with zero ops overhead.
2. **Existing tooling?** Don't replace a working stack — extend it.
3. **Air-gapped or regulated?** Constrains to self-hostable, no-external-dependency tools.
4. **Cross-provider?** Requires open standards (OTLP, Prometheus remote write) over provider-native.

See `cncf-landscape.md` observability section for the full comparison table and stack combinations.

---

## OpenTelemetry (OTLP) — the collection standard

Regardless of which backend is chosen, OpenTelemetry is the emerging collection standard:
- **OpenTelemetry Collector** — vendor-neutral pipeline: receive, process, export to any backend
- **OTEL Operator** — Kubernetes operator that manages collectors and auto-instruments workloads
- **Auto-instrumentation** — inject instrumentation without code changes for Java, Python, Node.js, .NET, Go

Using OTLP as the wire format decouples collection from the backend. You can change backends without re-instrumenting applications.

### Auto-instrumentation via OTEL Operator
```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: my-instrumentation
  namespace: my-namespace
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
  sampler:
    type: parentbased_traceidratio
    argument: "0.25"  # 25% head-based sampling
  java:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:latest
  python:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:latest
  nodejs:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-nodejs:latest
```

---

## Key Metrics to Alert On

These are consistent regardless of which metrics backend is used. PromQL-compatible query syntax shown.

### Cluster health
- `kube_node_status_condition{condition="Ready",status="true"}` < 1 — node not ready
- `rate(kube_pod_container_status_restarts_total[5m])` > threshold — CrashLoopBackOff indicator
- `kube_pod_status_phase{phase=~"Pending|Unknown"}` > 0 sustained >5min — stuck pods
- API server error rate > 1% — control plane degradation

### Resource pressure
- Node CPU utilisation > 80% sustained — approaching saturation
- Node memory utilisation > 85% — OOMKill risk
- PVC usage > 80% — storage running out (no auto-expand by default)
- `kube_resourcequota` used / hard > 90% — namespace quota nearly exhausted

### Workload health
- Deployment unavailable replicas > 0 sustained — rollout stuck or pods failing
- `kube_horizontalpodautoscaler_status_condition{condition="AbleToScale",status="false"}` — HPA blocked
- Job failure rate > 0 — batch jobs failing silently

### Application SLIs (RED method)
- HTTP error rate: 5xx / total requests
- P99 request latency
- Request rate (for capacity planning)
- Queue consumer lag (if using event-driven autoscaling)

---

## Distributed Tracing

### Trace sampling strategy
- **Head-based sampling:** decide at trace start. Simple, predictable volume. Good starting point (10–20%).
- **Tail-based sampling:** decide at trace end — keeps errors and slow traces, drops fast/successful ones. Better signal density, more complex setup (requires stateful collector with tail sampling processor).
- Start with head-based; move to tail-based when trace volume makes cost/noise a real problem.

### Instrumentation approach
- **Auto-instrumentation** (via OTEL Operator): no code changes; covers Java, Python, Node.js, .NET — start here
- **Manual SDK instrumentation**: for Go and workloads needing custom span attributes or business-context traces

---

## Logging Patterns

### Structured logging is a prerequisite
Before worrying about the logging backend, ensure applications emit structured JSON logs. Unstructured logs are significantly harder to query and alert on at scale.

```json
{"level":"error","ts":"2025-01-01T12:00:00Z","msg":"database connection failed","service":"my-app","trace_id":"abc123","error":"connection refused"}
```

### Log collection patterns
- **DaemonSet collector** (most common): one collector pod per node, reads from `/var/log/pods/`. Works with Fluent Bit, Alloy, OTel Collector.
- **Sidecar collector**: one collector per pod. Higher resource overhead; use only when per-pod config is genuinely needed.
- **Direct from app** (push): application sends logs directly to backend. Simple but couples app to backend.

### Log volume management
Uncontrolled log ingestion is the most common observability cost surprise:
- Set log retention policies per namespace / workload — not "never expire"
- Use sampling or filtering for high-volume debug logs in production
- Drop known-noisy, low-value logs at the collector level before they reach the backend

---

## Profiling

Continuous profiling catches performance regressions that metrics can't see.

| Tool | Approach | Notes |
|---|---|---|
| **Pyroscope (Grafana)** | SDK + eBPF | Integrates with Grafana stack; supports many languages |
| **Parca** | eBPF, no code changes | CNCF project; language-agnostic |
| **Pixie** | eBPF, no code changes | CNCF sandbox; good for K8s-native workloads; more than profiling |
| **Cloud profilers** | Managed (AWS CodeGuru, GCP Cloud Profiler, Azure via App Insights) | Zero ops; provider lock-in |

For most teams: add profiling after metrics, logs, and traces are working well. It's the fourth signal for a reason.
