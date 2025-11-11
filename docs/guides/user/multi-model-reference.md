# Multi-Model Quick Reference Guide

## What Happens When Different Clients Use Different Models?

### TL;DR
With Ollama (local deployment), multiple clients can use different models simultaneously. The main costs are **computational resources** (CPU, RAM, GPU), not API fees.

---

## Quick Facts

| Aspect | Reality |
|--------|---------|
| **API Cost** | $0 (local deployment) |
| **Resource Cost** | CPU + RAM + Electricity |
| **Model Switching** | 2-10 second loading delay |
| **Concurrent Models** | Limited by available RAM |
| **Privacy** | 100% - data never leaves your server |

---

## Common Scenarios

### Scenario 1: Sequential Access (Current Behavior)
```
Client A → llama3.2 → Response
Client B → mistral → Load model (5s delay) → Response
Client C → llama3.2 → Load model (5s delay) → Response
```

**Impact:**
- ✗ Model switching adds 2-10s latency
- ✓ Low memory usage (only 1 model loaded)
- ✗ Reduced throughput

**When to use:** Limited RAM (< 16GB)

### Scenario 2: Pre-loaded Models (Optimized)
```
System startup → Load llama3.2, mistral, phi3
Client A → llama3.2 → Instant response
Client B → mistral → Instant response
Client C → phi3 → Instant response
```

**Impact:**
- ✓ Zero model switching delays
- ✗ High memory usage (all models in RAM)
- ✓ Maximum throughput

**When to use:** Adequate RAM (32GB+), high traffic

---

## Model Resource Requirements

| Model | Size | RAM Needed | Speed (tokens/s) | Quality |
|-------|------|------------|------------------|---------|
| **llama3.2:1b** | 1.3GB | 2GB | 50-100 | Good |
| **phi3:3.8b** | 2.3GB | 4GB | 30-70 | Very Good |
| **llama3.2:8b** | 4.7GB | 8GB | 20-50 | Excellent |
| **mistral:7b** | 4.1GB | 8GB | 25-60 | Excellent |
| **llama3.1:70b** | 40GB | 64GB | 5-15 | Superior |

**Rule of Thumb:** Total RAM = (Sum of model sizes) × 1.5

**Example:**
- Want to run: llama3.2:8b (4.7GB) + mistral:7b (4.1GB) + phi3 (2.3GB)
- Total model size: 11.1GB
- RAM needed: 11.1 × 1.5 = **~17GB minimum**
- Recommended: **32GB RAM** (leaves room for OS + applications)

---

## Cost Comparison

### Your Setup (Ollama)
```
Model inference: $0.00
Infrastructure: ~$400-2500/month (depending on hardware)
Cost per request: ~$0.001-0.03
```

### Cloud APIs
```
OpenAI GPT-4o: $0.005 per request (avg)
Anthropic Claude: $0.008 per request (avg)
Cost per request: ~$0.005-0.01
```

### Break-Even Point
- **Low traffic (< 10,000 requests/month):** Cloud may be cheaper
- **Medium traffic (10,000-100,000/month):** Ollama saves 50-70%
- **High traffic (> 100,000/month):** Ollama saves 85-95%

---

## Quick Setup Guide

### 1. Install Resource Monitor

Already configured in your `plugins/config.yaml`! Just ensure the plugin is in the right location:

```bash
# Check if plugin exists
ls plugins/monitoring_plugins/resource_monitor_plugin.py
```

### 2. Run Cost Analysis Demo

```bash
# Make executable
chmod +x demo_multi_model_cost_analysis.py

# Run demo
python demo_multi_model_cost_analysis.py
```

This will:
- Test multiple models with different clients
- Measure resource usage per model
- Calculate estimated costs
- Generate a detailed report
- Compare with cloud API pricing

### 3. View Cost Report

If using Flask app with resource monitor enabled:

```bash
# Start your Flask app
python apps/app_flask.py

# In another terminal, get cost report
curl http://localhost:5001/cost-report
```

### 4. Monitor Real-time

```bash
# Watch system resources
watch -n 2 'ps aux | grep ollama'
htop  # or top on macOS

# Check Ollama models
ollama list

# Check running models
ollama ps
```

---

## Optimization Strategies

### Quick Wins (< 1 hour implementation)

1. **Pre-load Common Models**
   ```bash
   # Pull and keep loaded
   ollama pull llama3.2
   ollama pull phi3
   ollama pull mistral
   ```

2. **Use Smaller Models for Simple Tasks**
   - FAQ / Simple queries → phi3 (3.8B)
   - General conversation → llama3.2 (8B)
   - Complex analysis → mistral (7B) or llama3.1 (70B)

3. **Set Model Defaults**
   Update `plugins/config.yaml`:
   ```yaml
   backends:
     ollama:
       config:
         default_model: "llama3.2"  # Fast and efficient
   ```

### Medium Effort (2-4 hours)

4. **Implement Response Caching**
   - Cache responses for temperature=0 (deterministic)
   - 10-30% cache hit rate = 10-30% resource savings
   - See detailed implementation in `COST_ANALYSIS_AND_OPTIMIZATION.md`

5. **Add Intelligent Model Routing**
   - Route by query complexity
   - Automatically select smallest capable model
   - Example in `COST_ANALYSIS_AND_OPTIMIZATION.md` Section 3.2

### Advanced (1-2 days)

6. **Load Balancing Multiple Ollama Instances**
   ```yaml
   # Run multiple Ollama servers
   ollama serve --port 11434  # Instance 1
   ollama serve --port 11435  # Instance 2

   # Load balance with nginx/haproxy
   ```

7. **GPU Acceleration**
   - Install CUDA/ROCm drivers
   - Ollama automatically uses GPU
   - 2-5x performance boost

---

## Monitoring Commands

### Check Resource Usage

```bash
# CPU and Memory
top -o cpu

# Disk I/O
iostat -x 1

# GPU (if available)
nvidia-smi

# Ollama specific
ollama ps  # Running models
ollama list  # Installed models
```

### Log Analysis

```bash
# Check plugin logs
tail -f logs/plugin_system.log

# Check audit logs
tail -f logs/audit/*.log

# Search for errors
grep -i error logs/plugin_system.log
```

---

## Troubleshooting

### Problem: "Model takes too long to load"

**Cause:** Model switching overhead
**Solution:**
1. Keep frequently-used models loaded
2. Use smaller models for low-priority requests
3. Add more RAM to pre-load multiple models

### Problem: "Out of memory errors"

**Cause:** Too many models loaded simultaneously
**Solution:**
1. Reduce number of concurrent models
2. Use smaller model variants (e.g., 1B instead of 8B)
3. Upgrade RAM
4. Implement LRU model unloading

### Problem: "Different clients getting inconsistent performance"

**Cause:** Resource contention during model switching
**Solution:**
1. Pre-load all commonly-used models
2. Implement request queuing per model
3. Set up separate Ollama instances per model
4. Use load balancer to distribute requests

### Problem: "Want to track costs but resource monitor not working"

**Cause:** Plugin not loaded or missing dependencies
**Solution:**
```bash
# Check plugin is enabled
grep -A 5 "resource_monitor" plugins/config.yaml

# Install dependencies
pip install psutil GPUtil

# Test plugin directly
python -c "from plugins.monitoring_plugins.resource_monitor_plugin import ResourceMonitorPlugin; print('OK')"
```

---

## Cost Optimization Checklist

- [ ] Run `demo_multi_model_cost_analysis.py` to establish baseline
- [ ] Identify top 3 most-used models from logs
- [ ] Calculate total RAM needed for concurrent loading
- [ ] Enable resource monitoring plugin
- [ ] Set up model usage tracking
- [ ] Implement caching for deterministic queries (temp=0)
- [ ] Create tiered model architecture (small/medium/large)
- [ ] Add intelligent model routing
- [ ] Monitor weekly cost reports
- [ ] Compare costs with cloud alternatives monthly

---

## When to Switch to Cloud APIs?

Consider cloud APIs if:
- ✓ Request volume < 10,000/month (may be cheaper)
- ✓ Need 99.99% uptime SLA
- ✓ Require global edge locations
- ✓ Don't want to manage infrastructure
- ✓ Need latest cutting-edge models (GPT-4, Claude Opus)
- ✓ Highly variable traffic (cloud scales better)

Stick with Ollama if:
- ✓ Request volume > 50,000/month (massive savings)
- ✓ Privacy is critical (healthcare, finance)
- ✓ Have stable, predictable traffic
- ✓ Have available hardware/cloud credits
- ✓ Need offline operation
- ✓ Want full control over models

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `COST_ANALYSIS_AND_OPTIMIZATION.md` | Comprehensive analysis guide |
| `demo_multi_model_cost_analysis.py` | Demo script to test multi-model costs |
| `plugins/monitoring_plugins/resource_monitor_plugin.py` | Resource tracking plugin |
| `plugins/config.yaml` | Configuration (lines 187-197 for monitoring) |
| `research/sensitivity_analysis.py` | Performance benchmarking tools |
| `research/data_comparison.py` | Model comparison analysis |

---

## Quick Decision Tree

```
Do you have > 16GB RAM?
├─ Yes: Pre-load 2-3 models → Zero switching delays
└─ No: Use single default model → Accept switching delays

Are requests > 100,000/month?
├─ Yes: Ollama saves 80-95% vs cloud
└─ No: Calculate break-even point

Need multiple models simultaneously?
├─ Yes: RAM = (Sum of model sizes) × 1.5
└─ No: Use single model with 8GB RAM

Need to track costs?
├─ Yes: Enable resource_monitor plugin
└─ No: Use basic performance metrics
```

---

## Next Steps

1. **Run the demo**: `python demo_multi_model_cost_analysis.py`
2. **Review the report**: Check generated `cost_analysis_report_*.txt`
3. **Enable monitoring**: Ensure `resource_monitor` plugin is active
4. **Measure for 1 week**: Collect real usage data
5. **Optimize**: Implement strategies from comprehensive guide
6. **Monitor savings**: Track weekly cost trends

---

**Last Updated:** 2025-11-11
**For detailed information, see:** `COST_ANALYSIS_AND_OPTIMIZATION.md`
