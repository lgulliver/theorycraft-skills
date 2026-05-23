# theorycraft

A suite of Claude skills for cloud architecture, platform engineering, and Kubernetes. Drop them into Claude and get a senior architect in your pocket — one that challenges your assumptions, knows the CNCF landscape, and produces real documentation.

---

## What is this?

theorycraft is a collection of installable Claude skills. Each skill gives Claude deep, structured knowledge in a specific domain and a consistent approach to using it — Socratic Q&A before recommendations, opinionated outputs over option menus, and real artefacts (design docs, diagrams, cost estimates) rather than generic advice.

The skills are designed to work together. `theorycraft-architecture` is the front door — it runs discovery and then draws on the provider and stack skills to produce a complete design. But every skill also works standalone for targeted questions.

---

## Installation

1. Download the `.skill` file for the skill you want (or the full `theorycraft-suite.zip` bundle) from [Releases](../../releases)
2. In Claude, go to **Settings → Skills**
3. Upload the `.skill` file
4. The skill is now active in your conversations

For the full suite, download `theorycraft-suite.zip` from the latest release, extract it, and install each `.skill` file individually.

> The `.skill` files and suite bundle are built automatically by GitHub Actions on each release. You never need to build them yourself.

---

## Skill Catalogue

| Skill | What it does | Status |
|---|---|---|
| [`theorycraft-architecture`](skills/theorycraft-architecture/) | Front door for the suite. Socratic Q&A to challenge your idea, then produces architecture design docs, diagrams, cost analysis, and T-shirt effort estimates. | ✅ Full |
| [`theorycraft-cloud`](skills/theorycraft-cloud/) | Cloud architecture analysis engine. Recommendations, WAF alignment, FinOps, security threat modelling, and multi-cloud trade-offs. Provider-agnostic. | ✅ Full |
| [`theorycraft-kubernetes`](skills/theorycraft-kubernetes/) | Full K8s lifecycle — cluster design, workload patterns, security, CNCF tool selection, observability, operations, and troubleshooting. | ✅ Full |
| [`theorycraft-platform`](skills/theorycraft-platform/) | Platform engineering. IDP design (Backstage vs Port), CI/CD pipelines, golden paths, DORA/SPACE metrics, Team Topologies, and platform SLOs. | ✅ Full |
| [`theorycraft-azure`](skills/theorycraft-azure/) | Azure-specific depth. Service selection, Azure WAF, networking, security (Entra ID, Defender, Policy), FinOps in GBP, and Mermaid/SVG diagrams. | 🟡 Partial |
| [`theorycraft-aws`](skills/theorycraft-aws/) | AWS-specific depth. Service selection, six-pillar WAF, IAM/VPC design, CDK/Terraform guidance, and Mermaid/SVG diagrams. | 🟡 Partial |
| [`theorycraft-gcp`](skills/theorycraft-gcp/) | GCP-specific depth. Service selection, GCP Architecture Framework, Shared VPC, BigQuery/Spanner guidance, and Mermaid/SVG diagrams. | 🟡 Partial |
| [`theorycraft-serverless`](skills/theorycraft-serverless/) | Serverless architecture. FaaS selection, cold start strategy, choreography vs orchestration, DLQ patterns, and consumption billing FinOps. | 🟡 Partial |
| [`theorycraft-iaas`](skills/theorycraft-iaas/) | IaaS / VM-based architectures. VM sizing, HA design, Windows workloads, lift-and-shift migration patterns. | 🟡 Partial |
| [`theorycraft-paas`](skills/theorycraft-paas/) | PaaS and managed services. Abstraction level selection, managed database/queue/platform choices, VNet integration, PaaS FinOps. | 🟡 Partial |
| [`theorycraft-containers`](skills/theorycraft-containers/) | Container and Kubernetes architecture diagrams. Topology, GitOps pipeline, service mesh, and multi-cluster visualisations. | 🟡 Partial |

**Status key:**
- ✅ **Full** — SKILL.md + complete reference files
- 🟡 **Partial** — SKILL.md with limited or no reference files; core skill works but depth is thinner

Partial skills are great candidates for contribution — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## How the skills relate

```
theorycraft-architecture          ← start here for greenfield design
        │
        ├── theorycraft-cloud     ← cloud-layer analysis (provider-agnostic)
        │         │
        │         ├── theorycraft-azure      ← Azure-specific depth + diagrams
        │         ├── theorycraft-aws        ← AWS-specific depth + diagrams
        │         └── theorycraft-gcp        ← GCP-specific depth + diagrams
        │
        ├── theorycraft-kubernetes           ← K8s full lifecycle
        ├── theorycraft-platform             ← platform engineering
        │
        └── Stack skills (extend theorycraft-cloud)
              ├── theorycraft-serverless
              ├── theorycraft-iaas
              ├── theorycraft-paas
              └── theorycraft-containers
```

Provider skills (azure, aws, gcp) and stack skills (serverless, iaas, paas, containers) extend `theorycraft-cloud` — they assume the cloud-layer analysis has been done and add provider/stack-specific depth and diagrams on top.

`theorycraft-kubernetes` and `theorycraft-platform` are standalone — they don't depend on `theorycraft-cloud`.

---

## Example usage

### Greenfield architecture session

```
You: I want to build a multi-tenant SaaS platform for contact centres.

Claude: [theorycraft-architecture triggers]
        This sounds like a complex idea — I'm going to push on it hard
        before we get to architecture. Let's go.

        Question 1: What problem does this solve that existing CCaaS 
        platforms don't? What's the nearest competitor and why doesn't 
        it work for your use case?
        
        [~20 rounds of Socratic Q&A]
        
        [Produces: design doc, C4 diagrams, cost breakdown, effort estimates]
```

### Targeted cloud question

```
You: We're running out of Azure VM capacity — should we burst to AWS?

Claude: [theorycraft-cloud triggers, draws on theorycraft-aws]
        [Produces: multi-cloud recommendation, networking design, 
         cost comparison in GBP, implementation roadmap]
```

### Kubernetes operational question

```
You: My pod is stuck in CrashLoopBackOff after a deploy.

Claude: [theorycraft-kubernetes triggers]
        Let's diagnose this systematically.
        kubectl logs <pod-name> --previous
        [Systematic troubleshooting with exact commands]
```

---

## Repo structure

```
theorycraft/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── skill_request.md
│   ├── pull_request_template.md
│   └── workflows/
│       └── build-skills.yml
├── skills/
│   ├── theorycraft-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── question-bank.md
│   │       ├── effort-calibration.md
│   │       └── document-templates.md
│   ├── theorycraft-cloud/
│   │   ├── SKILL.md
│   │   └── references/
│   └── ... (one directory per skill)
└── scripts/
    └── package.py
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version:

- **Bug reports and content fixes:** open an issue or PR directly
- **New reference files for partial skills:** most welcome — this is where the most useful contributions land
- **New skills:** open an issue to discuss before building
- **Company-specific or proprietary content:** keep it in your own fork

---

## Licence

Apache 2.0. See [LICENSE](LICENSE).
