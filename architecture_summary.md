# 🚀 MULTI-SERVICE PARALLEL ARCHITECTURE PLAN

## 📊 **ARCHITECTURE OVERVIEW**

### **Pipeline Design:**
```
Claim Input → Decomposer → [Brave Search, MiniCheck] → Evidence Aggregator → Results
```

### **🔧 SERVICES CONFIGURATION:**

| Service | Port | Max Concurrent | Timeout | Function |
|---------|------|----------------|---------|----------|
| **Decomposer** | 8006 | 5 | 30s | Atomic claim generation |
| **Brave Search** | 8010 | 20 | 15s | Evidence search |
| **MiniCheck** | 8011 | 15 | 10s | Quick verification |
| **Evidence Aggregator** | 8012 | 10 | 5s | Result aggregation |

### **⚡ PARALLEL PROCESSING STRATEGY:**

#### **Wave 1 (No Dependencies):**
- Brave Search (20 concurrent)
- MiniCheck (15 concurrent)
- Both run immediately after decomposition

#### **Wave 2 (Dependencies):**
- Evidence Aggregator (10 concurrent)
- Runs after Brave Search completes

### **📈 PERFORMANCE EXPECTATIONS:**

#### **Throughput Metrics:**
- **Simple Claims**: ~2-3 atomic claims → ~6 tasks
- **Complex Claims**: ~5-8 atomic claims → ~15 tasks
- **Processing Time**: 8-12s total
- **Throughput**: 0.5-1.0 claims/sec

#### **Concurrency Benefits:**
- **20x Faster** than sequential processing
- **Max 1000 evidences** per atomic claim
- **No bottleneck** in evidence gathering

### **🎯 IMPLEMENTATION PRIORITY:**

#### **Phase 1: Core Services**
1. ✅ **Decomposer Service** (already running)
2. 🔄 **Brave Search Integration** (mock → real)
3. 🔄 **MiniCheck Service** (mock → real)
4. 🔄 **Evidence Aggregator** (mock → real)

#### **Phase 2: Optimization**
1. **Load Balancing** across multiple instances
2. **Caching** for repeated claims
3. **Batch Processing** for multiple claims
4. **Monitoring** and metrics collection

### **🛠️ TECHNICAL IMPLEMENTATION:**

#### **Key Components:**
- **ParallelServiceOrchestrator**: Manages task distribution
- **Dependency Management**: Handles task dependencies
- **Semaphore Control**: Limits concurrent requests per service
- **Result Aggregation**: Combines results from all services

#### **Data Flow:**
```python
1. Decompose claim → Atomic claims
2. Create parallel tasks for each atomic claim
3. Execute tasks in waves based on dependencies
4. Aggregate results from all services
5. Return comprehensive fact-checking result
```

### **📋 CONFIGURATION OPTIONS:**

#### **Performance Tuning:**
```python
config = {
    "max_workers": 50,           # Total concurrent workers
    "max_evidences": 1000,       # Per atomic claim
    "batch_size": 10,             # Tasks per batch
    "timeout_decomposer": 30,     # Decomposer timeout
    "timeout_search": 15,         # Search timeout
    "timeout_check": 10,          # MiniCheck timeout
    "timeout_aggregate": 5       # Aggregator timeout
}
```

#### **Service Scaling:**
```python
services = {
    "decomposer": {"max_concurrent": 5},
    "brave_search": {"max_concurrent": 20},
    "minicheck": {"max_concurrent": 15},
    "evidence_aggregator": {"max_concurrent": 10}
}
```

### 🎯 **NEXT STEPS:**

#### **Immediate Actions:**
1. **Implement Real Services**: Replace mock services with actual implementations
2. **Brave Search API**: Integrate with actual search engine
3. **MiniCheck Algorithm**: Implement quick verification logic
4. **Evidence Ranking**: Add relevance scoring

#### **Integration Points:**
- **Decomposer → Brave Search**: Pass optimized queries
- **Brave Search → Evidence Aggregator**: Pass search results
- **MiniCheck → Results**: Pass verification scores
- **All Services → Monitoring**: Track performance metrics

### 📊 **EXPECTED BENEFITS:**

#### **Performance:**
- **20x Speed Improvement**: Parallel vs sequential
- **Higher Throughput**: Multiple claims per second
- **Better Resource Utilization**: All services busy

#### **Scalability:**
- **Horizontal Scaling**: Add more service instances
- **Load Distribution**: Balance across multiple servers
- **Fault Tolerance**: Continue if one service fails

#### **Accuracy:**
- **Comprehensive Evidence**: 1000 sources per claim
- **Multiple Verification**: Cross-check results
- **Ranking System**: Prioritize most relevant evidence

### 🔧 **DEPLOYMENT CONSIDERATIONS:**

#### **Infrastructure:**
- **Service Discovery**: Dynamic service registration
- **Health Monitoring**: Service availability checks
- **Load Balancing**: Distribute requests evenly
- **Circuit Breakers**: Fail fast for unhealthy services

#### **Monitoring:**
- **Response Times**: Track per-service performance
- **Success Rates**: Monitor service reliability
- **Throughput**: Track claims per second
- **Error Rates**: Identify bottlenecks

---

**🎯 STATUS: ARCHITECTURE DESIGNED**
**📋 NEXT: IMPLEMENT REAL SERVICES**
**⚡ GOAL: MAXIMUM PARALLEL THROUGHPUT**
