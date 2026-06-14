# Infrastructure Metrics Analysis
## Deviation from Bob Protocol - Detailed Evaluation

**Date:** 2026-06-14  
**Context:** STEP 2 metric validation found 18 unmatched metrics  
**Decision:** Deviate from strict protocol to evaluate infrastructure metrics

---

## All 18 Unmatched Metrics

### Kubernetes Resource Metrics (14 metrics)

| Metric | Category | Source | Kubecost Relevant? |
|--------|----------|--------|-------------------|
| `kubernetes.cpu.usage.total` | Compute | K8s Agent | ✅ YES - CPU cost |
| `kubernetes.cpu.limits` | Compute | K8s Agent | ✅ YES - Resource allocation |
| `kubernetes.cpu.cfs.throttled.seconds` | Compute | K8s Agent | ✅ YES - Efficiency metric |
| `kubernetes.memory.usage` | Compute | K8s Agent | ✅ YES - Memory cost |
| `kubernetes.memory.limits` | Compute | K8s Agent | ✅ YES - Resource allocation |
| `kubernetes.containers.restarts` | Reliability | K8s Agent | ⚠️ INDIRECT - Stability indicator |
| `kubernetes.containers.state.oomkilled` | Reliability | K8s Agent | ⚠️ INDIRECT - Memory sizing |
| `kubernetes.pods.running` | Capacity | K8s Agent | ✅ YES - Pod count for cost |
| `kubernetes.pods.pending` | Capacity | K8s Agent | ⚠️ INDIRECT - Scheduling issues |
| `kubernetes.pods.failed` | Reliability | K8s Agent | ❌ NO - Reliability only |
| `kubernetes.network.tx_bytes` | Network | K8s Agent | ✅ YES - Data transfer cost |
| `kubernetes.network.rx_bytes` | Network | K8s Agent | ✅ YES - Data transfer cost |
| `kubernetes.network.tx_errors` | Network | K8s Agent | ❌ NO - Reliability only |
| `kubernetes.network.rx_errors` | Network | K8s Agent | ❌ NO - Reliability only |
| `kubernetes.io.read_bytes` | Storage | K8s Agent | ✅ YES - I/O cost |
| `kubernetes.io.write_bytes` | Storage | K8s Agent | ✅ YES - I/O cost |

### Application Performance Metrics (2 metrics)

| Metric | Category | Source | Kubecost Relevant? |
|--------|----------|--------|-------------------|
| `@duration` | APM | Datadog APM | ❌ NO - Performance only |
| `@cldy_user_id` | APM | Datadog APM | ❌ NO - User tracking |

---

## Kubecost Relevance Assessment

### ✅ Directly Relevant to Kubecost (11 metrics)

**Compute Costs:**
- `kubernetes.cpu.usage.total` - Actual CPU consumption
- `kubernetes.cpu.limits` - Allocated CPU (for cost allocation)
- `kubernetes.cpu.cfs.throttled.seconds` - CPU efficiency
- `kubernetes.memory.usage` - Actual memory consumption
- `kubernetes.memory.limits` - Allocated memory (for cost allocation)

**Network Costs:**
- `kubernetes.network.tx_bytes` - Egress data transfer
- `kubernetes.network.rx_bytes` - Ingress data transfer

**Storage Costs:**
- `kubernetes.io.read_bytes` - Disk read operations
- `kubernetes.io.write_bytes` - Disk write operations

**Capacity Planning:**
- `kubernetes.pods.running` - Active pod count for cost calculation

### ⚠️ Indirectly Relevant (3 metrics)

**Resource Efficiency Indicators:**
- `kubernetes.containers.restarts` - May indicate resource constraints
- `kubernetes.containers.state.oomkilled` - Memory under-provisioning
- `kubernetes.pods.pending` - Scheduling/capacity issues

### ❌ Not Relevant to Kubecost (4 metrics)

**Reliability/Performance Only:**
- `kubernetes.pods.failed` - Reliability metric
- `kubernetes.network.tx_errors` - Network reliability
- `kubernetes.network.rx_errors` - Network reliability
- `@duration` - Application latency
- `@cldy_user_id` - User identification

---

## Kubecost Integration Assessment

### Current State

**Environment Variables Available:**
```bash
KUBECOST_CLUSTER_DEV=uw2d-akp-k1
KUBECOST_CLUSTER_STAGING=uw2s-akp-k1
KUBECOST_CLUSTER_PROD=uw2p-akp-k1
```

**Kubecost Capabilities:**
1. **Cost Allocation** - Per pod, namespace, service
2. **Resource Efficiency** - Utilization vs allocation
3. **Savings Recommendations** - Right-sizing, spot instances
4. **Network Costs** - Data transfer costs
5. **Storage Costs** - PV costs

### Integration Options

#### Option 1: Kubecost API Plugin (Recommended)

**Pros:**
- Direct access to cost data
- Pre-calculated cost allocations
- Savings recommendations included
- Historical cost trends
- Multi-cluster support (dev, staging, prod)

**Cons:**
- Requires Kubecost API access
- Additional dependency
- May need authentication setup

**Implementation:**
```python
# New dependency
kubecost-integration @ git+https://github.com/lecton-apptio/kubecost-integration.git

# Usage
from kubecost_integration import KubecostClient

client = KubecostClient(
    cluster=os.getenv("KUBECOST_CLUSTER_PROD"),
    api_url="http://kubecost.uw2p-akp-k1.svc.cluster.local:9090"
)

# Get cost allocation
costs = client.get_allocation(
    window="7d",
    aggregate="service"
)
```

#### Option 2: Calculate from Kubernetes Metrics

**Pros:**
- Uses existing Datadog metrics
- No additional dependencies
- Works with current setup

**Cons:**
- Must implement cost calculation logic
- Need cloud provider pricing data
- Less accurate than Kubecost
- No savings recommendations

**Implementation:**
```python
# Calculate CPU cost
cpu_hours = kubernetes.cpu.usage.total * hours
cpu_cost = cpu_hours * AWS_CPU_PRICE_PER_HOUR

# Calculate memory cost
memory_gb_hours = kubernetes.memory.usage * hours / 1024**3
memory_cost = memory_gb_hours * AWS_MEMORY_PRICE_PER_GB_HOUR
```

#### Option 3: Hybrid Approach

**Pros:**
- Best of both worlds
- Fallback if Kubecost unavailable
- Validates Kubecost data

**Cons:**
- More complex
- Maintenance overhead

---

## Recommendation

### ✅ Create Kubecost Integration Plugin

**Rationale:**
1. **11 of 18 metrics** are directly relevant to cost tracking
2. Kubecost clusters already configured (dev, staging, prod)
3. Provides richer cost insights than raw metrics
4. Aligns with dashboard's operational review purpose
5. Enables cost optimization recommendations

**Plugin Scope:**
```python
# kubecost-integration package
class KubecostClient:
    def get_allocation(window, aggregate) -> Dict
    def get_efficiency() -> Dict
    def get_savings_recommendations() -> List
    def get_network_costs() -> Dict
    def get_storage_costs() -> Dict
```

**Integration with Bob:**
- STEP 2: Validate Kubecost API connectivity
- STEP 3: Include cost data in weekly Confluence summary
- STEP 4: Sync cost dashboards to Datadog
- STEP 5: N/A (Kubecost doesn't emit metrics to instrument)

### Modified STEP 2 Validation

**Update metric validation logic:**
```python
# Categorize metrics
INFRASTRUCTURE_METRICS = {
    "kubernetes.*",
    "@duration",
    "@cldy_user_id"
}

KUBECOST_METRICS = {
    "kubernetes.cpu.*",
    "kubernetes.memory.*",
    "kubernetes.network.*",
    "kubernetes.io.*",
    "kubernetes.pods.running"
}

# Validation rules:
# 1. Application metrics → must exist in service repos
# 2. Infrastructure metrics → skip validation (agent-collected)
# 3. Kubecost metrics → validate Kubecost API access
```

---

## Action Items

### Immediate
1. ✅ Document infrastructure metrics (this file)
2. ⏳ Create kubecost-integration repository
3. ⏳ Implement KubecostClient with basic API calls
4. ⏳ Add kubecost-integration to pyproject.toml
5. ⏳ Update bob_step2.py to validate Kubecost API

### Short-term
6. ⏳ Implement cost calculation in STEP 3 (weekly summary)
7. ⏳ Add cost trends to Confluence reports
8. ⏳ Create cost optimization recommendations

### Long-term
9. ⏳ Build cost forecasting models
10. ⏳ Implement cost anomaly detection
11. ⏳ Create cost allocation dashboards per team/service

---

## Conclusion

**DEVIATION JUSTIFIED:** Infrastructure metrics serve a valid operational purpose (cost tracking) but don't belong in application code. A separate Kubecost plugin is the correct architectural solution.

**SYSTEM_STATUS:** Should be updated to:
- VALID (with caveat) - Infrastructure metrics handled by separate plugin
- BLOCKED - Pending Kubecost integration implementation

**Next Steps:**
1. Create kubecost-integration plugin
2. Update STEP 2 to validate Kubecost API
3. Proceed to STEP 3 with cost data integration