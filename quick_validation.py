#!/usr/bin/env python3
"""Quick validation of system components."""

import sys
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("QUICK VALIDATION TEST SUITE".center(70))
print("=" * 70)

# Test 1: Model Loading
print("\n[1/5] Testing Model Loading...")
try:
    from models.model import BrainTumorClassifier
    from utils.config import ConfigLoader
    
    config = ConfigLoader.load_config('configs/config.yaml')
    device = torch.device('cpu')
    
    model = BrainTumorClassifier(
        backbone=config['model']['backbone'],
        num_classes=config['model']['num_classes'],
        pretrained=False,
        use_attention=config['model']['use_attention']
    )
    checkpoint = torch.load('models/best_model.pth', map_location=device)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model = model.to(device)
    model.eval()
    print("   ✅ Model loaded successfully")
except Exception as e:
    print(f"   ❌ Model loading failed: {e}")

# Test 2: Forward Pass
print("\n[2/5] Testing Forward Pass...")
try:
    x = torch.randn(1, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(x)
        # Handle attention model output (returns tuple)
        if isinstance(output, tuple):
            output = output[0]
    print(f"   ✅ Forward pass successful - Output shape: {output.shape}")
except Exception as e:
    print(f"   ❌ Forward pass failed: {e}")

# Test 3: Inference
print("\n[3/5] Testing Inference...")
try:
    x = torch.randn(1, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(x)
        # Handle attention model output (returns tuple)
        if isinstance(output, tuple):
            output = output[0]
        probabilities = torch.softmax(output, dim=1)[0].cpu().numpy()
        predicted_class = torch.argmax(output, dim=1).item()
    
    class_names = ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
    print(f"   ✅ Inference successful")
    print(f"      Predicted: {class_names[predicted_class]} ({probabilities[predicted_class]:.2%})")
except Exception as e:
    print(f"   ❌ Inference failed: {e}")

# Test 4: XAI (Grad-CAM)
print("\n[4/5] Testing Explainability (Grad-CAM)...")
try:
    from xai.explainers import GradCAMExplainer
    
    gradcam = GradCAMExplainer(model)
    x = torch.randn(1, 3, 224, 224).to(device)
    heatmap = gradcam.explain(x, predicted_class)
    print(f"   ✅ Grad-CAM explanation generated - Shape: {heatmap.shape}")
except Exception as e:
    print(f"   ❌ Grad-CAM failed: {e}")

# Test 5: API Health
print("\n[5/5] Testing API Health...")
try:
    import requests
    response = requests.get('http://localhost:5000/health', timeout=5)
    if response.status_code == 200:
        print(f"   ✅ API is healthy: {response.json()}")
    else:
        print(f"   ❌ API returned status {response.status_code}")
except Exception as e:
    print(f"   ⚠️  API not responding (ensure it's running): {e}")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE".center(70))
print("=" * 70)
