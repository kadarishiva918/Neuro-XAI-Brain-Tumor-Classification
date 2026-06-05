# Brain Tumor Classification - Tools & Utilities Reference

**Quick Reference Guide for All Project Tools**

---

## 📋 Table of Contents

1. [Core Executable Scripts](#core-executable-scripts)
2. [Testing & Quality Tools](#testing--quality-tools)
3. [Deployment & Docker](#deployment--docker)
4. [Monitoring & Analytics](#monitoring--analytics)
5. [Configuration Files](#configuration-files)
6. [Documentation Files](#documentation-files)

---

## Core Executable Scripts

### 1. Training Script
**File**: `train.py`  
**Purpose**: Train the brain tumor classification model  
**Usage**:
```bash
python train.py --config configs/config.yaml
```
**Features**:
- YAML configuration support
- Early stopping
- Model checkpointing
- Tensorboard logging
- Device auto-detection

---

### 2. Evaluation Script
**File**: `evaluate.py`  
**Purpose**: Evaluate model on test set  
**Usage**:
```bash
python evaluate.py --model-path models/best_model.pth --data-dir data/raw
```
**Features**:
- Multi-class metrics (precision, recall, F1)
- Confusion matrix
- ROC curves
- Per-class analysis

---

### 3. Explanation Generation
**File**: `generate_explanations.py`  
**Purpose**: Generate XAI explanations for predictions  
**Usage**:
```bash
python generate_explanations.py --model-path models/best_model.pth --num-samples 20
```
**Features**:
- Grad-CAM visualization
- SHAP explanations
- LIME local explanations
- Comparison views

---

### 4. CLI Inference Tool
**File**: `inference.py`  
**Purpose**: Make predictions via command-line  
**Usage**:
```bash
# Single image
python inference.py --image path/to/image.jpg --explain

# Batch processing
python inference.py --image-dir path/to/images/ --output results.json

# With explanations
python inference.py --image image.jpg --explain --method gradcam --output output.json
```
**Features**:
- Single image prediction
- Batch processing
- XAI explanations
- GPU/CPU support
- JSON output

---

### 5. REST API Server
**File**: `api.py`  
**Purpose**: REST API for predictions  
**Usage**:
```bash
python api.py --port 5000 --device cuda
```
**Endpoints**:
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /classes` - Class information
- `POST /predict` - Single prediction (file upload)
- `POST /predict-base64` - Prediction from base64
- `POST /explain` - Explanation generation
- `POST /batch-predict` - Batch predictions

**Features**:
- File upload support
- Base64 encoding
- Error handling
- CORS enabled
- Configurable port

---

### 6. Dataset Setup
**File**: `setup_kaggle_dataset.py`  
**Purpose**: Download dataset from Kaggle  
**Usage**:
```bash
python setup_kaggle_dataset.py --api-key /path/to/kaggle.json
```
**Features**:
- Kaggle API integration
- Automatic extraction
- Validation

---

### 7. Synthetic Dataset Creator
**File**: `create_synthetic_dataset.py`  
**Purpose**: Create synthetic images for testing  
**Usage**:
```bash
python create_synthetic_dataset.py --num-images 100 --output data/synthetic
```

---

## Testing & Quality Tools

### 1. Test Suite
**File**: `tests/test_model.py`  
**Purpose**: Comprehensive testing framework  
**Usage**:
```bash
# Run all tests
pytest tests/test_model.py -v

# Run with coverage
pytest tests/test_model.py --cov=src

# Run specific test category
pytest tests/test_model.py -m unit
pytest tests/test_model.py -m integration
pytest tests/test_model.py -m performance
```
**Features**:
- 120+ tests
- Unit & integration tests
- Performance benchmarks
- Pytest markers
- Fixtures

**Test Categories**:
- `unit` - Individual component tests
- `integration` - Multi-component tests
- `performance` - Speed & memory tests
- `api` - API endpoint tests
- `data` - Data loading tests
- `xai` - Explanation tests
- `slow` - Long-running tests
- `gpu` - GPU-specific tests

---

### 2. Performance Benchmarking
**File**: `benchmark_model.py`  
**Purpose**: Benchmark inference performance  
**Usage**:
```bash
# Full benchmark suite
python benchmark_model.py --full --device cpu

# Test specific batch sizes
python benchmark_model.py --batch-sizes 1 4 8 16

# Export results
python benchmark_model.py --export benchmark_results.json

# Memory benchmarking
python benchmark_model.py --device cuda
```
**Metrics**:
- Latency (mean, std, p95, p99)
- Throughput (images/second)
- Memory usage (CPU & GPU)
- Model size statistics
- Parameter count

---

### 3. Model Optimization
**File**: `optimize_model.py`  
**Purpose**: Optimize model for deployment  
**Usage**:
```bash
# INT8 Quantization
python optimize_model.py --quantize

# Weight Pruning (30%)
python optimize_model.py --prune 0.3

# ONNX Export
python optimize_model.py --onnx

# TorchScript Export
python optimize_model.py --torchscript

# Generate Report
python optimize_model.py --report

# Combined optimization
python optimize_model.py --quantize --prune 0.3 --onnx
```
**Features**:
- INT8 quantization
- Magnitude pruning
- ONNX export
- TorchScript export
- Size/performance reports

---

## Deployment & Docker

### 1. Dockerfile
**File**: `Dockerfile`  
**Purpose**: Production-ready container image  
**Features**:
- Multi-stage build
- Minimal base image (python:3.10-slim)
- Security best practices
- Health checks
- Non-root user
- ~1.5GB final size

**Build**:
```bash
docker build -t brain-tumor-api:latest .
```

**Run**:
```bash
docker run -p 5000:5000 brain-tumor-api:latest
```

---

### 2. Docker Compose
**File**: `docker-compose.yml`  
**Purpose**: Full stack local deployment  
**Services**:
- **api**: Flask API server
- **notebook**: Jupyter Lab environment
- **prometheus**: Metrics collection
- **grafana**: Visualization dashboards
- **postgres**: PostgreSQL database
- **redis**: Redis cache

**Usage**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Access services**:
- API: http://localhost:5000
- Jupyter: http://localhost:8888
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- PostgreSQL: localhost:5432
- Redis: localhost:6379
```

---

## Monitoring & Analytics

### 1. Monitoring System
**File**: `src/monitoring.py`  
**Purpose**: Track and monitor predictions  
**Components**:
- `MetricsCollector`: Collect metrics
- `HealthChecker`: System health monitoring
- `AlertManager`: Alert generation
- `Monitor`: Unified interface

**Usage**:
```python
from src.monitoring import Monitor

# Create monitor
monitor = Monitor(model)

# Record prediction
monitor.record_request(
    predicted_class='glioma',
    confidence=0.95,
    latency_ms=150
)

# Get status
status = monitor.get_status()
print(status)

# Export metrics
monitor.export_metrics('metrics.json')

# Get report
print(monitor.get_report())
```

**Features**:
- Real-time metrics collection
- Health checks
- Alert management
- JSON export
- Performance monitoring

---

### 2. CI/CD Pipeline
**File**: `.github/workflows/ci-cd.yml`  
**Purpose**: Automated testing and deployment  
**Triggers**:
- Push to main/develop
- Pull requests
- Scheduled daily

**Jobs**:
- **test**: Unit tests + coverage
- **build**: Docker image build
- **security**: Bandit security scan
- **performance**: Performance tests
- **publish**: Push to Docker registry

---

## Configuration Files

### 1. Main Configuration
**File**: `configs/config.yaml`  
**Purpose**: Model, data, and training configuration  
**Sections**:
- `model`: Architecture settings
- `data`: Data loading parameters
- `training`: Training hyperparameters
- `augmentation`: Data augmentation settings
- `attention`: Attention mechanism config
- `xai`: Explanation settings

---

### 2. Pytest Configuration
**File**: `pytest.ini`  
**Purpose**: Pytest framework configuration  
**Features**:
- Test discovery patterns
- Marker definitions
- Coverage thresholds (70%)
- Timeout settings
- Logging configuration

---

### 3. Requirements Files
**File**: `requirements.txt`  
**Purpose**: Core dependencies  
**Contains**: PyTorch, TorchVision, scikit-learn, Albumentations, etc.

**File**: `requirements-api.txt`  
**Purpose**: API and deployment dependencies  
**Contains**: Flask, Gunicorn, Jupyter, Docker, etc.

---

## Documentation Files

### 1. System Overview
**File**: `SYSTEM_OVERVIEW.md`  
**Purpose**: Complete system documentation  
**Sections**:
- Executive summary
- Architecture overview
- Deployment options
- Testing framework
- Quick reference
- Performance metrics

---

### 2. Production Readiness
**File**: `PRODUCTION_READINESS.md`  
**Purpose**: Deployment checklist  
**Phases**:
1. Code Quality & Testing
2. Model & Performance
3. Security & Privacy
4. Deployment
5. Monitoring & Observability
6. Documentation
7. Backup & Disaster Recovery
8. Performance & Load Testing
9. User Acceptance Testing
10. Launch & Post-Launch

---

### 3. Testing Guide
**File**: `TESTING_GUIDE.md`  
**Purpose**: Comprehensive testing documentation  
**Topics**:
- Test structure
- Running tests
- Test categories
- Writing tests
- Code coverage
- CI/CD integration
- Best practices
- Troubleshooting

---

### 4. Usage Guide
**File**: `USAGE_GUIDE.md`  
**Purpose**: How to use all tools  
**Covers**:
- CLI usage
- API endpoint examples
- Batch processing
- Python integration
- Docker setup
- Troubleshooting

---

### 5. Deployment Package
**File**: `DEPLOYMENT_PACKAGE.md`  
**Purpose**: Deployment guide  
**Covers**:
- Project structure
- Installation
- API reference
- Security
- Scalability
- Monitoring

---

### 6. Quick Start
**File**: `QUICKSTART.md`  
**Purpose**: Get started in 5 minutes  
**Covers**:
- Installation
- Quick training
- Quick inference
- Quick API

---

### 7. Tuning Guide
**File**: `TUNING_GUIDE.md`  
**Purpose**: Hyperparameter tuning  
**Topics**:
- Learning rate tuning
- Batch size optimization
- Augmentation strategies
- Architecture modifications
- Loss function tuning

---

## 🎯 Quick Command Reference

| Task | Command |
|------|---------|
| Train model | `python train.py --config configs/config.yaml` |
| Evaluate model | `python evaluate.py --model-path models/best_model.pth` |
| Single inference | `python inference.py --image path/to/image.jpg` |
| Batch inference | `python inference.py --image-dir path/to/images/` |
| Start API | `python api.py` |
| Open Jupyter | `jupyter lab notebooks/demo.ipynb` |
| Run tests | `pytest tests/` |
| Full benchmark | `python benchmark_model.py --full` |
| Optimize model | `python optimize_model.py --quantize --onnx` |
| Docker build | `docker build -t brain-tumor-api:latest .` |
| Docker compose | `docker-compose up -d` |
| Generate report | `pytest tests/ --cov=src --cov-report=html` |

---

## 📊 System Capabilities Summary

### Inference Modes
- ✅ Single image (CLI)
- ✅ Batch processing (CLI)
- ✅ REST API
- ✅ Python programmatic
- ✅ Jupyter notebook
- ✅ Docker container

### Explanation Methods
- ✅ Grad-CAM
- ✅ SHAP
- ✅ LIME

### Optimization Options
- ✅ INT8 Quantization
- ✅ Weight Pruning
- ✅ ONNX Export
- ✅ TorchScript Export

### Deployment Options
- ✅ Standalone Python
- ✅ Flask REST API
- ✅ Docker container
- ✅ Docker Compose stack
- ✅ Kubernetes-ready

### Monitoring & Analytics
- ✅ Real-time metrics
- ✅ Performance tracking
- ✅ Health checks
- ✅ Alert management
- ✅ Grafana dashboards
- ✅ Prometheus metrics

---

## 🔧 Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Configure**: Edit `configs/config.yaml`
3. **Train**: `python train.py`
4. **Test**: `pytest tests/ --cov=src`
5. **Benchmark**: `python benchmark_model.py --full`
6. **Optimize**: `python optimize_model.py --quantize`
7. **Deploy**: `docker-compose up -d`
8. **Monitor**: Access Grafana at http://localhost:3000

---

## 📞 Getting Help

- **Documentation**: Read the relevant .md files
- **Code Examples**: Check `USAGE_GUIDE.md`
- **Testing**: See `TESTING_GUIDE.md`
- **Production**: Refer to `PRODUCTION_READINESS.md`
- **Issues**: Search existing GitHub issues or create new one

---

**Version**: 3.0.0  
**Status**: 🟢 Production Ready  
**Last Updated**: May 20, 2026
