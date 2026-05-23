# Kubernetes Security Reference

## RBAC

### Principles
- **Least privilege always.** No cluster-admin for workloads. No wildcard verbs or resources.
- **Namespace-scoped Roles over ClusterRoles** wherever possible — ClusterRoles apply across all namespaces.
- **ServiceAccount per workload** — don't share ServiceAccounts between different workloads.
- Audit ClusterRoleBindings regularly — they're the highest-risk RBAC objects.

### Common safe patterns
```yaml
# Read-only access to pods in a namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
```

### What to audit
- Any ClusterRoleBinding granting cluster-admin
- Any Role/ClusterRole with `*` verbs or `*` resources
- ServiceAccounts with automounted tokens that don't need API access (`automountServiceAccountToken: false`)
- Subjects bound to roles that include `secrets` get/list — this means they can read all secrets in scope

---

## Pod Security Standards

Three levels, enforced via namespace labels (built-in since K8s 1.25, replacing PodSecurityPolicy):

| Level | What it blocks | Use for |
|---|---|---|
| **privileged** | Nothing | System namespaces (kube-system), CNI, node agents |
| **baseline** | Privilege escalation, host namespaces, dangerous capabilities | Most workloads as a minimum |
| **restricted** | Everything in baseline + requires non-root, read-only root FS, drops all capabilities | New workloads, security-sensitive namespaces |

### Enforcement modes
- `enforce` — rejects non-compliant pods
- `audit` — logs violations, doesn't block
- `warn` — warns at admission, doesn't block

**Recommended approach:** set `audit` + `warn` for `restricted` cluster-wide, then progressively move namespaces to `enforce: restricted` as workloads are validated.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

Pod Security Standards should be enabled on all clusters regardless of which policy engine is also in use.

---

## Network Policies

### Default-deny pattern (apply to every namespace)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: my-namespace
spec:
  podSelector: {}
  policyTypes:
    - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: my-namespace
spec:
  podSelector: {}
  policyTypes:
    - Egress
```

### Allow DNS egress (required with default-deny egress)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: my-namespace
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
```

### CNI NetworkPolicy support
Not all CNIs support NetworkPolicy enforcement. Verify before relying on them:
- Azure CNI + Azure NPM: ✅
- Azure CNI Overlay + Cilium: ✅
- AWS VPC CNI alone: ❌ — requires Calico or Cilium overlay for enforcement
- GKE Dataplane V2 (Cilium-based): ✅
- Flannel: ❌ — no NetworkPolicy support
- Calico: ✅
- Cilium: ✅ — also supports L7 policies beyond standard NetworkPolicy

---

## Secrets Management

### Principles (consistent regardless of backend)
- Never store secrets in ConfigMaps or plaintext environment variables
- Never commit base64-encoded secrets to Git
- Use an external secrets store; sync to Kubernetes Secrets via an operator
- Rotate secrets automatically; don't rely on manual rotation

### Kubernetes-side bridge options

**External Secrets Operator (ESO):** creates Kubernetes Secrets from an external store on a refresh interval. Works with all env var and volume mount patterns. Easier to manage at scale.

**Secrets Store CSI Driver:** mounts secrets directly as volumes. Better for large secrets or high-rotation scenarios where avoiding pod restarts matters. More complex to operate.

ESO is the more common choice for most workloads. CSI Driver is useful when direct volume mounting or pod-restart-free rotation is required.

### Backend options — choose based on existing infrastructure
See `cncf-landscape.md` secrets section for full comparison. In summary:
- Azure/AKS → Azure Key Vault via ESO + Workload Identity
- AWS/EKS → AWS Secrets Manager via ESO + IRSA
- GCP/GKE → GCP Secret Manager via ESO + Workload Identity
- Multi-cloud or self-hosted → HashiCorp Vault or Infisical via ESO

---

## Admission Control / Policy Engines

Policy enforcement beyond Pod Security Standards requires an admission controller. Tool choice depends on team experience and policy complexity. See `cncf-landscape.md` for full comparison.

### Kyverno
Policy written as Kubernetes resources (YAML). Supports validate, mutate, generate, and image verification. Lower learning curve — no Rego knowledge required.

```yaml
# Example: require resource requests on all pods
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-requests
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-requests
      match:
        resources:
          kinds: ["Pod"]
      validate:
        message: "CPU and memory requests are required"
        pattern:
          spec:
            containers:
              - resources:
                  requests:
                    cpu: "?*"
                    memory: "?*"
```

### OPA Gatekeeper
Policies written in Rego. More powerful for complex constraint logic. Constraint templates can be reused across many policies. Higher learning curve.

```yaml
# ConstraintTemplate defines the policy logic in Rego
# Constraint instantiates it with parameters
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    labels: ["team"]
```

### Choosing between them
- New to policy enforcement, small-medium cluster, don't know Rego → Kyverno
- Large org, dedicated platform team, complex policy requirements, team knows Rego → OPA Gatekeeper
- Either way: layer on top of Pod Security Standards, not instead of them

---

## Image Supply Chain

Consistent regardless of policy engine:
- Scan images in CI (Trivy, Grype) — fail the build on CRITICAL CVEs before they reach the cluster
- Sign images with cosign (Sigstore) in CI
- Pin production image references to digests, not tags (`image: myapp@sha256:abc123`) — tags are mutable
- Enforce trusted registry allowlist via admission policy (Kyverno or Gatekeeper)
- Verify signatures at admission — Kyverno `verifyImages` rule, or Gatekeeper + Ratify
