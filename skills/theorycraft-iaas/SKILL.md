---
name: theorycraft-iaas
description: IaaS (Infrastructure as a Service) architecture extension. Produces deep VM-based architecture recommendations, infrastructure design patterns, migration guidance, and architecture diagrams (Mermaid for topology, SVG for detailed infrastructure diagrams). Extends theorycraft-cloud — run that skill's analysis first, then this skill adds IaaS-specific depth: VM sizing and families, availability sets and zones, scale sets and autoscaling, storage for VMs, networking (NSGs, load balancers, bastion), Windows and Linux workload patterns, lift-and-shift migration strategy, and hybrid connectivity. Use this skill whenever a user asks about VM-based architectures, IaaS design, VM sizing, availability zones for VMs, scale sets, auto scaling groups, managed disks, bastion hosts, Windows Server workloads, lift-and-shift migrations, or hybrid cloud connectivity. Trigger for any architecture question where compute is VM-based rather than containerised or serverless.
---

# TheoryCraft IaaS

An IaaS architecture extension. Assumes theorycraft-cloud has produced or will produce the high-level analysis. This skill adds IaaS-specific depth: VM design, HA patterns, storage, networking, and migration strategy.

---

## Behaviour

### Step 1 — Confirm or run theorycraft-cloud analysis
Build on theorycraft-cloud analysis if available. If not, proceed — self-sufficient.

### Step 2 — IaaS Pattern Classification
Before recommending specifics, classify the IaaS use case:

| Pattern | Description |
|---|---|
| **Lift and shift** | Move existing VMs to cloud with minimal change |
| **Lift and optimise** | Move to cloud, right-size and modernise config, not architecture |
| **Scale set / ASG** | Stateless VM fleet behind a load balancer, auto-scaled |
| **Stateful multi-tier** | VMs with attached storage, ordered dependencies (DB, app, web tiers) |
| **Windows workload** | Licensed software, domain join, RDP access, specific kernel/OS requirements |
| **HPC / GPU** | Compute-intensive, specialised SKUs, MPI networking |
| **Hybrid** | VMs that must communicate with on-prem over VPN or private circuit |

### Step 3 — VM Sizing and Family Selection
Always recommend specific VM families and SKUs with rationale. Never say "an appropriately sized VM."

### Step 4 — Produce Diagrams
Always produce at least one diagram.

**Mermaid** — for topology showing VM tiers, load balancers, and network flows
**SVG** — for detailed infrastructure diagrams showing AZ placement, subnet layout, NSGs, and storage attachments

---

## Output Structure

### 🖥️ VM Design

- **VM family and SKU** — specific recommendation with rationale (compute-optimised vs memory-optimised vs general purpose)
- **OS / image** — specific base image, marketplace image, or custom image approach
- **Storage** — OS disk type, data disk type and count, caching policy
- **Availability** — single VM (dev only), Availability Set, Availability Zones — recommend zones for prod
- **Scaling** — fixed fleet vs Scale Sets (Azure) / Auto Scaling Groups (AWS) / Managed Instance Groups (GCP)

#### VM family quick reference (cross-provider)

| Workload | Azure | AWS | GCP |
|---|---|---|---|
| General purpose | D-series v5 (Dsv5) | m6i / m7i | n2-standard |
| Compute optimised | F-series (Fsv2) | c6i / c7i | c2-standard |
| Memory optimised | E-series v5 (Esv5) | r6i / r7i | m2-ultramem / n2-highmem |
| Burstable (dev/test) | B-series | t3 / t4g | e2-micro/small |
| Windows optimised | D/E-series (same family, Windows licence) | m6i Windows LI | n2-standard (Windows) |
| Storage optimised | L-series (Lsv3) | i4i | n2-highstorage |
| GPU | NC-series (NCv3/NCA100) | p4 / g5 | a2-highgpu |

### 🔁 High Availability Design

Always recommend Availability Zones for production. Cover:
- **Zone spread:** minimum 2 zones for HA, 3 zones for resilience against zone failure during maintenance
- **Load balancer:** zone-redundant Standard LB (Azure), ALB/NLB (AWS), Cloud LB (GCP) in front of VM fleet
- **PodDisruptionBudget equivalent:** Update Domain / fault domain separation in Availability Sets, or zone pinning in Scale Sets
- **Stateful HA:** primary + standby pattern, quorum-based clustering, or shared storage (Azure Shared Disk, AWS EBS Multi-Attach)

### 💾 Storage Design

- **OS disk:** Premium SSD for prod (never Standard HDD); ephemeral OS disk where supported (faster, cheaper, no persistence needed)
- **Data disks:** Premium SSD v2 (Azure) / gp3 (AWS) / Hyperdisk Balanced (GCP) as default for data; size to IOPS requirements not just capacity
- **Shared storage:** Azure Shared Disk / EFS / Filestore for multi-VM access patterns
- **Backup:** Azure Backup / AWS Backup / GCP Backup and DR — always define RPO/RTO before choosing backup frequency

### 🌐 Networking Design

- **Subnet segmentation:** web tier (public or behind LB), app tier (private), data tier (isolated — no route to internet)
- **NSG / Security Group design:** deny-all default, explicit allow by tier-to-tier and port
- **Bastion / jump host:** Azure Bastion / AWS Systems Manager Session Manager (no bastion needed) / IAP (GCP) — prefer managed bastion over self-managed jump box
- **Private DNS:** internal DNS resolution for VM hostnames within VNet/VPC
- **Egress:** NAT Gateway for outbound internet from private subnets (avoid public IPs on app/data tier VMs)

### 🪟 Windows-Specific Considerations

When workload is Windows:
- **Licensing:** Azure Hybrid Benefit (AHUB) reduces Windows Server cost ~40% if you have SA/subscription licences; AWS BYOL on Dedicated Hosts; GCP BYOL
- **Domain join:** Azure AD Domain Services (managed AD) or extend on-prem AD via VPN; avoid standalone workgroup VMs for enterprise workloads
- **RDP access:** never expose RDP (3389) to internet; Azure Bastion / AWS SSM / GCP IAP only
- **Patching:** Azure Update Manager / AWS Systems Manager Patch Manager / OS Config — automated patching with maintenance windows
- **Agent:** install Azure Monitor Agent / CloudWatch Agent / Ops Agent for logs and metrics

### 🔄 Migration Patterns

For lift-and-shift or lift-and-optimise:
- **Discovery:** Azure Migrate / AWS Migration Hub / Migrate for Compute Engine — assess on-prem inventory, dependencies, right-sizing recommendations
- **Replication:** Azure Site Recovery / AWS MGN (Application Migration Service) / Migrate for Compute Engine — continuous block-level replication with cutover
- **Right-sizing:** never lift at current on-prem size; use assessment tool recommendations and reduce by 20–30% (cloud performance ≠ on-prem performance at same spec)
- **Wave planning:** migrate by dependency group, not alphabetically; database tier last (or move to managed service in parallel)

### 💰 IaaS FinOps

- Concrete monthly cost estimates in GBP; specify SKU, region, OS (Windows adds ~40% vs Linux on most providers)
- **Reserved Instances / CUDs:** 1-year saves ~35–40% (Azure/AWS), 3-year saves ~50–60%; commit only on stable, long-running VMs
- **Dev/test cost reduction:** Azure Dev/Test subscription (~50% off); AWS dev instance types on off-hours scheduler; GCP preemptible for non-prod
- **Spot/Preemptible:** only for stateless/batch VMs; Windows Spot available but less discount than Linux
- **Idle VM detection:** VMs that run 24/7 but are used 8 hours/day are wasting ~65% of compute cost; implement start/stop automation for non-prod

### 🚫 Anti-Patterns

- **Public IPs on app/data tier VMs** — unnecessary attack surface; use load balancer + private subnets
- **Manual snowflake VMs** — handcrafted VMs that can't be reproduced from IaC; treat every VM as cattle not pets
- **Oversized VMs "just in case"** — use right-sizing assessments; over-provisioning is the single biggest IaaS cost waste
- **No shutdown for non-prod** — dev/test VMs running 24/7 at prod sizing; auto-shutdown saves 65%+ on non-prod
- **RDP/SSH to internet** — expose management ports only via bastion; direct internet exposure is one misconfiguration from compromise
- **Ignoring ephemeral OS disks** — for stateless scale set VMs, ephemeral OS disk is faster and free; use it

### 📐 Architecture Diagrams

Always produce:
1. **Topology overview** (Mermaid) — VM tiers, load balancers, networking layers, AZ placement
2. **Infrastructure detail** (SVG) — subnet layout, NSG boundaries, storage attachments, bastion access path, AZ columns

---

## Reference Files

- `references/vm-sizing.md` — detailed VM family comparisons, Windows sizing, IOPS/throughput benchmarks, right-sizing methodology
- `references/iaas-networking.md` — subnet design patterns, NSG rule sets, load balancer config, bastion patterns, hybrid connectivity
- `references/migration-patterns.md` — lift-and-shift tooling, wave planning, database migration options, cutover strategy
- `references/iaas-finops.md` — RI benchmarks by provider/region/OS in GBP, Dev/Test pricing, Spot for IaaS, idle VM cost modelling
