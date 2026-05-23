# Platform Metrics Reference

## DORA Metrics Implementation Guide

### Data sources needed
| Metric | Primary source | Secondary source |
|---|---|---|
| Deployment frequency | CD pipeline events (Argo CD sync, GitHub Actions deploy job) | Git tags / releases |
| Lead time for changes | Git commit timestamp → deployment timestamp | PR creation → merge → deploy |
| Change failure rate | Incident tool (PagerDuty, Grafana IRM, Opsgenie) correlated with deployments | Rollback events in CD pipeline |
| MTTR | Incident tool: incident opened → resolved | Grafana IRM / Teams incident duration |

### Measuring lead time accurately
Lead time = time from first commit on a branch to that commit running in production.
- Not PR creation time (that excludes pre-PR work)
- Not merge time (that excludes deployment lag)
- Use: `git log` commit timestamp → deployment event timestamp in CD system

### DORA performance bands (2023 State of DevOps)
| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment frequency | Multiple/day | 1/week–1/day | 1/month–1/week | <1/month |
| Lead time | <1 hour | 1 day–1 week | 1 week–1 month | >1 month |
| Change failure rate | <5% | 5–10% | 10–15% | >15% |
| MTTR | <1 hour | <1 day | 1 day–1 week | >1 week |

### Baseline before you measure
Always capture a DORA baseline before starting platform improvements. Without it:
- You can't demonstrate value to leadership
- You can't prioritise which bottleneck to fix first
- You can't detect regressions

---

## SPACE Framework Implementation

### Satisfaction & wellbeing
- Quarterly developer survey (10 questions max, same questions each time for trend)
- Key questions: "I can focus on meaningful work", "I have the tools I need", "The deployment process doesn't slow me down"
- Net Promoter Score for the platform team: "How likely are you to recommend our platform to a colleague?"

### Performance
- Measure outcomes, not output. Deployments/day is output. Features shipped per sprint is closer to outcome.
- Defect escape rate (bugs found in prod vs in dev/staging)
- Customer-impacting incidents attributed to engineering changes

### Activity
- PRs merged per engineer per week (trend, not absolute — avoid gaming)
- Build success rate
- Deployment success rate (not failure rate — positive framing)

### Communication & collaboration
- PR review turnaround time (time from PR open to first review)
- PR cycle time (first commit to merge)
- Number of review rounds per PR (proxy for clarity of requirements)

### Efficiency & flow
- Context switching incidents (number of P1/P2 incidents per engineer per month)
- Unplanned work ratio (% of sprint spent on unplanned work)
- CI pipeline duration (P50 and P95 — long pipelines kill flow)
- Build queue wait time (self-hosted runner capacity)

---

## Platform SLO Templates

Define SLOs with the teams that consume the platform, not unilaterally.

### CI/CD pipeline SLOs
| SLO | Target | Measurement |
|---|---|---|
| Pipeline success rate | >98% of runs complete without infrastructure failure | CD platform events, excluding user code failures |
| Pipeline P95 duration | <10 minutes for standard service | Pipeline run duration metrics |
| Deployment success rate | >99.5% of deploys reach target environment | Argo CD sync success events |
| GitOps reconciliation lag | <2 minutes from commit to sync initiated | Argo CD sync timestamp vs Git commit timestamp |

### IDP availability SLOs
| SLO | Target | Measurement |
|---|---|---|
| Portal availability | 99.9% (43 min/month downtime budget) | Synthetic uptime monitoring |
| Scaffolder success rate | >99% of template instantiations succeed | Backstage/Port action completion events |
| Self-service action latency | P95 <30s for namespace/secret provisioning | Action completion timestamps |

### Toil measurement
Toil = manual, repetitive, automatable work that scales with load rather than with value delivered.

Track per platform engineer per week:
- Time spent on manual infra requests (tickets)
- Time spent on manual deployments or rollbacks
- Time spent on repeated oncall actions that should be automated

**Target:** toil <50% of platform team time. If above this, the platform is consuming itself.

---

## Reporting to Leadership

Platform teams often struggle to demonstrate value. Use this framing:

### Before/after metrics
For every platform capability shipped, report:
- Metric before (baseline)
- Metric after (N weeks post-adoption)
- Time saved per team per week / per deployment

### Adoption metrics
- % of teams on golden path vs rolling their own
- Number of services in the catalogue
- Self-service request volume (proxy for toil avoided)

### Reliability contribution
- Platform-caused incidents as % of total incidents (target: <5%)
- Platform MTTR (time to restore a platform service)

### Developer satisfaction trend
- Quarterly NPS trend for the platform team
- Survey question trend lines (same questions, same scale, every quarter)
