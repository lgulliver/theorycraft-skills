# CI/CD Patterns Reference

## Pipeline Platform Selection

| | GitHub Actions | Tekton | Argo Workflows | Jenkins |
|---|---|---|---|---|
| **Type** | SaaS / self-hosted runners | K8s-native CRDs | K8s-native DAGs | Self-hosted |
| **Ease of use** | High | Medium | Medium | Low |
| **K8s integration** | Good (via actions) | Native | Native | Plugin-based |
| **Ecosystem** | Excellent (GitHub marketplace) | Good (Tekton Hub) | Good | Large but legacy |
| **Cost** | GitHub minutes (free tier + paid); self-hosted runners for K8s | Free (runs on your cluster) | Free (runs on your cluster) | Free but ops overhead |
| **Recommended for** | Default choice for most teams on GitHub | K8s-native orgs that want pipeline-as-code in the cluster | Complex DAG pipelines, ML workflows, fan-out/fan-in | Legacy — migrate away |

**Recommendation:** GitHub Actions is the right default unless the team has a specific K8s-native requirement. It has the best ecosystem, lowest friction, and easiest onboarding.

---

## GitOps Delivery: Argo CD vs Flux

| | Argo CD | Flux |
|---|---|---|
| **UI** | Strong — visual app health, sync status, diff view | Minimal — primarily CLI/API |
| **Multi-tenancy** | Strong RBAC, AppProject isolation | Namespace-based, simpler |
| **Application model** | `Application` / `ApplicationSet` CRDs | `Kustomization` / `HelmRelease` CRDs |
| **Notification** | Argo CD Notifications (webhooks, Slack, Teams) | Flux Notification Controller |
| **Best for** | Teams that want visibility and RBAC; multi-team platforms | Teams that want pure GitOps with minimal UI; simpler setups |
| **Recommendation** | Default for most platform teams | Good for smaller, more homogeneous setups |

### Argo CD multi-team pattern
```yaml
# AppProject per team — restricts what they can deploy and where
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-a
  namespace: argocd
spec:
  sourceRepos:
    - 'https://github.com/myorg/team-a-*'
  destinations:
    - namespace: team-a-*
      server: https://kubernetes.default.svc
  clusterResourceWhitelist: []  # no cluster-level resources
```

---

## Golden Path Pipeline Structure

### GitHub Actions — standard service pipeline
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint & test
        run: make test

      - name: Security scan (SAST)
        uses: github/codeql-action/analyze@v3

      - name: Secret scan
        uses: gitleaks/gitleaks-action@v2

      - name: Build image
        run: docker build -t ghcr.io/myorg/myapp:${{ github.sha }} .

      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/myorg/myapp:${{ github.sha }}
          exit-code: '1'
          severity: 'CRITICAL'

      - name: Sign image
        uses: sigstore/cosign-installer@main
        # cosign sign --key env://COSIGN_KEY ghcr.io/myorg/myapp:${{ github.sha }}

      - name: Push image
        run: docker push ghcr.io/myorg/myapp:${{ github.sha }}

      - name: Update GitOps repo
        # Update image tag in kustomize overlay or Helm values
        run: |
          git clone https://github.com/myorg/gitops-repo
          cd gitops-repo
          yq -i '.image.tag = "${{ github.sha }}"' apps/myapp/values.yaml
          git commit -am "chore: update myapp to ${{ github.sha }}"
          git push
```

---

## Progressive Delivery Patterns

### When to use each
| Pattern | Use when | Don't use when |
|---|---|---|
| **Blue/green** | Zero-downtime deployment; easy rollback; stateless services | Stateful services with data migrations; high infra cost concern |
| **Canary** | Validating changes on a subset of traffic before full rollout; catching production-specific issues | Very low traffic (canary sample too small to be meaningful) |
| **Feature flags** | Decouple deploy from release; A/B testing; dark launches | Simple one-off deploys with no rollback risk |
| **Ring deployment** | Staged rollout to internal → early adopters → general availability | Simple single-tenant apps |

### Canary with Argo Rollouts
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-service
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10   # 10% traffic to new version
        - pause: {duration: 5m}
        - analysis:       # automated analysis gate
            templates:
              - templateName: success-rate
        - setWeight: 50
        - pause: {duration: 5m}
        - setWeight: 100
```

---

## Pipeline Security Checklist

- [ ] Branch protection: require PR reviews, no direct push to main
- [ ] Signed commits enforced (optional but recommended)
- [ ] SAST in CI (CodeQL for GitHub, Semgrep for polyglot)
- [ ] Secret scanning in CI (Gitleaks) + GitHub secret scanning enabled
- [ ] Container image scanning (Trivy) — fail on CRITICAL CVEs
- [ ] SBOM generation (Syft) on every build
- [ ] Image signing (cosign) with admission policy enforcement
- [ ] No long-lived credentials in CI secrets — use OIDC federation (GitHub Actions → cloud provider)
- [ ] Least-privilege pipeline permissions (`permissions:` block in GitHub Actions)
- [ ] Dependency scanning (Dependabot or Renovate)
