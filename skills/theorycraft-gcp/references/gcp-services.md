# GCP Service Selection Guide

## Compute

| Need | Service | Config guidance |
|---|---|---|
| Containerised workloads, K8s | GKE Standard or GKE Autopilot | Autopilot: hands-off, pay per pod request; Standard: more control, manual node pool management |
| Containers without K8s | Cloud Run | Preferred for stateless HTTP; concurrent requests per instance; scale to zero |
| Serverless functions | Cloud Functions (2nd gen) | Built on Cloud Run; simpler DX; use for GCP-native event triggers |
| Web apps / APIs | App Engine or Cloud Run | Cloud Run preferred for new workloads; App Engine for legacy migrations |
| General VMs | Compute Engine | e2-micro/small dev; n2-standard-4 prod; n2d (AMD) or t2a (Arm) for better price/perf |
| GPU / ML | Compute Engine A100/H100 or Vertex AI | Vertex AI for managed ML platform; raw GPU VMs for custom workloads |
| Batch | Cloud Batch or GKE + KEDA | Cloud Batch for simple job arrays; GKE for complex K8s-native batch |

## Data

| Need | Service | Config guidance |
|---|---|---|
| Relational (PostgreSQL/MySQL) | Cloud SQL Flexible | db-g1-small dev; db-n2-standard-4 prod; HA with regional persistent disk for prod |
| Relational (globally distributed) | Cloud Spanner | Multi-region for global apps; expensive but unique scalability + consistency guarantees |
| Document / NoSQL | Firestore | Native mode preferred over Datastore mode; serverless, scales to zero |
| Wide-column / IoT | Bigtable | Minimum 3 nodes prod; HDD for lower cost; SSD for low-latency; best for time series at scale |
| Analytical / Data warehouse | BigQuery | Serverless, pay per TB scanned (on-demand) or slot commitments (flat-rate); default for GCP analytics |
| Search | Vertex AI Search or Elasticsearch on GKE | Vertex AI Search for GCP-native managed search; ES for existing ecosystem |
| Cache | Cloud Memorystore | Redis: M1 Basic (dev, no HA); M1 Standard+ (prod, HA); Memcached for simple caching |
| Object storage | Cloud Storage | Standard (hot); Nearline (monthly access); Coldline (quarterly); Archive (annual) |
| Event streaming | Pub/Sub or Datastream | Pub/Sub for app-level messaging; Datastream for CDC from databases to BigQuery |

## Messaging & Integration

| Need | Service | Config guidance |
|---|---|---|
| Pub/Sub messaging | Cloud Pub/Sub | At-least-once delivery; push (HTTP) or pull; Exactly Once Delivery available as opt-in |
| Task queue | Cloud Tasks | Rate-limited, exactly-once task dispatch; HTTP targets or App Engine handlers |
| Workflow orchestration | Cloud Workflows | Serverless, pay per step; YAML/JSON; good for service orchestration |
| Event-driven functions | Eventarc | Route GCP events (Audit Logs, Pub/Sub, Cloud Storage) to Cloud Run/Functions |
| API management | Apigee or Cloud Endpoints | Apigee: enterprise API management; Cloud Endpoints: lightweight OpenAPI-based |
| Data pipelines | Dataflow | Managed Apache Beam; streaming and batch; preferred over Spark for GCP-native |

## Networking

| Need | Service | Notes |
|---|---|---|
| Load balancing (global L7) | Cloud Load Balancing (Global HTTPS LB) | Single anycast IP; Cloud Armor WAF integration; multi-region backend support |
| Load balancing (regional L7) | Regional Application LB | For regional workloads; lower latency for single-region |
| Load balancing (L4) | Network Load Balancer | Pass-through or proxy; TCP/UDP |
| CDN | Cloud CDN | Integrates with HTTPS LB; cache at Google's edge |
| DNS | Cloud DNS | Public and private zones; DNSSEC support |
| Private connectivity to GCP APIs | Private Service Connect | Private endpoint for Google APIs (BigQuery, GCS, etc.) inside VPC — no public internet |
| On-prem connectivity (dedicated) | Cloud Dedicated Interconnect | 10Gbps / 100Gbps; lowest latency |
| On-prem connectivity (VPN) | Cloud VPN (HA VPN) | 3Gbps per tunnel; two tunnels for HA; cheaper than Interconnect |
| Multi-project networking | Shared VPC | Host project owns VPC; service projects use it; centralised networking control |
| Firewall | VPC Firewall Rules or Cloud NGFW | VPC rules for basic; Cloud NGFW (formerly Network Firewall) for L7 inspection |

## Identity & Security

| Need | Service | Notes |
|---|---|---|
| Identity provider | Google Workspace or Cloud Identity | Cloud Identity free for GCP-only orgs; Workspace for full productivity suite |
| Workload identity (GKE) | Workload Identity | Bind K8s SA to GCP SA via annotation; no key files; gold standard |
| Service account key files | Avoid | Use Workload Identity, metadata server, or impersonation instead |
| Secrets management | Secret Manager | Versioned, IAM-controlled; automatic rotation via Cloud Functions; replaces env vars |
| Threat detection | Security Command Center (SCC) | Standard (free CSPM); Premium (threat detection, compliance, vulnerability scanning) |
| WAF / DDoS | Cloud Armor | L7 WAF policies; Adaptive Protection for DDoS; attach to HTTPS LB |
| Policy enforcement | Organization Policy Service | Constraints on resource creation (no public IPs, restrict regions, require OS login) |
| Data exfiltration prevention | VPC Service Controls | Perimeters around sensitive projects; block data leaving approved perimeter |
| Encryption key management | Cloud KMS | Software or HSM keys; CMEK for most GCP services; Key Access Justifications for sensitive data |

## Observability

| Need | Service | Notes |
|---|---|---|
| Metrics | Cloud Monitoring | Platform metrics included; custom metrics ~£0.07/metric/month beyond free tier |
| Logs | Cloud Logging | ~£0.41/GB ingested beyond free allotment; set retention and exclusion filters |
| Tracing | Cloud Trace | Auto-instrumented for Cloud Run/GKE with OTEL; SDK for custom |
| Profiling | Cloud Profiler | Continuous CPU/memory profiling; very low overhead; free |
| Dashboards | Cloud Monitoring Dashboards or Grafana Cloud | Grafana Cloud with Cloud Monitoring datasource gives more flexibility |
| Error tracking | Cloud Error Reporting | Automatic grouping of errors from logs; free |

---

## GCP-Specific Decision Rules

**BigQuery on-demand vs flat-rate:**
- On-demand: £4.50/TB scanned. Fine for ad-hoc, low-volume queries.
- Flat-rate (slot commitments): from 100 slots (~£1,400/mo). Break-even at ~300TB/month scanned.
- Use on-demand until query costs approach flat-rate break-even. Add partitioning + clustering first to reduce scan volume.

**GKE Autopilot vs Standard:**
- Autopilot: pay per pod CPU/memory request. No node management. Best for most teams.
- Standard: pay per node. More control over node pools, taints, custom OS images. Better for cost-optimised large clusters with experienced platform teams.
- At small-medium scale with a small platform team: Autopilot almost always wins.

**Cloud SQL vs Spanner:**
- Cloud SQL: regional, familiar PostgreSQL/MySQL, simple ops. Right for 99% of use cases.
- Spanner: globally distributed, 99.999% SLA, no manual sharding. Only warranted for multi-region strong consistency at scale. 3-node minimum ~£2,000/mo.

**Pub/Sub vs Cloud Tasks:**
- Pub/Sub: fan-out, multiple subscribers, stream processing. At-least-once.
- Cloud Tasks: rate-limited dispatch to one target, exactly-once, retries with backoff. Use for job queues.
