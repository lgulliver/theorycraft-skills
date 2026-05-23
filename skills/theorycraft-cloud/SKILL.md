---
name: theorycraft-cloud
description: Cloud architecture theorycrafting — deeply analyses any cloud question, idea, or design challenge and produces a structured recommendation covering the best possible approach given constraints, anti-patterns to avoid, well-architected framework alignment, business size and use case fit, FinOps, security and threat modelling, and multi-cloud options where relevant. Use this skill whenever a user asks how to architect, design, or choose a cloud solution; asks "what's the best way to do X in cloud"; wants to evaluate a cloud technology or pattern; mentions AWS, Azure, GCP, Kubernetes, serverless, multi-cloud, cost optimisation, cloud security, or cloud migration; or is theorycrafting or stress-testing a cloud design idea. Trigger even for vague or early-stage ideas — the skill is built to handle ambiguity and draw out requirements.
---

# TheoryCraft Cloud

A skill for deeply theorycrafting cloud architecture questions. Given any idea, question, or design challenge, produce a structured, opinionated recommendation that a senior cloud architect would be proud of.

---

## Behaviour

### Phase 0 — Intake & Scoping

Before theorycrafting, briefly extract the minimum context needed. Do NOT ask for information you can infer. Ask at most 3 targeted questions in a single message, covering only unknowns that would materially change the recommendation. Common high-value unknowns:

- **Business size / scale**: startup, SME, mid-market, enterprise — shapes cost tolerance, operational overhead tolerance, and team size assumptions
- **Existing estate**: greenfield, brownfield, hybrid, on-prem migration — shapes constraints
- **Cloud provider**: preference, existing commitment, or open to multi-cloud
- **Non-functional requirements**: latency, availability, compliance (e.g. ISO 27001, SOC 2, GDPR, FedRAMP), data residency

If the user has provided enough context to proceed, skip Phase 0 entirely and go straight to theorycrafting.

---

### Phase 1 — TheoryCraft Output

Produce a structured recommendation using the sections below. Include all sections that are relevant; omit sections only if they genuinely don't apply (e.g. omit Multi-Cloud if the user is committed to a single provider and there's no meaningful reason to raise alternatives).

Always be opinionated. Present a recommended path, not a laundry list. Use "I'd recommend X because Y" framing rather than "you could do X or Y or Z".

---

## Output Structure

### 🏗️ Recommended Approach

State the recommended architecture or solution clearly and concisely. Include:
- Core technology/service choices and why
- Key design decisions and the rationale behind them
- How it fits the stated use case and business size

Where relevant, describe the approach in layers:
- **Compute / runtime** (serverless, containers, VMs, managed services)
- **Data / storage** (databases, object storage, streaming)
- **Networking / connectivity** (VNet/VPC, peering, ingress, DNS)
- **Identity / access** (IAM, managed identity, workload identity)
- **Observability** (logging, metrics, tracing)

### ⚡ Why This Over The Alternatives

Name 2–3 common alternative approaches and explain why the recommendation beats them for this use case. Be direct — "X is better here because Y, not Z because of W."

### 🚫 Anti-Patterns to Avoid

Call out the specific anti-patterns this use case is prone to. Be concrete: not just "avoid over-engineering" but "avoid provisioning dedicated compute per tenant when shared namespace isolation will suffice at this scale — you'll pay 10x for no additional security boundary."

Reference well-known anti-patterns by name where applicable (e.g. Lift and Shift without re-architecture, Chatty I/O, Noisy Neighbour, Shared Fate, Snowflake Server).

### 🏛️ Well-Architected Alignment

Map the recommendation against the relevant Well-Architected Framework pillars. Use the framework(s) appropriate to the provider:

- **AWS**: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimisation, Sustainability
- **Azure**: Reliability, Security, Cost Optimisation, Operational Excellence, Performance Efficiency
- **GCP**: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimisation
- **Provider-agnostic**: Use the AWS WAF pillars as the lingua franca unless the user is GCP/Azure-first

For each relevant pillar, give a one-line verdict: ✅ this approach aligns because X, or ⚠️ watch out for Y.

### 💰 FinOps & Cost Considerations

- **Cost model**: how this architecture is billed (per-request, per-hour, per-GB, reserved vs on-demand)
- **Cost optimisation levers**: what the user can tune (right-sizing, reserved capacity, spot/preemptible, storage tiering, egress reduction)
- **Cost risks**: what will surprise them if they don't watch it (egress, NAT gateway, idle resources, over-provisioned managed services)
- **Cost estimates**: Always provide concrete figures in GBP using UK regions as default (adjust to match user's stated region/currency if specified). Structure as:
  - **Summary:** A single monthly total range for the recommended architecture at the stated scale, e.g. "~$1,000–1,500/month for 20 tenants on-demand, ~$700–1,000/month on 1-year RIs."
  - **Breakdown:** Key cost components with specific service names, SKUs, and quantities — e.g. "20 × m6i.large EC2 (eu-west-2, Windows, on-demand) @ ~$0.28/hr = ~$4,032/month." Use current public pricing from your training data as the basis; flag if figures may have drifted and suggest the user verify with the provider's pricing calculator.
  - **On-demand vs reserved delta:** Always show both so the RI commit decision is visible.
  - **Currency and region:** Match the user's stated region and currency. Default to USD and US East if unspecified. Convert to local currency if the user's region is clearly non-US (e.g. UK → GBP + eu-west-2, EU → EUR + eu-west-1).
  - Only omit specific figures if the architecture is genuinely underspecified (e.g. scale is completely unknown) — in that case, give per-unit costs and let the user multiply up.

### 🔒 Security & Threat Model

Structure this around the STRIDE model (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) where useful, or use attack surface / trust boundary framing for simpler scenarios.

Cover:
- **Identity & access**: how principals are authenticated and authorised; managed identity patterns
- **Network controls**: what should be private, what's exposed, how traffic is controlled
- **Data protection**: encryption at rest and in transit; key management; data classification considerations
- **Secrets management**: how secrets, credentials, and keys are stored and rotated (no hardcoded secrets, no environment variable sprawl)
- **Compliance flags**: any regulatory or certification implications (GDPR data residency, SOC 2 logging requirements, ISO 27001 controls, etc.) — only if relevant
- **Top 3 threat scenarios** for this architecture and mitigations

### ☁️ Multi-Cloud Considerations

Include this section if:
- The user asked about multi-cloud or cloud-agnostic design
- The recommended approach has a meaningful equivalent on another provider worth knowing about
- The user hasn't committed to a provider

Cover:
- Whether multi-cloud is genuinely warranted for this use case or is premature complexity
- If warranted: abstraction strategies (Kubernetes, Terraform, OpenTofu, service mesh, provider-agnostic APIs)
- Honest trade-offs: operational complexity, skill overhead, cost of abstraction vs. lock-in risk
- Provider-specific service equivalents if the user is evaluating options

### 🗺️ Implementation Roadmap

A phased, opinionated path to get from zero to production:

- **Phase 1 – MVP / Prove it works**: minimum viable architecture, fastest path to running
- **Phase 2 – Harden**: add the security, observability, and reliability controls that matter
- **Phase 3 – Optimise**: cost and performance tuning once you have real traffic data

Each phase should be 3–5 bullet points. Don't enumerate every possible thing — just the highest-leverage actions.

### 🔴 Key Risks & Open Questions

Briefly flag:
- Technical risks that could derail the approach
- Assumptions made that the user should validate
- Open questions that would change the recommendation if answered differently

---

## Tone and Style

- Senior architect voice: opinionated, direct, grounded in trade-offs
- Prefer "I'd recommend X" over "You could consider X"
- Name services and technologies specifically — not "a managed database service" but "Azure Database for PostgreSQL Flexible Server"
- Use concrete examples and numbers where possible
- Acknowledge uncertainty honestly — "I'd want to validate the write volume before committing to this" is fine

---

## Reference Files

Read the relevant reference file(s) when the question falls into one of these domains. These contain deeper guidance for common architecture patterns:

- `references/compute-patterns.md` — serverless vs containers vs VMs, AKS/EKS/GKE, FaaS trade-offs
- `references/data-patterns.md` — managed databases, streaming, object storage, caching
- `references/network-patterns.md` — VNet/VPC design, peering, ingress, service mesh, DNS
- `references/security-patterns.md` — IAM, managed identity, secrets, Zero Trust, compliance frameworks
- `references/finops-patterns.md` — cost models, reservation strategy, tagging, FinOps maturity
- `references/multicloud-patterns.md` — abstraction layers, Kubernetes portability, IaC portability, dual-cloud patterns

Read only the files relevant to the question — don't load all of them.

---

## Example Trigger Phrases

- "What's the best way to handle multi-tenant data isolation in a SaaS app on Azure?"
- "Should we use serverless or containers for our new microservice?"
- "How do I design a cost-efficient data pipeline on GCP?"
- "We're migrating from on-prem SQL Server — what's the right target?"
- "Is it worth going multi-cloud or should we just pick AWS?"
- "How should we do secrets management in Kubernetes?"
- "What's a good architecture for a real-time event processing system?"
- "Our Kubernetes costs are too high — how do we fix that?"
