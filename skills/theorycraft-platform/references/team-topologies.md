# Team Topologies Reference

## The Four Team Types

### Stream-aligned team
- Aligned to a flow of work (a product, a service, a customer journey)
- Owns end-to-end delivery — from idea to production
- Has everything needed to deliver value: product, design, engineering, QA
- **Platform relationship:** consumes platform capabilities as a service; should not need to understand how they work
- **Danger sign:** if stream-aligned teams are spending >25% of time on platform/infra concerns, the platform is failing them

### Platform team
- Reduces cognitive load for stream-aligned teams
- Provides self-service capabilities that teams consume without needing specialist knowledge
- **Runs like a product team:** has a backlog, measures adoption and satisfaction, does discovery with customers (the stream-aligned teams)
- **Danger sign:** acting as a gatekeeper (ticket queue) rather than an enabler (self-service)

### Enabling team
- Temporary; helps stream-aligned teams adopt new practices or technologies
- Embeds with teams, runs workshops, then steps back
- Does NOT build long-lived services — that's platform team work
- **Example:** an enabling team that helps all stream-aligned teams adopt OpenTelemetry, then disbands
- **Danger sign:** enabling team becomes permanent and starts building things — it's become a platform team in disguise

### Complicated subsystem team
- Owns a subsystem requiring deep specialist knowledge that changes slowly
- Low interaction with other teams; operates as a service provider
- **Example:** a data platform team, ML infrastructure, or cryptography/security library team
- **Danger sign:** too many complicated subsystem teams; most things don't actually need this level of isolation

---

## Cognitive Load

The central concept. There are three types:

| Type | Description | Platform role |
|---|---|---|
| **Intrinsic** | Complexity inherent to the problem (business logic, domain rules) | Cannot be reduced — it IS the work |
| **Extraneous** | Complexity from the environment (infra, tooling, process) | **This is what the platform reduces** |
| **Germane** | Complexity that builds useful knowledge (learning the domain) | Good cognitive load — enable it |

**The platform's job is to reduce extraneous cognitive load.** Every time a developer has to understand Kubernetes scheduling, Terraform module composition, or network topology to ship a feature — that's extraneous load the platform should be absorbing.

### Cognitive load assessment questions
Ask stream-aligned teams:
- "What do you have to know about infrastructure to deploy a service?"
- "What blocks you from deploying independently?"
- "What do you have to ask the platform team for?"
- "What took longer than it should have last sprint?"

The answers tell you where extraneous load is highest.

---

## Interaction Modes

### X-as-a-Service (default for mature capabilities)
- Stream-aligned team consumes a well-defined service with clear API and documentation
- Minimal interaction required — the service just works
- **Examples:** CI/CD pipeline (teams just push code), namespace provisioning (teams request via IDP), secret management (teams use ESO)
- **When to move to this mode:** capability is stable, well-documented, and teams can use it without help

### Collaboration (for building new capabilities)
- Platform team and stream-aligned team work closely together to build something new
- Temporary — should transition to X-as-a-Service once the capability is stable
- **Examples:** building the first golden path template together with a pilot team; adopting a new observability stack
- **Danger:** collaboration mode that never ends — the teams have fused into a combined team without admitting it

### Facilitating (enabling team mode)
- Enabling team works with stream-aligned team to help them adopt a new capability or practice
- Explicitly temporary; the goal is to make the enabling team redundant for that capability
- **Examples:** running onboarding sessions for a new IDP feature; helping teams instrument their services with OTEL

---

## Platform Boundary Setting

Where to draw the line between platform team ownership and stream-aligned team ownership. This is the most contentious decision in platform engineering.

### Heuristics for drawing the boundary

**Platform owns it when:**
- The capability is needed by multiple teams
- Specialist knowledge is required that most teams don't have
- Inconsistent implementation causes cross-cutting problems (security, compliance, reliability)
- Economies of scale exist (one well-maintained Argo CD vs 10 teams managing their own)

**Stream-aligned team owns it when:**
- The capability is specific to their service or domain
- They need to change it frequently and independently
- Centralising it creates a bottleneck without meaningful benefit

**Canonical examples:**

| Capability | Who owns it |
|---|---|
| Kubernetes cluster | Platform team |
| Namespace within cluster | Shared — platform provisions, team configures |
| CI/CD pipeline template | Platform team |
| CI/CD pipeline for a specific service | Stream-aligned team (using platform template) |
| Secrets management system (ESO, Key Vault) | Platform team |
| Specific secrets for a service | Stream-aligned team |
| Observability stack (Grafana, Loki, Mimir) | Platform team |
| Dashboards and alerts for a service | Stream-aligned team |
| DNS zone | Platform team |
| DNS record for a service | Stream-aligned team (via self-service) |

---

## Common Platform Team Failure Modes

**The ticket queue team:** the platform team has become a queue of requests rather than a product team. Every infra change requires a ticket. Fix: invest in self-service capabilities; measure and reduce ticket volume.

**The platform that nobody uses:** technically excellent but stream-aligned teams route around it because it doesn't meet their needs. Fix: treat platform as a product; do discovery with actual customers; measure adoption.

**The platform team that never says no:** takes on every request from every team, has no strategy, is perpetually behind. Fix: define a platform strategy and product roadmap; say no to things outside it.

**Perpetual enabling:** the platform team spends all its time helping teams use the platform rather than improving it. Fix: build better documentation, templates, and self-service; treat heavy enablement as a signal that the platform UX is failing.

**Platform as a cost centre:** leadership sees the platform team as overhead rather than a multiplier. Fix: measure and report DORA improvements, time-saved, incident reduction, and adoption. Make the value visible.
