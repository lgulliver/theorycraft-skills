# Operations & Troubleshooting Reference

## Common Failure Mode Catalogue

### Pod stuck in Pending
**Causes (in order of frequency):**
1. Insufficient cluster resources (CPU/memory) — no node can fit the pod
2. Node selector / affinity / taint not matching any node
3. PVC can't be provisioned or bound (storage class issue, AZ mismatch)
4. Namespace ResourceQuota exhausted
5. Admission controller (Kyverno/Gatekeeper) rejecting the pod

**Diagnose:**
```bash
kubectl describe pod <pod-name> -n <namespace>
# Look at Events section — the reason is almost always there

kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check node resource headroom
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check quota
kubectl describe resourcequota -n <namespace>
```

---

### CrashLoopBackOff
**Causes:**
1. Application error on startup (missing env var, bad config, failed DB connection)
2. OOMKill — memory limit too low
3. Liveness probe failing before app is ready
4. Missing secret or ConfigMap
5. Image pull error (wrong tag, no registry access)

**Diagnose:**
```bash
# Get last logs before crash
kubectl logs <pod-name> -n <namespace> --previous

# Check exit code
kubectl describe pod <pod-name> -n <namespace>
# Look for: Last State, Exit Code, Reason

# OOMKill check
kubectl describe pod <pod-name> | grep -i oom
# Or: Exit Code 137 = OOMKill
```

---

### OOMKill
- Exit code 137. Memory limit exceeded.
- Short-term fix: increase memory limit.
- Root cause: profile memory usage with Pyroscope or heap dumps; is there a memory leak, or is the limit just wrong?
- Check VPA recommendations: `kubectl describe vpa <name> -n <namespace>`

---

### ImagePullBackOff / ErrImagePull
```bash
kubectl describe pod <pod-name> -n <namespace>
# Events will show the registry error

# Common causes:
# 1. Image tag doesn't exist
# 2. Private registry — imagePullSecret not configured or expired
# 3. Registry rate limit (Docker Hub)
# 4. Network policy blocking egress to registry
```

---

### Pod stuck in Terminating
```bash
# Usually a finalizer preventing deletion
kubectl get pod <pod-name> -n <namespace> -o json | jq '.metadata.finalizers'

# Force delete (use as last resort — can leave orphaned resources)
kubectl delete pod <pod-name> -n <namespace> --grace-period=0 --force
```

---

### Envoy Gateway / HTTPRoute not routing

This is one of the trickier failure modes because the error is often silent — requests hit Envoy and get a `direct_response` (404 or 500) with no upstream hit.

```bash
# Check HTTPRoute status
kubectl describe httproute <route-name> -n <namespace>
# Look for: Accepted, ResolvedRefs conditions

# Check Gateway status
kubectl describe gateway <gateway-name> -n <namespace>

# Check Envoy Gateway controller logs
kubectl logs -n envoy-gateway-system -l app=envoy-gateway

# Check Envoy proxy pod logs (the actual data plane)
kubectl logs -n <gateway-namespace> <envoy-pod-name>
# Look for: direct_response, no_route, no_cluster
```

**Common causes:**
1. HTTPRoute `parentRef` pointing to wrong Gateway name/namespace
2. Service `port` in HTTPRoute backendRef doesn't match Service spec
3. Namespace label missing — Gateway doesn't allow routes from that namespace (`allowedRoutes` policy)
4. HTTPRoute in wrong namespace — check `allowedRoutes.namespaces` on Gateway

---

### NATS JetStream consumer lag

```bash
# Check stream and consumer status via NATS CLI
nats stream info <stream-name>
nats consumer info <stream-name> <consumer-name>

# Or via kubectl exec into a pod with nats CLI
kubectl exec -it <pod> -n <namespace> -- nats consumer info <stream> <consumer>

# Look for: NumPending (unprocessed messages), NumAckPending (in-flight)
```

**Common causes:**
1. Consumer processing too slow — scale out consumer pods (KEDA scaler on NumPending)
2. Consumer stuck on a poison message — check DeliverPolicy, MaxDeliver, and whether messages are landing in dead-letter
3. Stream storage full — check storage quota and disk usage

---

### ESO (External Secrets) sync failure

```bash
# Check ExternalSecret status
kubectl describe externalsecret <name> -n <namespace>
# Look for: Ready condition, SecretSyncedError

# Common causes:
# 1. Workload Identity / ServiceAccount federation misconfigured
# 2. UAMI doesn't have Key Vault Secrets User role on the vault
# 3. Secret name in vault doesn't match remoteRef.key
# 4. ClusterSecretStore misconfigured (wrong vault URL, wrong auth)

kubectl describe clustersecretstore <store-name>
```

---

## Upgrade Strategy

### AKS upgrade approach (recommended: node pool rotation)

1. **Check available versions:** `az aks get-upgrades -g <rg> -n <cluster>`
2. **Upgrade control plane first:** `az aks upgrade -g <rg> -n <cluster> --kubernetes-version <version> --control-plane-only`
3. **Upgrade node pools one at a time:**
   - For each node pool: `az aks nodepool upgrade -g <rg> --cluster-name <cluster> -n <nodepool> --kubernetes-version <version>`
   - Nodes are cordoned, drained, and replaced one by one (or in surge batches)
4. **Verify:** `kubectl get nodes` — all nodes on new version, all Ready

**Surge upgrade settings:** configure `--max-surge` on node pools (e.g. `33%`) to provision extra nodes during upgrade rather than drain-before-replace. Faster upgrades, temporary cost increase.

**PodDisruptionBudgets are respected during drain.** If a PDB blocks eviction, the drain stalls. Ensure PDBs have `maxUnavailable >= 1` — `maxUnavailable: 0` will block upgrades entirely.

### Pre-upgrade checklist
- [ ] Check for deprecated APIs in your manifests: `kubectl api-resources` and use `pluto` tool to scan for deprecated API versions
- [ ] Verify PDBs won't block drainage
- [ ] Test upgrade in non-prod first (same version path)
- [ ] Check add-on compatibility (Helm charts, operators) with new K8s version
- [ ] Have a rollback plan — for AKS, rollback means redeploying from known-good state (no in-place downgrade)

---

## Node Drain & Cordon

```bash
# Cordon — prevent new pods scheduling on node (doesn't evict existing)
kubectl cordon <node-name>

# Drain — cordon + evict all pods (respects PDBs and terminationGracePeriod)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# If drain stalls on a PDB:
kubectl get pdb -A  # check which PDB is blocking
# Either fix the PDB or use --disable-eviction (bypasses PDB — use carefully)

# Uncordon after maintenance
kubectl uncordon <node-name>
```

---

## Day-2 Housekeeping

### Regular tasks
- **Monthly:** audit ClusterRoleBindings for unnecessary cluster-admin grants; review unused namespaces; check for orphaned PVCs
- **Per release:** run `pluto` to detect deprecated API usage before upgrading
- **Continuous:** monitor PVC capacity — Kubernetes won't warn you when a volume is nearly full unless you have an alert
- **Quarterly:** review resource requests vs actual usage (VPA recommendations); right-size before committing Reserved Instances

### Useful one-liners
```bash
# Pods not running
kubectl get pods -A --field-selector=status.phase!=Running

# Pods without resource requests (Burstable/BestEffort)
kubectl get pods -A -o json | jq '.items[] | select(.spec.containers[].resources.requests == null) | .metadata.name'

# Top pods by memory
kubectl top pods -A --sort-by=memory

# Events sorted by time (great for debugging cluster-wide issues)
kubectl get events -A --sort-by='.lastTimestamp' | tail -50

# All images running in cluster (useful for supply chain audit)
kubectl get pods -A -o jsonpath='{range .items[*]}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' | sort -u
```
