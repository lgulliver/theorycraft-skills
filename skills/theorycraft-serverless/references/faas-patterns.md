# FaaS Patterns Reference

## AWS Lambda

### Runtime cold start benchmarks (approximate, 512MB memory)
| Runtime | Typical cold start | Notes |
|---|---|---|
| Node.js 20 | 100–300ms | Fastest overall |
| Python 3.12 | 100–400ms | Fast, widely used |
| .NET 8 (NativeAOT) | 200–500ms | Much faster than standard .NET |
| .NET 8 (standard) | 800ms–2s | JIT startup cost |
| Java 21 (SnapStart) | 200–600ms | SnapStart cuts standard 2–5s to this |
| Java 21 (standard) | 2–5s | Avoid for latency-sensitive without SnapStart |
| Go 1.x | 100–300ms | Compiled binary, fast |

### Provisioned concurrency
- Eliminates cold starts entirely. Instances stay warm.
- Cost: charged even when idle, at ~65% of on-demand invocation rate.
- Use for: user-facing synchronous APIs with latency SLOs, not for async queue workers.
- Configure via Application Auto Scaling to scale provisioned concurrency with traffic patterns.

### Lambda concurrency limits
- Default: 1,000 concurrent executions per account per region (soft limit — raise via support ticket)
- Reserved concurrency: cap a specific function to prevent it consuming the whole account limit
- Provisioned concurrency: subset of reserved concurrency that stays warm

### Lambda VPC integration
- Functions in a VPC can reach private resources (RDS, ElastiCache, internal services)
- Cold start historically slower in VPC due to ENI allocation — largely fixed since Hyperplane ENI (2019)
- Requires: VPC, subnets, security groups. Egress to internet needs NAT Gateway.
- For functions that don't need VPC access: keep them outside VPC — simpler, marginally faster

### Lambda ARM (Graviton2)
- ~20% better price/performance for most runtimes. Enable in function config.
- Not compatible with x86-compiled native binaries — check dependencies first.

---

## Azure Functions

### Plan comparison
| Plan | Cold start | Max timeout | VNet | Scale |
|---|---|---|---|---|
| **Consumption** | Yes (~1–3s) | 10 min | ❌ | Automatic to 200 instances |
| **Flex Consumption** | Reduced (pre-provisioned) | 60 min | ✅ | Zone-redundant, faster scale |
| **Premium (EP1+)** | None (pre-warmed) | Unlimited | ✅ | Manual + automatic |
| **Dedicated (App Service)** | None | Unlimited | ✅ | Manual or App Service autoscale |

**Recommendation:**
- Consumption: dev, low-traffic, async workloads where cold start doesn't matter
- Flex Consumption: new default for production — better cold start, VNet, zone redundancy
- Premium: latency-sensitive synchronous functions needing VNet
- Dedicated: when you already have App Service Plan capacity or need predictable billing

### Durable Functions patterns
- **Function Chaining:** call functions in sequence, pass output as input. Orchestrator function with `CallActivityAsync`.
- **Fan-out / Fan-in:** spawn parallel activity functions, wait for all to complete with `Task.WhenAll`.
- **Async HTTP API:** long-running operation with polling endpoint. Client gets 202 + status URL.
- **Monitor:** recurring polling loop with `CreateTimer` — replaces cron for conditional waits.
- **Human Interaction:** pause workflow waiting for external event (`WaitForExternalEventAsync`).

Storage backend: Azure Storage (default, cheapest) or MSSQL/Netherite for high-throughput scenarios.

### Azure Functions trigger ecosystem
- HTTP, Timer, Service Bus, Event Hubs, Event Grid, Blob Storage, Queue Storage, Cosmos DB change feed, SignalR, Kafka, RabbitMQ
- Use Service Bus trigger for reliable exactly-once processing (sessions for ordering)
- Use Event Hubs trigger for high-throughput stream processing (batched delivery)
- Use Event Grid trigger for event-driven reactions to Azure resource events

---

## GCP Cloud Run

### Key differentiator: concurrent requests per instance
Unlike Lambda/Functions (one request per instance), Cloud Run instances handle multiple concurrent requests. This changes the scaling model:
- Set `--concurrency` to match your app's actual thread capacity (default 80, max 1000)
- One warm instance can handle many requests → fewer cold starts at steady load
- Memory and CPU shared across concurrent requests — size accordingly

### Cloud Run vs Cloud Functions (2nd gen)
Cloud Functions 2nd gen is built on Cloud Run. The differences are primarily DX:
- Cloud Run: deploy any container, full control, better for existing containerised apps
- Cloud Functions: deploy source code, Google manages the container, simpler for pure FaaS

For new serverless workloads on GCP: prefer Cloud Run for flexibility. Cloud Functions for simple event-triggered functions already in GCP-native code.

### Always-on CPU
By default, Cloud Run only allocates CPU during request processing (CPU throttled between requests). Enable "CPU always allocated" for:
- Background threads / async processing
- Durable connections (WebSockets, gRPC streaming)
- CPU-intensive startup work
Cost increases with always-on CPU but eliminates some cold start issues.

---

## VNet / Private Connectivity Patterns

### Lambda → Private RDS/ElastiCache
Lambda in VPC subnets, security group allowing outbound to RDS security group. RDS in private subnets, no public access.

### Azure Functions → Private PostgreSQL
Functions Premium/Flex with VNet integration. PostgreSQL Flexible Server in VNet or via Private Endpoint. Private DNS zone for `privatelink.postgres.database.azure.com`.

### Cloud Run → Private Cloud SQL
Use Cloud SQL Auth Proxy as a sidecar, or VPC connector for direct private IP access. Workload Identity for Cloud SQL IAM authentication — no passwords.
