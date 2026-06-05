# Advanced Model Optimization Guide

**Brain Tumor Classification - Model Optimization & Compression**

**Date**: May 20, 2026  
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Optimization Techniques](#optimization-techniques)
3. [Quantization](#quantization)
4. [Knowledge Distillation](#knowledge-distillation)
5. [Pruning](#pruning)
6. [Combined Strategies](#combined-strategies)
7. [Performance Comparison](#performance-comparison)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Model optimization focuses on reducing model size, inference latency, and memory usage while maintaining or slightly sacrificing accuracy. This guide covers advanced optimization techniques beyond basic compression.

### Goals
- **Reduce model size** (target: <100 MB)
- **Improve inference speed** (target: <50ms on CPU, <10ms on GPU)
- **Minimize memory usage** (target: <500MB peak)
- **Maintain accuracy** (target: >90% on test set)

### Key Metrics
| Metric | Baseline | Target | Priority |
|--------|----------|--------|----------|
| Model Size | 278.7 MB | 70-100 MB | High |
| CPU Latency | 1-2s | 200-500ms | Medium |
| GPU Latency | 50-100ms | 10-20ms | Medium |
| Accuracy | 95% | >90% | High |

---

## Optimization Techniques

### 1. Quantization

**What**: Convert floating-point weights to lower precision (INT8, INT4)

**Types**:
- **Post-Training Quantization (PTQ)**: Quantize after training
- **Quantization-Aware Training (QAT)**: Train while simulating quantization
- **Dynamic Quantization**: Quantize only weights (not activations)

**Pros**:
- 4x size reduction (FP32 → INT8)
- 2-4x speedup
- Easy to implement
- No retraining required (PTQ)

**Cons**:
- 0-5% accuracy loss typically
- Limited to 8-bit or 4-bit
- Some layers may not support quantization

**Commands**:
```bash
# Post-training quantization (already implemented in optimize_model.py)
python optimize_model.py --quantize

# Quantization-Aware Training
python quantization_aware_training.py --qat --epochs 5
```

---

### 2. Knowledge Distillation

**What**: Train a smaller "student" model to mimic a larger "teacher" model

**How It Works**:
```
Teacher Model (278.7 MB) → Knowledge Transfer → Student Model (50-70 MB)
95% Accuracy                                      ~92% Accuracy
```

**Student Models Available**:
- **Lightweight CNN**: 50-70 MB, 5-10x faster
- **MobileNet**: 20-40 MB, 10-20x faster
- **TinyNet**: 10-20 MB, 20-30x faster

**Hyperparameters**:
- **Temperature**: Controls softness of knowledge transfer (default: 4.0)
  - Higher → softer targets, more knowledge transfer
  - Lower → harder targets, less transfer
- **Alpha**: Weight balance between CE and KL losses (default: 0.7)
  - 0.7 → 70% CE, 30% KL divergence

**Pros**:
- Can achieve 90%+ accuracy with 4-5x compression
- Improves generalization
- Flexible architecture choice
- Can be combined with quantization

**Cons**:
- Requires retraining
- Longer training time
- Need large unlabeled/labeled dataset
- Manual architecture design

**Commands**:
```bash
# Knowledge distillation
python knowledge_distillation.py \
  --epochs 20 \
  --temperature 4.0 \
  --alpha 0.7 \
  --output models/student_model.pth

# Custom temperature and alpha
python knowledge_distillation.py \
  --temperature 5.0 \
  --alpha 0.8
```

---

### 3. Pruning

**What**: Remove less important connections/weights

**Types**:
- **Magnitude Pruning**: Remove small weights
- **Structured Pruning**: Remove entire channels/filters
- **Unstructured Pruning**: Remove individual weights

**Sparsity Levels**:
- 30% pruning: ~1.3x compression, minimal accuracy loss
- 50% pruning: ~1.8x compression, 1-2% accuracy loss
- 70% pruning: ~2.5x compression, 3-5% accuracy loss

**Pros**:
- Hardware-friendly (can be deployed efficiently)
- Better than quantization for some models
- Can be combined with quantization

**Cons**:
- Requires special libraries/hardware for speedup
- Pruned models need fine-tuning
- Less effective alone (use with quantization)

**Commands**:
```bash
# 30% pruning
python optimize_model.py --prune 0.3

# 50% pruning
python optimize_model.py --prune 0.5

# 70% pruning
python optimize_model.py --prune 0.7
```

---

### 4. Export Formats

**ONNX (Open Neural Network Exchange)**:
- Cross-platform format
- CPU/GPU support
- Third-party tool ecosystem
```bash
python optimize_model.py --onnx
# Creates: models/model.onnx
```

**TorchScript**:
- PyTorch-native format
- Good for deployment with C++
- Minimal external dependencies
```bash
python optimize_model.py --torchscript
# Creates: models/model.pt
```

---

## Quantization

### Post-Training Quantization (PTQ)

**Workflow**:
```
1. Load trained model
2. Apply quantization config
3. Calibrate on small dataset (100 batches)
4. Convert to quantized model
5. Optionally fine-tune
```

**Implementation**:
```python
python optimize_model.py --quantize --output models/quantized_model.pth
```

**Expected Results**:
- Size reduction: 4x (278.7 MB → ~70 MB)
- Latency reduction: 1.5-2x (1s → 500-700ms on CPU)
- Accuracy drop: 0-2%

### Quantization-Aware Training (QAT)

**Workflow**:
```
1. Load trained model
2. Insert fake quantization ops
3. Calibrate on training data
4. Train for 5-10 epochs
5. Convert to quantized model
```

**Implementation**:
```bash
python quantization_aware_training.py --qat --epochs 5
```

**Expected Results**:
- Size reduction: 4x (same as PTQ)
- Latency reduction: 2-3x (1s → 300-500ms)
- Accuracy: Better than PTQ (usually minimal loss)
- Time cost: +10-30 minutes training

### Which to Choose?

| Criterion | PTQ | QAT |
|-----------|-----|-----|
| Accuracy retention | 95-98% | 98-99% |
| Time required | Minutes | Hours |
| Accuracy loss | 1-3% | 0-1% |
| Recommended | Quick prototyping | Production |
| Retraining needed | No | Yes |

---

## Knowledge Distillation

### Training Process

**1. Prepare Teacher Model**
```python
# Teacher is already trained (best_model.pth)
teacher = BrainTumorClassifier(...)
teacher.load_state_dict(torch.load('models/best_model.pth'))
teacher.eval()
```

**2. Create Student Model**
```python
# Student architecture (automatically created, 4-5x smaller)
student = StudentModel(num_classes=4)
```

**3. Distillation Loss**
```
Loss = α × CE(student_pred, labels) + (1-α) × KL(student_soft, teacher_soft)
```

**4. Training Loop**
```bash
python knowledge_distillation.py \
  --teacher-model models/best_model.pth \
  --epochs 20 \
  --temperature 4.0 \
  --alpha 0.7
```

### Temperature Tuning

| Temperature | Effect | When to Use |
|-------------|--------|------------|
| 1.0 | No softening (cross-entropy) | Baseline |
| 2.0-3.0 | Light softening | Large models |
| 4.0-6.0 | Medium softening (recommended) | Standard |
| 8.0-10.0 | Strong softening | Small student models |
| >10.0 | Very soft targets | Extreme compression |

### Alpha (Loss Weight) Tuning

| Alpha | CE Loss | KL Loss | When to Use |
|-------|---------|---------|------------|
| 1.0 | 100% | 0% | Standard CE training |
| 0.9 | 90% | 10% | Heavy on accuracy |
| 0.7 | 70% | 30% | **Recommended** |
| 0.5 | 50% | 50% | Balanced |
| 0.3 | 30% | 70% | Heavy on knowledge transfer |
| 0.1 | 10% | 90% | Extreme compression |

---

## Pruning

### Magnitude Pruning

**Concept**: Remove weights below threshold

```python
import torch.nn.utils.prune as prune

for module in model.modules():
    if isinstance(module, nn.Linear):
        prune.l1_unstructured(module, name='weight', amount=0.3)
```

**Sparsity Levels**:
- 30%: Most weights kept, minimal impact
- 50%: Half weights removed, some speedup
- 70%: Aggressive, needs fine-tuning

### Fine-Tuning Pruned Models

```bash
# 1. Prune model
python optimize_model.py --prune 0.3 --output models/pruned_model.pth

# 2. Fine-tune pruned model
python train.py --pretrained-model models/pruned_model.pth --epochs 5
```

---

## Combined Strategies

### Strategy 1: Quantization + Pruning

**Best for**: Maximum compression without accuracy loss

**Steps**:
```bash
# 1. Prune
python optimize_model.py --prune 0.3 --output models/pruned.pth

# 2. Quantize pruned model
python optimize_model.py --model models/pruned.pth --quantize --output models/pruned_quant.pth

# 3. Fine-tune
python train.py --pretrained-model models/pruned_quant.pth --epochs 3
```

**Expected Results**:
- Size: 278.7 MB → ~50 MB (5.5x compression)
- Latency: 1s → 250-400ms (2.5-4x speedup)
- Accuracy drop: 2-3%

### Strategy 2: Knowledge Distillation + Quantization

**Best for**: Extreme compression with good accuracy

**Steps**:
```bash
# 1. Distillation (train student)
python knowledge_distillation.py \
  --teacher-model models/best_model.pth \
  --epochs 20 \
  --output models/student.pth

# 2. Quantize student model
python optimize_model.py --model models/student.pth --quantize \
  --output models/student_quant.pth
```

**Expected Results**:
- Size: 278.7 MB → ~20-30 MB (9-14x compression)
- Latency: 1s → 100-200ms (5-10x speedup)
- Accuracy: ~90-92% (5-7% drop)
- Best for mobile/edge deployment

### Strategy 3: Progressive Distillation

**Best for**: Multi-stage compression

**Steps**:
```bash
# Stage 1: Teacher → Medium Student (2x compression)
python knowledge_distillation.py --teacher-model best_model.pth \
  --output student_medium.pth

# Stage 2: Medium Student → Small Student (2x compression)
python knowledge_distillation.py --teacher-model student_medium.pth \
  --output student_small.pth

# Stage 3: Quantize small student
python optimize_model.py --model student_small.pth --quantize
```

**Expected Results**:
- Size: 278.7 MB → ~30-40 MB (7-9x compression)
- Latency: 1s → 150-300ms
- Accuracy: ~92-93%

---

## Performance Comparison

### Model Variants Summary

| Model | Size (MB) | CPU Lat (ms) | GPU Lat (ms) | Accuracy | Speedup | Notes |
|-------|-----------|--------------|--------------|----------|---------|-------|
| Original | 278.7 | 1000 | 75 | 95% | 1.0x | Baseline |
| PTQ (INT8) | 70 | 700 | 60 | 93.5% | 1.4x | Quick |
| QAT (INT8) | 70 | 600 | 55 | 94% | 1.7x | Better |
| Pruned (30%) | 195 | 800 | 65 | 94.5% | 1.25x | Needs hardware |
| Distilled | 60 | 400 | 40 | 92% | 2.5x | Retraining |
| Quantized+Pruned | 45 | 400 | 35 | 91.5% | 2.7x | Best compression |
| Dist+Quant | 20 | 200 | 20 | 90% | 5x | Mobile-ready |

### Comparison Command

```bash
python model_comparison.py \
  --models models/best_model.pth models/quantized.pth models/student.pth \
  --names "Original" "Quantized" "Distilled" \
  --recommendations
```

---

## Best Practices

### 1. Start Simple
```
Try Quantization (PTQ) first → Easy, quick, effective
↓
If accuracy drop > 3%, use QAT
↓
For extreme compression, add Knowledge Distillation
```

### 2. Always Verify Accuracy
```bash
# Before optimization
python evaluate.py --model models/best_model.pth

# After optimization
python evaluate.py --model models/optimized_model.pth

# Compare accuracy drop
# Acceptable: < 2-3%
# Concerning: > 5%
```

### 3. Benchmark Before and After
```bash
# Original model
python benchmark_model.py --model models/best_model.pth --full

# Optimized model
python benchmark_model.py --model models/optimized_model.pth --full
```

### 4. Test on Target Hardware
- CPU inference: Test on CPU
- Mobile: Test with quantization
- GPU: Test with GPU device

### 5. Combine Techniques Carefully
- Quantization + Pruning: ✅ Good
- Quantization + Distillation: ✅ Excellent
- Pruning + Distillation: ✅ Good
- QAT + Pruning + Distillation: ⚠️ Complex, test carefully

---

## Troubleshooting

### Problem: Accuracy drops too much after quantization

**Solutions**:
1. Use QAT instead of PTQ
2. Increase quantization epochs
3. Use higher precision (INT16 instead of INT8)
4. Combine with knowledge distillation

### Problem: Quantization doesn't speed up inference

**Solutions**:
1. Model is limited by non-quantizable parts (LSTM, etc.)
2. Need specialized hardware or libraries (TensorRT, ONNX Runtime)
3. Use ONNX export for better speedup
4. Try pruning instead

### Problem: Student model accuracy too low after distillation

**Solutions**:
1. Increase temperature (4→6 or 8)
2. Increase alpha (0.7→0.9)
3. Train longer (20→30 epochs)
4. Reduce student compression ratio
5. Use better student architecture

### Problem: Combined optimization fails

**Solutions**:
1. Test each optimization individually first
2. Start with smaller changes (prune 10% first)
3. Use QAT before other techniques
4. Fine-tune after each major change

### Problem: Export to ONNX fails

**Solutions**:
1. Ensure model is on CPU: `model.cpu()`
2. Simplify model if too complex
3. Check ONNX opset version compatibility
4. Try TorchScript instead

---

## Recommended Optimization Pipelines

### For Mobile Deployment
```bash
# Goal: <50MB, works on smartphone
# Steps:
1. Knowledge Distillation → ~60-70 MB
2. Quantization (INT8) → ~15-20 MB
3. ONNX Export

# Command:
python knowledge_distillation.py --epochs 20 --output student.pth
python optimize_model.py --model student.pth --quantize --onnx
```

### For Edge Device (Raspberry Pi)
```bash
# Goal: <30MB, low power
# Steps:
1. Progressive Distillation (2 stages)
2. Quantization
3. Pruning

# Commands:
python knowledge_distillation.py --teacher-model best.pth --output student1.pth
python knowledge_distillation.py --teacher-model student1.pth --output student2.pth
python optimize_model.py --model student2.pth --prune 0.3 --quantize
```

### For Server (Fast inference)
```bash
# Goal: Fast inference, maintain accuracy
# Steps:
1. Quantization (INT8)
2. Optional: TensorRT conversion

# Command:
python optimize_model.py --model best_model.pth --quantize --onnx
# Use with TensorRT for GPU acceleration
```

---

## Performance Benchmarking

### Benchmark Your Optimizations
```bash
# Full benchmark of optimized model
python benchmark_model.py \
  --model models/optimized_model.pth \
  --full \
  --device cuda \
  --export results/benchmark.json
```

### Compare Multiple Variants
```bash
python model_comparison.py \
  --models \
    models/best_model.pth \
    models/quantized.pth \
    models/student.pth \
    models/pruned_quant.pth \
  --names "Original" "Quantized" "Distilled" "Pruned+Quant" \
  --recommendations
```

---

## References & Further Reading

- [PyTorch Quantization Docs](https://pytorch.org/docs/stable/quantization.html)
- [Knowledge Distillation Papers](https://arxiv.org/abs/1503.02531)
- [ONNX Runtime](https://onnxruntime.ai/)
- [TensorRT Optimization](https://developer.nvidia.com/tensorrt)

---

**Next Steps**:
1. Choose optimization strategy
2. Run optimization commands
3. Evaluate accuracy
4. Benchmark performance
5. Deploy optimized model

