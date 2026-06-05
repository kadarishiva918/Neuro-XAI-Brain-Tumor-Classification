# Performance Tuning Guide

## High Accuracy Configuration (Maximum Performance)
Use when accuracy is the priority:

```yaml
model:
  backbone: efficientnet_b0
  pretrained: true
  use_attention: true
  attention_type: cross_gated_multipath

training:
  epochs: 150
  learning_rate: 0.0003
  weight_decay: 0.00001
  optimizer: adam
  scheduler: cosine
  early_stopping_patience: 25
  use_gate_consistency_loss: true
  gate_consistency_weight: 0.15

data:
  batch_size: 16
  augmentation: true

augmentation:
  rotation_range: 45
  shift_range: 0.3
  zoom_range: 0.4
  brightness_range: 0.3
  flip_probability: 0.7
```

## Fast Training Configuration (Quick Prototyping)
Use for rapid iteration and testing:

```yaml
model:
  backbone: mobilenetv2
  pretrained: true
  use_attention: false

training:
  epochs: 30
  learning_rate: 0.001
  batch_size: 64
  optimizer: adam
  scheduler: step
  early_stopping_patience: 10

data:
  batch_size: 64
  augmentation: false

augmentation:
  rotation_range: 15
  flip_probability: 0.3
```

## Production Configuration (Balanced)
Use for deployment:

```yaml
model:
  backbone: efficientnet_b0
  pretrained: true
  use_attention: true
  attention_type: cross_gated_multipath

training:
  epochs: 100
  learning_rate: 0.0005
  optimizer: adam
  scheduler: cosine
  early_stopping_patience: 15
  use_gate_consistency_loss: true

data:
  batch_size: 32
  augmentation: true

augmentation:
  rotation_range: 30
  shift_range: 0.2
  zoom_range: 0.3
  brightness_range: 0.2
  flip_probability: 0.5
```

## Lightweight Model Configuration (Mobile/Edge Deployment)
Use for constrained environments:

```yaml
model:
  backbone: mobilenetv2
  pretrained: true
  use_attention: false
  dropout_rate: 0.2

training:
  epochs: 100
  learning_rate: 0.001
  weight_decay: 0.0001
  optimizer: adam
  scheduler: cosine

data:
  batch_size: 32
  image_size: 224

augmentation:
  rotation_range: 20
  zoom_range: 0.2
  flip_probability: 0.5
```

## Large Dataset Configuration (Computational Resources Available)
Use with sufficient GPU memory:

```yaml
model:
  backbone: efficientnet_b0
  use_attention: true
  attention_type: cross_gated_multipath

training:
  epochs: 200
  learning_rate: 0.0002
  batch_size: 128
  optimizer: adam
  scheduler: cosine
  warmup_epochs: 5
  use_gate_consistency_loss: true
  mixed_precision: true

data:
  batch_size: 128
  num_workers: 8
  augmentation: true

augmentation:
  rotation_range: 45
  shift_range: 0.3
  zoom_range: 0.4
  brightness_range: 0.3
  gaussian_noise: true
  flip_probability: 0.7
```

## Small Dataset Configuration (Limited Samples)
Use when training data is limited:

```yaml
model:
  backbone: efficientnet_b0
  pretrained: true
  use_attention: true
  dropout_rate: 0.5

training:
  epochs: 150
  learning_rate: 0.001
  weight_decay: 0.0001
  optimizer: adam
  scheduler: cosine
  early_stopping_patience: 20
  use_gate_consistency_loss: true
  gate_consistency_weight: 0.1

data:
  batch_size: 16
  augmentation: true

augmentation:
  rotation_range: 60
  shift_range: 0.4
  zoom_range: 0.5
  brightness_range: 0.4
  flip_probability: 0.8
  elastic_deformation: true
```

## Class Imbalance Configuration
Use when dataset has skewed class distribution:

```yaml
model:
  backbone: efficientnet_b0
  pretrained: true
  use_attention: true

training:
  epochs: 120
  learning_rate: 0.0005
  loss_function: focal_loss
  optimizer: adam
  scheduler: cosine
  early_stopping_patience: 20
  use_gate_consistency_loss: true

data:
  batch_size: 32

augmentation:
  rotation_range: 45
  zoom_range: 0.4
  flip_probability: 0.7
```

## Transfer Learning Configuration (Pretrained Models)
Use for domain adaptation:

```yaml
model:
  backbone: efficientnet_b0
  pretrained: true
  use_attention: true
  dropout_rate: 0.3

training:
  epochs: 50
  learning_rate: 0.0001
  weight_decay: 0.00001
  optimizer: adam
  scheduler: step
  early_stopping_patience: 15

data:
  batch_size: 32
  augmentation: true

augmentation:
  rotation_range: 15
  shift_range: 0.1
  zoom_range: 0.2
  flip_probability: 0.5
```

## Hyperparameter Search Configuration
Use for AutoML/Optuna optimization:

```yaml
# Optuna search space (in code)
hp_ranges:
  learning_rate: [0.0001, 0.001]
  batch_size: [16, 32, 64]
  weight_decay: [0.00001, 0.0001]
  dropout_rate: [0.2, 0.5]
  rotation_range: [15, 45]
  zoom_range: [0.2, 0.4]
  gate_consistency_weight: [0.05, 0.2]
```

## Tips for Configuration Selection

### Choose Configuration Based On:
1. **Hardware**: GPU memory determines batch size
2. **Dataset Size**: More data allows larger models and batches
3. **Time Budget**: Limited time requires smaller models/epochs
4. **Accuracy Requirements**: Higher accuracy needs more complex models
5. **Deployment Target**: Edge devices need lightweight models

### Tuning Strategy:
1. Start with **Balanced** configuration
2. Monitor validation metrics
3. If overfitting: increase dropout, augmentation, weight decay
4. If underfitting: reduce dropout, complexity, add regularization
5. If too slow: reduce batch size, use MobileNetV2
6. If too slow training: reduce epochs, use smaller model

### Common Issues and Fixes:

| Issue | Solution |
|-------|----------|
| Out of memory | Reduce batch_size, use MobileNetV2 |
| Not converging | Reduce learning_rate, increase epochs |
| Overfitting | Increase dropout, augmentation, weight_decay |
| Underfitting | Increase model complexity, reduce augmentation |
| Slow training | Use smaller model, increase batch_size |
| Low accuracy | Increase epochs, add attention, better augmentation |

## Performance Comparison

| Config | Accuracy | Speed | Memory |
|--------|----------|-------|--------|
| High Accuracy | 95% | 1x | 6GB |
| Fast | 85% | 8x | 2GB |
| Production | 92% | 3x | 4GB |
| Lightweight | 88% | 10x | 1GB |

Choose based on your requirements and constraints!
