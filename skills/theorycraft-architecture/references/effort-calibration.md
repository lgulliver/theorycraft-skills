# Effort Estimation & Calibration

## T-Shirt Size Definitions

| Size | Day range | What it feels like |
|---|---|---|
| **S** | 1–5 days | One engineer, one focused sprint. Well-understood problem, clear scope. |
| **M** | 5–15 days | One or two engineers, 2–3 weeks. Standard pattern, some complexity. |
| **L** | 15–40 days | Small team, 1–2 months. Multiple moving parts, real integration work. |
| **XL** | 40–90 days | Team effort, 2–4 months. Significant scope, non-trivial architecture. |
| **XXL** | 90+ days | Flag this — consider phasing. If something is XXL, it probably contains several L/XL problems. |

---

## Baseline Phase Estimates by System Type

Assumes 2 experienced engineers unless stated.

| System type | Design | Foundation | Core build | Hardening | Test & release | Total |
|---|---|---|---|---|---|---|
| Simple CRUD API + DB | S (2d) | S (3d) | M (10d) | M (8d) | S (4d) | **M–L (27d)** |
| SaaS web app (single tenant) | S (3d) | M (7d) | L (20d) | M (12d) | M (8d) | **L (50d)** |
| SaaS web app (multi-tenant) | M (8d) | M (12d) | L (35d) | L (18d) | M (8d) | **XL (81d)** |
| Event-driven microservice | S (3d) | M (6d) | M (15d) | M (8d) | M (6d) | **L (38d)** |
| Data pipeline (batch) | S (3d) | M (5d) | M (15d) | M (8d) | M (8d) | **L (39d)** |
| Data pipeline (streaming) | M (7d) | M (8d) | L (22d) | M (12d) | M (8d) | **XL (57d)** |
| ML inference service | M (8d) | M (8d) | L (22d) | M (12d) | L (10d) | **XL (60d)** |
| Internal platform / IDP | L (12d) | L (16d) | XL (45d) | L (18d) | M (8d) | **XL (99d)** |
| CCaaS / telephony integration | M (8d) | M (12d) | L (35d) | L (18d) | L (12d) | **XL (85d)** |
| Lift-and-shift migration (5–10 services) | M (8d) | M (8d) | L (28d) | M (12d) | L (12d) | **XL (68d)** |

---

## Complexity Multipliers

Apply to the baseline total. Multipliers are multiplicative.

| Factor | Condition | Multiplier |
|---|---|---|
| **Compliance** | ISO 27001, SOC 2, PCI-DSS in scope | ×1.3–1.5 |
| **Regulated data** | PII, health, financial data with audit trail | ×1.2–1.4 |
| **Multi-region** | Active-active or active-passive multi-region | ×1.3–1.6 |
| **Multi-tenant isolation** | Database-per-tenant or cluster-per-tenant | ×1.3–1.5 |
| **Legacy integration** | Poorly documented or unstable external system | ×1.2–1.4 per integration |
| **New technology** | Team unfamiliar with a core technology choice | ×1.3–1.5 |
| **Real-time constraints** | Sub-100ms P99 latency required | ×1.2–1.3 |
| **High concurrency** | >10k concurrent users or >10k events/sec | ×1.2–1.4 |
| **Greenfield infra** | No existing CI/CD, IaC, cloud accounts | ×1.1–1.2 (Foundation phase only) |
| **Due diligence / audit** | Audit-ready documentation required throughout | ×1.1–1.2 |

---

## Team Size Adjustments

All baselines assume 2 experienced engineers.

| Team size | Adjustment | Notes |
|---|---|---|
| 1 engineer | ×1.7–2.0 | No parallelism, context switching overhead |
| 2 engineers | ×1.0 (baseline) | Optimal for most early-stage builds |
| 3 engineers | ×0.75–0.85 | Some parallelism; coordination starts to matter |
| 4 engineers | ×0.65–0.75 | Good for parallel workstreams; needs clear ownership |
| 5+ engineers | ×0.5–0.65 | Diminishing returns; coordination cost is real |
| Junior-heavy team | +30–50% | Mentoring, review, slower ramp on unfamiliar tech |

**Brook's Law reminder:** adding engineers to a late project makes it later. These adjustments apply to greenfield estimates, not recovery estimates.

---

## Confidence Calibration

| Confidence | Range | When to use |
|---|---|---|
| **High** | ±20% | Known technology, clear scope, experienced team, no significant external dependencies |
| **Medium** | ±40% | One or two meaningful unknowns, some external dependencies, standard tech applied to novel problem |
| **Low** | ±60%+  | Novel technology, poorly defined scope, critical external unknowns, data migration involved |

Low confidence with honest reasoning is more useful than false precision. Always state it.

---

## Common Scope Creep Patterns

Flag these proactively when they're likely for the architecture in question:

| Pattern | Typical impact | Prevention |
|---|---|---|
| Admin console (B2B SaaS) | +M (8–15d) | Scope separately from day one; always underestimated |
| Reporting / analytics | +M–L (8–25d) | Treat as a separate phase; never "just add it" |
| SSO / SAML (enterprise B2B) | +S–M (5–10d) | Often a surprise requirement; build auth layer to support it early |
| Audit logging (regulated) | +S–M (5–10d) | Retrofitting is expensive; bake into data model early |
| White-labelling | +M (8–15d) | Requires design system and theming infrastructure |
| Mobile app (when web was assumed) | +XL (50–80d) | Separate project; separate estimate |
| Offline / sync | +L (20–40d) | Conflict resolution is hard; rarely scoped accurately |
| i18n / l10n | +M (8–20d) if retrofitted | Build in from start if needed at all |

---

## Technology Risk Flags

Call these out explicitly when they appear in the recommended architecture:

| Technology / pattern | Risk | Why |
|---|---|---|
| Event sourcing | 🔴 High | Harder than it looks; retrofitting is very expensive; over-applied |
| CQRS | 🟡 Medium-High | Justified only at significant scale; often adds complexity without benefit |
| Service mesh (Istio) | 🟡 Medium | Certificate management, debugging complexity, operational overhead |
| Multi-region active-active | 🔴 High | Distributed systems consistency is fundamentally hard |
| Custom ML training pipeline | 🔴 High | Data quality, labelling, drift — ongoing investment, not a one-time build |
| Real-time streaming at scale | 🟡 Medium-High | Ordering guarantees and consumer lag are subtle production problems |
| Zero-downtime DB migrations | 🟡 Medium | Requires discipline; expand-contract pattern must be embedded in workflow |
| WebRTC at scale | 🔴 High | TURN/STUN, signalling, codec negotiation, NAT traversal — all complex |
| Blockchain (non-crypto) | 🔴 Very High | Almost always the wrong tool; challenge the requirement before designing anything |
