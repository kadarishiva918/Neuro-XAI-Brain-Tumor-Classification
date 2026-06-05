# Brain Tumor Classification - Usage Guide

## Quick Start

### 1. Inference Script

Classify brain tumor images using the command line.

**Single Image:**
```bash
python inference.py --image path/to/image.jpg --device cpu
```

**With Explanations:**
```bash
python inference.py --image path/to/image.jpg --device cpu --explain --method gradcam
```

**Batch Processing:**
```bash
python inference.py --image-dir data/raw/glioma --device cpu --output results.json
```

**Options:**
- `--model-path`: Path to trained model (default: `models/best_model.pth`)
- `--image`: Single image path
- `--image-dir`: Directory with images
- `--device`: `cpu` or `cuda` (default: `cpu`)
- `--explain`: Generate explanations
- `--method`: `gradcam`, `lime`, or `all`
- `--output`: Save results to JSON file

**Output:**
```json
{
  "predicted_class": 0,
  "predicted_label": "Glioma",
  "confidence": 0.95,
  "probabilities": {
    "Glioma": 0.95,
    "Meningioma": 0.03,
    "Pituitary": 0.01,
    "No Tumor": 0.01
  }
}
```

---

### 2. Jupyter Notebook Demo

Interactive exploration with visualizations.

```bash
jupyter notebook notebooks/demo.ipynb
```

**Features:**
- Load trained model
- Display sample predictions
- Visualize confidence scores
- Generate Grad-CAM heatmaps
- Analyze probability distributions
- Interactive explanations

---

### 3. Flask REST API

Start the model server for production deployment.

**Start Server:**
```bash
python api.py
```

Server runs at `http://localhost:5000`

**API Endpoints:**

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Get Classes
```bash
curl http://localhost:5000/classes
```

#### Single Prediction
```bash
curl -X POST -F "image=@path/to/image.jpg" \
  http://localhost:5000/predict
```

**Response:**
```json
{
  "filename": "image.jpg",
  "predicted_class": 0,
  "predicted_label": "Glioma",
  "confidence": 0.95,
  "probabilities": {
    "Glioma": 0.95,
    "Meningioma": 0.03,
    "Pituitary": 0.01,
    "No Tumor": 0.01
  }
}
```

#### Base64 Prediction
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_string"}' \
  http://localhost:5000/predict-base64
```

#### Grad-CAM Explanation
```bash
curl -X POST -F "image=@path/to/image.jpg" \
  http://localhost:5000/explain
```

**Response:**
```json
{
  "filename": "image.jpg",
  "predicted_class": 0,
  "predicted_label": "Glioma",
  "confidence": 0.95,
  "heatmap": "base64_encoded_heatmap",
  "probabilities": {...}
}
```

#### Batch Predictions
```bash
curl -X POST -F "images=@img1.jpg" -F "images=@img2.jpg" \
  http://localhost:5000/batch-predict
```

---

## Python API Usage

### Programmatic Inference

```python
from inference import BrainTumorInferencer

# Initialize
inferencer = BrainTumorInferencer(
    model_path='models/best_model.pth',
    device='cpu'
)

# Make prediction
result, image_array, image_tensor = inferencer.predict(
    'path/to/image.jpg',
    return_probs=True
)

print(f"Predicted: {result['predicted_label']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Probabilities: {result['probabilities']}")

# Generate explanation
explanation = inferencer.explain(
    'path/to/image.jpg',
    method='gradcam'
)

print(explanation['explanations']['gradcam'])
```

---

## Docker Deployment

### Build Docker Image

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy model and code
COPY models/ models/
COPY src/ src/
COPY configs/ configs/
COPY api.py .

# Expose port
EXPOSE 5000

# Run API
CMD ["python", "api.py"]
```

**Build:**
```bash
docker build -t brain-tumor-api:latest .
```

**Run:**
```bash
docker run -p 5000:5000 brain-tumor-api:latest
```

---

## Performance Optimization

### GPU Acceleration

```bash
python inference.py --image image.jpg --device cuda
python api.py  # Auto-detects GPU
```

### Batch Processing (CPU)

```python
from inference import BrainTumorInferencer
import os

inferencer = BrainTumorInferencer(device='cpu')

# Process directory
image_dir = 'data/raw/glioma'
for img_file in os.listdir(image_dir):
    result, _, _ = inferencer.predict(f'{image_dir}/{img_file}')
    print(f"{img_file}: {result['predicted_label']}")
```

---

## Troubleshooting

### Model Loading Issues

**Error: "No such file or directory: models/best_model.pth"**
- Ensure training completed successfully
- Check model checkpoint location
- Verify file exists: `ls -la models/best_model.pth`

### Memory Issues

**Error: "CUDA out of memory"**
- Use `--device cpu` for inference
- Reduce batch size in API settings
- Process images sequentially

### Slow Inference

**On CPU:**
- Normal inference time: 1-2 seconds per image
- Use GPU for faster processing
- Consider model quantization for deployment

---

## Integration Examples

### Web Application (Flask + HTML)

```python
from flask import Flask, render_template, request
from inference import BrainTumorInferencer

app = Flask(__name__)
inferencer = BrainTumorInferencer('models/best_model.pth')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    result, _, _ = inferencer.predict(file)
    return render_template('result.html', result=result)
```

### Command Line Tool

```bash
# Classify all images in directory
for img in data/raw/glioma/*.jpg; do
  python inference.py --image "$img" --device cpu
done
```

### Batch Script

```bash
#!/bin/bash
python inference.py --image-dir data/raw/glioma --output glioma_results.json
python inference.py --image-dir data/raw/meningioma --output meningioma_results.json
```

---

## Model Information

### Architecture
- **Backbone**: EfficientNet-B0 (pretrained)
- **Attention**: Cross-Gated Multi-Path Attention
- **Input Size**: 224 × 224 pixels
- **Classes**: 4 (Glioma, Meningioma, Pituitary, No Tumor)

### Performance
- **Parameters**: ~4.9M
- **Training Data**: 5,006 images
- **Inference Speed**: 
  - GPU: ~50ms per image
  - CPU: ~1-2 seconds per image

### Requirements
- Python 3.8+
- PyTorch 2.0+
- CUDA 11.8+ (for GPU, optional)

---

## Support and Documentation

- **README**: `README.md` - Project overview
- **Completion Report**: `PROJECT_COMPLETION_REPORT.md` - Implementation details
- **Configuration**: `configs/config.yaml` - Model and training settings
- **Source Code**: `src/` - Implementation modules

---

**For more information**, refer to the project documentation and code comments.
