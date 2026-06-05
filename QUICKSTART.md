# Quick Start Guide

## Setup (First Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset
Place your brain tumor MRI images in the following structure:
```
data/raw/
├── glioma/
│   ├── image_001.jpg
│   └── ...
├── meningioma/
│   ├── image_001.jpg
│   └── ...
├── pituitary/
│   ├── image_001.jpg
│   └── ...
└── no_tumor/
    ├── image_001.jpg
    └── ...
```

## Training

### Basic Training
```bash
python train.py --data-dir data/raw
```

### With Custom Configuration
```bash
python train.py --config configs/config.yaml --data-dir data/raw --device cuda
```

### Resume Training from Checkpoint
```bash
python train.py --data-dir data/raw --resume models/best_model.pth
```

### Training Options
- `--config`: Path to configuration file (default: configs/config.yaml)
- `--data-dir`: Path to dataset (default: data/raw)
- `--output-dir`: Output directory (default: results)
- `--device`: Use 'cuda' or 'cpu' (default: cuda)
- `--resume`: Resume from checkpoint

## Evaluation

### Evaluate Trained Model
```bash
python evaluate.py --model-path models/best_model.pth --data-dir data/raw
```

This generates:
- Classification metrics
- Confusion matrix
- ROC curves
- Detailed reports

## Generate Explanations

### Generate XAI Explanations
```bash
python generate_explanations.py --model-path models/best_model.pth --data-dir data/raw
```

This generates:
- Grad-CAM visualizations
- SHAP explanations
- LIME interpretations
- XAI summary report

### Explanation Options
- `--num-samples`: Number of samples per class (default: 5)
- `--output-dir`: XAI output directory (default: results/xai)

## Output Files

After training, check these directories:

### Models
- `models/best_model.pth` - Best trained model
- `models/checkpoint_epoch_*.pth` - Periodic checkpoints

### Results
- `results/logs/` - TensorBoard logs (view with `tensorboard --logdir=results/logs`)
- `results/visualizations/` - Training plots and confusion matrices
- `results/test_metrics.json` - Quantitative results
- `results/xai/` - XAI explanations and visualizations

## Configuration Tips

### For Better Accuracy
```yaml
training:
  epochs: 150
  learning_rate: 0.0005
  early_stopping_patience: 20
  
augmentation:
  rotation_range: 40
  zoom_range: 0.4
```

### For Faster Training
```yaml
data:
  batch_size: 64
  
model:
  backbone: mobilenetv2
  use_attention: false
```

### For Lightweight Model
```yaml
model:
  backbone: mobilenetv2
  pretrained: true
  use_attention: false
```

## Troubleshooting

### CUDA Out of Memory
Reduce batch size in config.yaml:
```yaml
data:
  batch_size: 16  # Instead of 32
```

### Slow Data Loading
Increase number of workers:
```yaml
data:
  num_workers: 8  # Default is 4
```

### Model Not Converging
- Increase learning rate (try 0.005)
- Reduce weight decay (try 0.00001)
- Increase augmentation strength
- Check data normalization

## Performance Benchmarks

Expected results on standard datasets:
- **Accuracy**: 90-95%
- **F1-Score**: 0.88-0.93
- **Training Time**: 2-4 hours on V100 GPU
- **Inference Time**: <100ms per image

## Using the Model Programmatically

```python
import torch
from src.models.model import create_model
from src.utils.config import ConfigLoader

# Load config
config = ConfigLoader.load_config('configs/config.yaml')

# Create model
model = create_model(config)
model = model.to('cuda')

# Load checkpoint
checkpoint = torch.load('models/best_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Make prediction
with torch.no_grad():
    output, gates = model(input_image)
    prediction = torch.argmax(output, dim=1)
    confidence = torch.softmax(output, dim=1).max()
```

## Common Commands

```bash
# View TensorBoard logs
tensorboard --logdir=results/logs

# List GPU usage
nvidia-smi

# Run training with all logs
python train.py --data-dir data/raw 2>&1 | tee training.log

# Evaluate multiple models
for model in models/checkpoint_*.pth; do
    python evaluate.py --model-path $model
done
```

## Next Steps

1. Prepare your dataset
2. Adjust configuration if needed
3. Run training
4. Evaluate results
5. Generate explanations
6. Analyze visualizations

For more details, see [README.md](README.md)
