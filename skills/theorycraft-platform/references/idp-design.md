# IDP Design Reference

## Portal / Catalogue Tool Comparison

| | Backstage | Port | Custom build |
|---|---|---|---|
| **Type** | Open source, self-hosted | SaaS | Whatever you build |
| **Time to value** | Weeks–months | Days–weeks | Months+ |
| **Customisation** | Very high (React plugins) | Medium (widgets, blueprints) | Unlimited |
| **Operational overhead** | High (you run it, update it, own plugins) | Low (SaaS) | High (you built it) |
| **Team size needed** | 1+ dedicated engineer to maintain | 0.5 engineer to configure | 2+ engineers to build |
| **Ecosystem** | Large plugin marketplace; active community | Growing; less mature | N/A |
| **Best for** | Large orgs (100+ engineers), high customisation needs, strong plugin requirements | Small–mid orgs (10–100 engineers), fast time to value, low ops overhead | Highly specific workflows, existing tooling investment, or platform-as-a-product for external devs |

### Backstage decision checklist
Only adopt Backstage if you can answer yes to all of these:
- [ ] You have at least one engineer willing to own it long-term
- [ ] You have real plugin requirements that Port can't meet
- [ ] You have 50+ engineers who will benefit from the catalogue
- [ ] You accept the maintenance burden is ongoing, not one-time

### Port decision checklist
Good fit if:
- [ ] Team is small (10–50 engineers) and wants fast time to value
- [ ] Customisation needs are moderate (entity types, actions, scorecards)
- [ ] Budget allows for SaaS pricing
- [ ] You want to focus on platform capabilities, not portal infrastructure

---

## Software Catalogue Design

The catalogue is only valuable if it's accurate and trusted. A stale catalogue is worse than no catalogue.

### Entity types to model
- **Service / Component:** a deployable unit. Owner, language, repo, API docs, dependencies, SLO status.
- **API:** the interface a service exposes. OpenAPI spec link, version, consumers.
- **System:** a collection of services that deliver a capability together.
- **Domain:** a business domain grouping systems.
- **Resource:** infrastructure resources (databases, queues, cloud accounts).

### Keeping the catalogue accurate
- **Source of truth in code:** `catalog-info.yaml` lives in each repo. Teams own their own entries. No central team maintaining a spreadsheet.
- **Automatic discovery:** GitHub integration scans repos for `catalog-info.yaml` — new services appear automatically on merge.
- **Staleness detection:** alert on services with no deployment in N days, or with owners who've left.
- **Scorecards / maturity:** use catalogue scorecards to track platform adoption (does the service have observability? Is it on the golden path? Does it have an owner?)

### Minimal catalog-info.yaml
```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: What this service does
  annotations:
    github.com/project-slug: org/my-service
    backstage.io/techdocs-ref: dir:.
  tags:
    - go
    - api
spec:
  type: service
  lifecycle: production
  owner: team-platform
  system: my-system
  providesApis:
    - my-service-api
  dependsOn:
    - resource:my-postgres-db
```

---

## Scaffolder / Golden Path Templates

The scaffolder (Backstage) or self-service actions (Port) are how teams create new services. The template defines the golden path.

### What a good service template includes
- Repo creation (from template with standard structure)
- CI/CD pipeline pre-configured (GitHub Actions workflow, Argo CD app registered)
- Dockerfile (multi-stage, non-root user, distroless base)
- Observability instrumentation (OTEL setup, structured logging config)
- Default health/readiness endpoints
- Secrets config wired to ESO / Key Vault
- README with getting-started instructions
- `catalog-info.yaml` pre-populated

### Template scope — one template per service archetype
- **HTTP API service** (most common): REST/gRPC, backed by database
- **Event consumer**: queue/stream consumer, no HTTP ingress
- **Scheduled job**: CronJob or KEDA-based scheduled task
- **Frontend**: SPA or SSR web app

Don't try to build one template that handles every case — it becomes a questionnaire nightmare. Separate templates are clearer.

---

## Self-Service Capability Roadmap

What teams should be able to do without a ticket, in rough priority order:

| Capability | Mechanism | Complexity |
|---|---|---|
| Create a new service | Scaffolder template | M |
| Provision a namespace | IDP action → Terraform/Crossplane | M |
| Add environment variables / secrets | ESO ExternalSecret template in scaffolder | S |
| Provision a managed database | IDP action → Terraform module | L |
| Provision a queue / topic | IDP action → Terraform module | M |
| Create a DNS entry | IDP action → ExternalDNS annotation | S |
| Request a TLS certificate | cert-manager annotation in Helm chart | S |
| Scale a deployment | IDP action → kubectl / HPA config | S |
| View service health and SLOs | Backstage TechDocs / Grafana embed | M |
| Rotate a secret | IDP action → Key Vault rotation trigger | M |
