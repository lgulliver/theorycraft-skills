# Security & Threat Modelling Reference

## STRIDE Applied to Cloud Architecture

Use STRIDE as a lens when reviewing an architecture:

| Threat | Cloud Manifestation | Key Controls |
|--------|-------------------|--------------|
| **Spoofing** | Impersonation of services/users, stolen credentials, JWT forgery | Managed identity, Workload Identity, short-lived tokens, MFA, OIDC federation |
| **Tampering** | Unauthorised data modification, man-in-the-middle, config drift | TLS everywhere, integrity checksums, IaC policy enforcement, signed artifacts |
| **Repudiation** | No audit trail, log deletion, unsigned actions | Immutable audit logs, CloudTrail/Activity Log, signed commits, non-repudiation tokens |
| **Information Disclosure** | Data exfiltration, over-permissive storage, misconfigured APIs | Least-privilege IAM, private endpoints, data classification, encryption at rest |
| **Denial of Service** | API abuse, cost-based DoS, resource exhaustion | Rate limiting, WAF, autoscaling limits, budget alerts, DDoS protection |
| **Elevation of Privilege** | IAM misconfiguration, SSRF, container escape, supply chain | Least-privilege roles, no wildcard IAM, admission controllers, image scanning |

---

## Identity & Access Patterns

### Preferred patterns (in priority order):
1. **Workload Identity / Managed Identity** — no secret to rotate, no credential sprawl. Gold standard for service-to-service auth in cloud.
2. **OIDC Federation** — for CI/CD (GitHub Actions → cloud, no long-lived keys in secrets)
3. **Short-lived tokens** — if secrets are unavoidable, generate at runtime via a secrets engine (Vault, Azure Key Vault + ESO)
4. **Service account keys** — last resort, with rotation policy enforced

### Azure specifics:
- Use **User-Assigned Managed Identity (UAMI)** for AKS workloads via Workload Identity Federation
- **Azure RBAC over legacy ABAC** — use built-in roles at resource group scope; avoid Owner/Contributor at subscription scope
- **PIM (Privileged Identity Management)** for just-in-time admin access
- **Conditional Access** for human identities — enforce MFA, device compliance

### Kubernetes specifics:
- **RBAC**: least-privilege ClusterRoles/Roles; never use cluster-admin for workloads
- **Network Policies**: default-deny, then allow explicitly
- **Pod Security Standards**: enforce `restricted` or `baseline` via admission controller (OPA Gatekeeper, Kyverno)
- **Image signing**: cosign + policy enforcement for supply chain security
- **Secrets**: never in env vars or ConfigMaps as plaintext; use ESO (External Secrets Operator) pulling from Key Vault/Secrets Manager

---

## Secrets Management

### Don't do:
- Hardcoded secrets in code or Docker images
- Secrets in environment variables committed to Git
- Long-lived service account keys without rotation
- Shared secrets across environments

### Do:
- **Azure**: Key Vault + ESO for Kubernetes; Key Vault references for App Service / Azure Functions
- **AWS**: Secrets Manager or Parameter Store (SSM) + IAM for pod identity
- **GCP**: Secret Manager + Workload Identity
- **Rotation**: automate rotation; use versioned secrets; test rotation before you need it

---

## Network Security

### Core principles:
- **Private by default**: databases, message brokers, internal APIs should never be publicly accessible
- **Private endpoints / VNet integration**: for PaaS services (Azure Database, Storage, Key Vault)
- **Ingress only at the edge**: one entry point (Envoy Gateway, AGIC, ALB, Cloud Load Balancing) with WAF attached
- **East-west controls**: service mesh (Istio, Linkerd) for mTLS between services if threat model warrants it; NetworkPolicy as minimum

### Egress control:
- Route egress through a firewall/NAT with allowlisted destinations for sensitive workloads
- Egress filtering catches compromised workloads calling back to C2
- Watch egress costs: Azure NAT Gateway, AWS NAT Gateway, GCP Cloud NAT are expensive at volume

---

## Compliance Quick Reference

| Framework | Key Cloud Controls |
|-----------|-------------------|
| **ISO 27001** | Asset inventory, access control (A.9), cryptography (A.10), logging/monitoring (A.12), supplier relationships (A.15) |
| **SOC 2 Type II** | Continuous monitoring, change management, access reviews, incident response evidence |
| **GDPR / UK GDPR** | Data residency (EU/UK), data subject rights, breach notification <72h, ROPA, DPA with processors |
| **PCI DSS** | Network segmentation, no cardholder data in logs, strong crypto, quarterly scans |
| **FedRAMP** | US Gov specific — NIST 800-53 controls, authorised cloud regions, continuous monitoring |

For **UK GDPR specifically**: data residency matters. Azure UK South / UK West, AWS eu-west-2, GCP europe-west2 for UK-resident data. Cross-border transfers require SCCs or adequacy decisions.

---

## Top Anti-Patterns in Cloud Security

1. **Overly permissive IAM** — `*` actions or `*` resources. Audit with IAM Access Analyzer / Entra ID Access Reviews.
2. **Public storage buckets / blob containers** — check for public ACLs on every deployment. Enforce via policy.
3. **Secrets in Git** — use pre-commit hooks (gitleaks, truffleHog), secret scanning in CI, and rotate anything found immediately.
4. **No network segmentation** — flat network where a compromised pod can reach everything. Network Policies and private endpoints are non-negotiable.
5. **Shared environments** — dev workloads in prod subscriptions/accounts. Separate blast radius with separate accounts/subscriptions.
6. **No egress monitoring** — you won't know you've been breached until it's too late. Log and alert on unexpected egress destinations.
7. **Missing audit logs** — ensure Azure Activity Log / CloudTrail / Cloud Audit Logs are on, retained, and tamper-resistant.
