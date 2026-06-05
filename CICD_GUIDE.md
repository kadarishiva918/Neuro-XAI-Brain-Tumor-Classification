# CI/CD Pipeline - Complete Guide

**Brain Tumor Classification - Continuous Integration & Continuous Deployment**

**Date**: May 21, 2026  
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Tools & Components](#tools--components)
4. [Model Registry](#model-registry)
5. [Performance Regression Detection](#performance-regression-detection)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Overview

The CI/CD pipeline provides **fully automated** model training, testing, optimization, and deployment. It ensures code quality, detects performance regressions, and manages production deployments safely.

### Goals
✅ **Automated Testing** - Run 120+ tests on every push  
✅ **Performance Monitoring** - Track metrics and detect regressions  
✅ **Automated Deployment** - Safe, staged rollouts to production  
✅ **Model Versioning** - Track all model versions with metadata  
✅ **Rollback Capability** - Quick rollback if issues detected  
✅ **Scheduled Retraining** - Automatic model updates  

### Key Features
- **10-Stage Pipeline**: Quality → Test → Benchmark → Regression Detection → Build → Registry → Deploy
- **Multiple Environments**: Staging → Canary → Production
- **Automated Rollback**: Health checks and automatic rollback on failure
- **Performance Tracking**: Per-version metrics and trend analysis
- **Comprehensive Logging**: Full audit trail of all changes

---

## Pipeline Architecture

### Workflow Stages

```
┌─────────────────────────────────────────────────────────────┐
│ COMMIT/PUSH TO MAIN OR DEVELOP                              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 1: Code Quality   │ (Flake8, Black, Isort)
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 2: Testing        │ (pytest, coverage)
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 3: Benchmarking   │ (Performance metrics)
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 4: Regression     │ (Accuracy, latency checks)
        │ Detection               │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 5: Docker Build   │ (Create container image)
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Stage 6: Registry       │ (Model registration)
        │ Update                  │
        └────────────┬────────────┘
                     │
    IF develop branch:         IF main branch:
    │                          │
    ▼                          ▼
 STAGING              ┌─────────────────────┐
 DEPLOYMENT           │ Stage 7: Canary     │
                      │ Deployment (10%)    │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ Stage 8: Full       │
                      │ Production Deploy   │
                      └────────────────────┘
```

### Trigger Conditions

**On Push to `develop`**:
- Quality checks ✅
- Tests ✅
- Benchmarking ✅
- Regression detection ✅
- Docker build ✅
- **Deploy to Staging** ✅

**On Push to `main`**:
- All of above +
- Model registry update ✅
- **Canary deployment (10%)** ✅
- **Full production deployment** ✅

**On Schedule (Daily @ 2 AM UTC)**:
- Scheduled retraining ✅
- Performance tracking ✅

---

## Tools & Components

### 1. Model Registry (`model_registry.py`)

**Purpose**: Central management of all model versions

**Commands**:
```bash
# Register new model
python model_registry.py register \
  --path models/best_model.pth \
  --version v1.0 \
  --accuracy 0.95 \
  --latency 1000

# List all models
python model_registry.py list

# Set current active model
python model_registry.py set --version v1.0

# Compare versions
python model_registry.py compare --v1 v1.0 --v2 v0.9
```

**Features**:
- ✅ Version tracking with metadata
- ✅ File hashing for integrity
- ✅ Size tracking
- ✅ Performance metadata storage
- ✅ Current model tracking

**Registry File**: `models/registry.json`
```json
{
  "models": [
    {
      "version": "v20260521_120000",
      "path": "models/best_model.pth",
      "hash": "abc123...",
      "size_mb": 278.7,
      "created_at": "2026-05-21T12:00:00",
      "metadata": {
        "accuracy": 0.95,
        "latency_ms": 1000
      },
      "status": "active"
    }
  ],
  "current": "v20260521_120000"
}
```

---

### 2. Regression Detection (`regression_detector.py`)

**Purpose**: Automatically detect performance regressions

**Commands**:
```bash
# Run regression detection
python regression_detector.py \
  --baseline baseline_metrics.json \
  --current current_metrics.json \
  --output regression_report.json \
  --fail-on-regression
```

**Checks**:
- **Accuracy**: Regression > 1% → FAIL
- **Latency**: Increase > 10% → FAIL
- **Model Size**: Increase > 10% → FAIL
- **Memory**: Increase > 5% → FAIL

**Output Report**:
```json
{
  "status": "PASSED",
  "regressions": [],
  "baseline": { "accuracy": 0.95, "latency_ms": 1000 },
  "current": { "accuracy": 0.94, "latency_ms": 950 }
}
```

---

### 3. Deployment Manager (`deployment_manager.py`)

**Purpose**: Manage model deployments across environments

**Commands**:
```bash
# Prepare deployment
python deployment_manager.py prepare \
  --model models/best_model.pth \
  --version v1.0 \
  --tests-passed

# Deploy to staging
python deployment_manager.py deploy \
  --model models/best_model.pth \
  --version v1.0 \
  --environment staging

# Health check
python deployment_manager.py health --environment staging

# Canary deployment
python deployment_manager.py canary \
  --model models/best_model.pth \
  --version v1.0 \
  --percentage 10

# Rollback
python deployment_manager.py rollback \
  --environment production \
  --version v0.9

# View status
python deployment_manager.py status --environment production

# View history
python deployment_manager.py history
```

**Environments**:
1. **Staging**: Pre-production testing (0% production traffic)
2. **Canary**: Limited rollout (10% production traffic)
3. **Production**: Full deployment (100% traffic)

---

### 4. Enhanced CI/CD Workflow (`.github/workflows/complete-ci-cd.yml`)

**10-Stage Automated Pipeline**:

| Stage | Purpose | Trigger | Action |
|-------|---------|---------|--------|
| 1 | Code Quality | Always | Lint, format, security |
| 2 | Testing | Always | Unit + integration tests |
| 3 | Benchmarking | On push | Performance profiling |
| 4 | Regression | On push | Performance checks |
| 5 | Docker Build | On push | Container creation |
| 6 | Registry | main only | Model registration |
| 7 | Staging Deploy | develop only | Deploy to staging |
| 8 | Production | main only | Canary + full deploy |
| 9 | Retraining | Scheduled | Automatic retraining |
| 10 | Notifications | Always | Status updates |

---

## Model Registry

### Workflow

**1. Model Training** (Local or CI)
```bash
python train.py --config configs/config.yaml
# Output: models/best_model.pth
```

**2. Register in Pipeline**
```bash
python model_registry.py register \
  --path models/best_model.pth \
  --version v${{ github.run_number }} \
  --accuracy 0.95
```

**3. Registry Updated**
```json
{
  "version": "v123",
  "accuracy": 0.95,
  "status": "active"
}
```

**4. Track Performance**
```bash
python model_registry.py performance \
  --version v123 \
  --accuracy 0.95 \
  --latency 1000 \
  --show-history
```

---

## Performance Regression Detection

### Automated Checks

```
Baseline (Previous)     Current (New)
─────────────────      ─────────────
Accuracy: 95%      →   Accuracy: 93%  ❌ 2% drop > 1% threshold
Latency: 1000ms    →   Latency: 1050ms ⚠️ 5% increase < 10%
Size: 278.7MB      →   Size: 280MB     ✅ < 10% threshold
```

### Configuration

**Thresholds** (in `regression_detector.py`):
```python
accuracy_threshold = 1.0      # 1% drop allowed
latency_threshold = 10.0      # 10% increase allowed
size_threshold = 10.0         # 10% increase allowed
memory_threshold = 5.0        # 5% increase allowed
```

### Adjusting Thresholds

Edit `regression_detector.py` and redeploy:
```python
def check_accuracy(self, threshold: float = 2.0) -> bool:  # Changed from 1.0
    ...
```

---

## Deployment Strategies

### Strategy 1: Staging Deployment (Branch: `develop`)

```
develop branch
    ↓
[All tests pass]
    ↓
Deploy to staging environment
    ↓
Health check
    ↓
✅ Ready for manual promotion to production
```

### Strategy 2: Canary Deployment (Branch: `main`)

```
main branch
    ↓
[All tests pass + Registry updated]
    ↓
Deploy to 10% of production (canary)
    ↓
[Monitor for 5 minutes]
    ↓
No errors detected?
    ├─ YES → Deploy to 100% ✅
    └─ NO → Automatic rollback ❌
```

### Strategy 3: Blue-Green Deployment

```
Blue (Current)        Green (New)
    │                    │
    └─── [All tests pass]
    
    Current traffic → Blue
           │
           └─→ Switch to Green when ready
           
Rollback: Switch back to Blue instantly
```

---

## Monitoring & Alerts

### Metrics Tracked

**Per Model**:
- Accuracy
- Inference latency (p50, p95, p99)
- Model size
- Memory usage
- File hash (integrity)

**Per Deployment**:
- Deployment time
- Health check status
- Error rate
- Uptime

### Alert Conditions

| Condition | Severity | Action |
|-----------|----------|--------|
| Test failure | Critical | Block deployment |
| Regression detected | Warning | Manual review |
| Health check fail | Critical | Auto rollback |
| Performance < baseline | Warning | Notify team |
| Model size > 300MB | Info | Suggest optimization |

### Setting Up Notifications

**GitHub Notifications** (Default):
- Email on pipeline failure
- GitHub check status

**Slack Integration** (Optional):
```yaml
- name: Slack Notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Troubleshooting

### Issue: Tests fail locally but pass in CI

**Causes**:
- Different Python versions
- Missing dependencies
- Environment variables not set

**Solutions**:
```bash
# Match CI environment
python --version  # Should be 3.10 or 3.11

# Install exact dependencies
pip install -r requirements.txt

# Run tests as CI does
pytest tests/ --cov=src
```

### Issue: Regression detection too strict

**Solution**: Adjust thresholds in `regression_detector.py`
```python
# Current: 1% accuracy drop triggers failure
# Change to 2% for more lenient checks
detector.check_accuracy(threshold=2.0)
```

### Issue: Deployment fails health check

**Check**:
```bash
# Manual health check
python deployment_manager.py health --environment staging

# Check API logs
docker logs brain-tumor-api

# Rollback if needed
python deployment_manager.py rollback --environment staging --version v0.9
```

### Issue: Model not registering

**Debug**:
```bash
# Check registry file exists
cat models/registry.json

# Manually register
python model_registry.py register \
  --path models/best_model.pth \
  --version v-manual-test \
  --accuracy 0.95

# List all
python model_registry.py list
```

---

## Best Practices

### 1. **Test Before Committing**
```bash
# Run locally first
pytest tests/ --cov=src
python benchmark_model.py --full
```

### 2. **Use Meaningful Commit Messages**
```
✅ Good:
  "feat: Improve model accuracy to 95% with new attention mechanism"
  
❌ Bad:
  "update model"
```

### 3. **Monitor Production After Deployment**
```bash
# Check deployment status
python deployment_manager.py status --environment production

# View health metrics
curl http://api-server:5000/health
```

### 4. **Regular Performance Audits**
```bash
# Weekly comparison
python model_comparison.py \
  --models \
    models/best_model.pth \
    deployments/production_v123/model.pth \
  --recommendations
```

### 5. **Keep Baseline Updated**
```bash
# Update baseline after successful production deployment
cp models/best_model.pth models/baseline_model.pth
python benchmark_model.py --model models/baseline_model.pth \
  --export baseline_metrics.json
```

### 6. **Document Deployments**
```bash
# Always note deployment reason
python deployment_manager.py history
# Review deployment_log.json for audit trail
```

---

## Workflow Examples

### Example 1: Development to Production

**Step 1**: Work on feature branch
```bash
git checkout -b feature/model-improvement
# Make changes, commit locally
```

**Step 2**: Push to develop
```bash
git push origin feature/model-improvement
git checkout develop
git pull origin develop
# GitHub Actions runs automatically:
# - Tests ✅
# - Benchmarking ✅
# - Deploy to staging ✅
```

**Step 3**: Manual testing in staging
```bash
# Test API
curl http://staging-api:5000/predict -F "file=@test.jpg"
```

**Step 4**: Merge to main for production
```bash
git checkout main
git pull
# Create PR from feature branch
# Once approved, merge to main
# GitHub Actions runs:
# - Tests ✅
# - Regression detection ✅
# - Canary deployment (10%) ✅
# - Full production deployment ✅
```

### Example 2: Hotfix Deployment

**Issue**: Critical bug in production

**Solution**:
```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug main

# 2. Fix and test locally
# ... make fix ...
pytest tests/

# 3. Merge to main (bypasses develop)
git commit -am "fix: Critical production bug"
git push origin hotfix/critical-bug
# Create PR to main, approve, merge

# 4. Automatic deployment
# GitHub Actions tests and deploys immediately
# Canary → Full deployment
```

### Example 3: Performance Optimization

**Goal**: Reduce model size without accuracy loss

**Workflow**:
```bash
# 1. Create optimization branch
git checkout -b optimize/model-compression develop

# 2. Apply optimization locally
python knowledge_distillation.py --epochs 20 --output models/student.pth
python optimize_model.py --model models/student.pth --quantize

# 3. Benchmark
python benchmark_model.py --model models/student.pth --export results.json
# Results: 278MB → 20MB (14x), Accuracy 95% → 90%

# 4. Decide if acceptable
# If yes: update model_registry.py, push to develop
# If no: try different optimization strategy

# 5. Push and let CI/CD validate
git push origin optimize/model-compression
# Automatic tests + regression detection + deployment
```

---

## Continuous Retraining

### Scheduled Retraining (Daily @ 2 AM UTC)

**Triggered by**: Cron schedule in CI/CD

**Process**:
```bash
1. Retrain model on latest data
2. Evaluate performance
3. Compare with baseline
4. If improvements: auto-commit and register
5. If regressions: alert team
```

**To Disable**:
Edit `.github/workflows/complete-ci-cd.yml`:
```yaml
# Comment out schedule trigger
# schedule:
#   - cron: '0 2 * * *'
```

---

## Environment Variables

Store secrets in GitHub Secrets:
```
DOCKER_USERNAME
DOCKER_PASSWORD
SLACK_WEBHOOK
MODEL_REGISTRY_KEY
DEPLOYMENT_TOKEN
```

Access in workflows:
```yaml
env:
  API_TOKEN: ${{ secrets.DEPLOYMENT_TOKEN }}
```

---

## Summary

**Phase 5: CI/CD Enhancement** provides:

✅ **Automated Testing** - 120+ tests, multiple Python versions  
✅ **Performance Monitoring** - Automatic regression detection  
✅ **Model Registry** - Version tracking with metadata  
✅ **Staged Deployments** - Staging → Canary → Production  
✅ **Automatic Rollback** - Health checks and instant rollback  
✅ **Scheduled Retraining** - Daily model updates  
✅ **Full Audit Trail** - Complete deployment history  

**Result**: **Production-ready CI/CD pipeline** for safe, automated model updates!

