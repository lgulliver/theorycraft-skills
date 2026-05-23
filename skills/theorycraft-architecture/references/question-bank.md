# Extended Question Bank

## Regulated Industries

### Financial services / fintech
- What financial regulations apply? (FCA, PSD2, Basel III, MiFID II, DORA)
- Is this handling payments? If so, is PCI-DSS in scope?
- What are the audit trail requirements — who needs to see what happened and for how long?
- Is there a requirement for operational resilience testing (DORA Article 25)?
- Do regulators need access to data or systems?

### Healthcare
- Is this handling patient data? Which regulation? (UK GDPR + Data Security Standard, US HIPAA)
- What is the data retention requirement for clinical records?
- Is clinical decision support involved? If so, is this a medical device under MDR/FDA?
- What are the integration requirements with existing clinical systems (HL7, FHIR)?

### Contact centre / CCaaS
- What telephony infrastructure is involved? (SIP, WebRTC, SBC)
- What call recording and retention obligations apply? (FCA, GDPR)
- Is AI/ML used on voice data? What are the consent and data residency implications?
- What are the concurrency requirements? (concurrent calls, concurrent agents)
- What's the failover requirement if the platform becomes unavailable mid-call?

### Public sector / government
- What security classification does the data carry? (OFFICIAL, OFFICIAL-SENSITIVE, SECRET)
- Is Cyber Essentials or Cyber Essentials Plus certification required?
- Are there G-Cloud / Digital Marketplace procurement constraints?
- What are the accessibility requirements? (WCAG 2.1 AA minimum for public-facing)

---

## Multi-Tenant SaaS

- How is tenant isolation implemented? (Row-level security, schema-per-tenant, database-per-tenant, cluster-per-tenant)
- What is the tenant onboarding flow — self-serve, sales-assisted, or automated provisioning?
- Are there tenant-specific customisations to the data model or business logic?
- What happens when one tenant's workload affects another? (noisy neighbour — what's the SLA impact?)
- How are tenant-specific secrets and credentials managed?
- Is there a white-labelling requirement? (Custom domains, custom branding, custom email from)
- What are the data portability requirements? (Can a tenant export all their data? In what format?)
- What's the largest tenant's data volume vs the median tenant?

---

## Real-Time Systems

- Define "real-time" for this system — sub-10ms, sub-100ms, sub-1s?
- What happens when the real-time constraint is violated — degraded experience or hard failure?
- Is this real-time processing or real-time delivery? (Different problems)
- What's the source of events and what's the expected event rate? (events/sec at p50 and p99)
- Is ordering of events important? Exactly-once processing required?
- What's the acceptable data loss window if the system fails? (Helps size buffer/queue depth)

---

## ML / AI Systems

- Is this training, inference, or both?
- What are the model serving latency requirements? (Batch offline, near-real-time, real-time interactive)
- Who produces the models — internal data science team, external vendor, foundation model API?
- What's the data pipeline — where does training data come from and how is it labelled?
- What are the model drift detection and retraining requirements?
- Is explainability required? (Regulated industries often require model decisions to be explainable)
- What are the GPU/accelerator requirements and budget?
- Is there a model registry and versioning requirement?

---

## Migration Projects

- What is the source system — on-prem, another cloud, legacy platform?
- What is the migration strategy — lift-and-shift, replatform, or rearchitect?
- What is the acceptable downtime window for cutover?
- Is there a parallel-run requirement? (Both systems live simultaneously for a period)
- What's the data migration strategy — big-bang or phased by tenant/data type?
- Are there integrations that must be migrated or updated at the same time?
- What's the rollback plan if migration fails?
- Are there licensing implications of moving from the source platform?

---

## Greenfield SaaS / Startup Context

- What's the funding situation — bootstrapped, seed, Series A+? This affects build vs buy decisions.
- What's the time-to-first-customer target?
- Is this B2B or B2C? (B2B usually needs SSO, audit logs, admin consoles earlier than expected)
- What's the growth model — viral, sales-led, product-led?
- Which features are table stakes vs differentiators? (Build differentiators, buy table stakes)
- What's the team's runway and when does this need to be revenue-generating?

---

## Integration-Heavy Systems

- How many external systems does this integrate with? List them.
- For each integration: sync or async? Who owns the contract? What's the SLA of the dependency?
- What happens when an integration is unavailable? Degrade gracefully or hard fail?
- Are there webhook inbound patterns? How are they secured?
- Is there an existing API gateway or integration platform to use/extend?
- What are the rate limits on critical external dependencies?

---

## Follow-up Probes (use when answers are vague)

When a user gives a vague answer, use these follow-up probes:

**"We need it to be scalable"** →
- What does scalable mean here — 10× current load, 100×, or genuinely unknown?
- What's the current load baseline we're scaling from?
- Is this scale a near-term requirement or a future hedge?

**"It needs to be secure"** →
- Secure against what specific threats?
- Is there a compliance framework defining the security controls, or is this engineering judgement?
- What's the consequence of a breach — financial, reputational, regulatory?

**"We want high availability"** →
- What's the acceptable downtime per month? (99.9% = 43min/mo, 99.99% = 4.3min/mo)
- Is this an SLA commitment to customers, or an internal target?
- What's the RTO (how fast to recover) and RPO (how much data loss is acceptable)?

**"We'll figure out the data model later"** →
- The data model is one of the hardest things to change later — let's spend 5 minutes on it now. What are the 3–5 core entities this system manages?

**"We don't have a budget yet"** →
- That's fine — what's the order of magnitude? £1k/mo, £10k/mo, £100k/mo? This shapes almost every technology decision.

**"The team is small"** →
- How many engineers, and what's the split between frontend, backend, and infra?
- Is there a dedicated platform/DevOps capability or does the team own everything?
