#!/usr/bin/env python3
"""Inference script for brain tumor classification with explanations."""

import os
import sys
import torch
import argparse
import numpy as np
import cv2
from pathlib import Path
from PIL import Image
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from utils.config import Config
from xai.explainers import GradCAMExplainer, SHAPExplainer, LIMEExplainer

class BrainTumorInferencer:
    """Brain tumor classification inference with explanations."""
    
    def __init__(self, model_path, config_path='configs/config.yaml', device='cpu'):
        """Initialize inferencer with model and config."""
        self.device = torch.device(device)
        self.config = Config(config_path)
        
        # Create model
        self.model = BrainTumorClassifier(
            backbone=self.config.model['backbone'],
            num_classes=self.config.model['num_classes'],
            pretrained=False,
            use_attention=self.config.model['use_attention']
        )
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Class names
        self.class_names = ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
        
        # Explainers
        self.gradcam = GradCAMExplainer(self.model)
        self.shap_explainer = SHAPExplainer(self.model)
        self.lime_explainer = LIMEExplainer(self.model)
        
    def preprocess_image(self, image_path):
        """Load and preprocess image."""
        if isinstance(image_path, str):
            image = Image.open(image_path).convert('RGB')
        else:
            image = image_path
        
        # Resize
        image = image.resize((self.config.data['image_size'], self.config.data['image_size']))
        
        # Convert to tensor
        image_array = np.array(image) / 255.0
        image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).float()
        
        # Normalize
        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        
        return image_tensor, image_array
    
    def predict(self, image_path, return_probs=False):
        """Get prediction for image."""
        image_tensor, image_array = self.preprocess_image(image_path)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0].cpu().numpy()
            predicted_class = torch.argmax(outputs, dim=1).item()
        
        result = {
            'predicted_class': predicted_class,
            'predicted_label': self.class_names[predicted_class],
            'confidence': float(probabilities[predicted_class]),
        }
        
        if return_probs:
            result['probabilities'] = {
                self.class_names[i]: float(probabilities[i]) 
                for i in range(len(self.class_names))
            }
        
        return result, image_array, image_tensor
    
    def explain(self, image_path, method='gradcam'):
        """Generate explanation for prediction."""
        result, image_array, image_tensor = self.predict(image_path, return_probs=True)
        
        explanation = {
            'prediction': result,
            'explanations': {}
        }
        
        # Grad-CAM
        if method in ['gradcam', 'all']:
            try:
                heatmap = self.gradcam.explain(image_tensor, result['predicted_class'])
                explanation['explanations']['gradcam'] = {
                    'method': 'Grad-CAM',
                    'heatmap': heatmap.cpu().numpy().tolist() if isinstance(heatmap, torch.Tensor) else heatmap
                }
            except Exception as e:
                explanation['explanations']['gradcam'] = {'error': str(e)}
        
        # LIME
        if method in ['lime', 'all']:
            try:
                lime_result = self.lime_explainer.explain(image_array, result['predicted_class'])
                explanation['explanations']['lime'] = {
                    'method': 'LIME',
                    'result': str(lime_result)[:200]  # Truncate for JSON
                }
            except Exception as e:
                explanation['explanations']['lime'] = {'error': str(e)}
        
        return explanation

def main():
    parser = argparse.ArgumentParser(description='Brain tumor classification inference')
    parser.add_argument('--model-path', type=str, default='models/best_model.pth',
                       help='Path to trained model')
    parser.add_argument('--image', type=str, help='Path to image for inference')
    parser.add_argument('--image-dir', type=str, help='Directory with images to process')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'])
    parser.add_argument('--explain', action='store_true', help='Generate explanations')
    parser.add_argument('--method', type=str, default='gradcam',
                       choices=['gradcam', 'lime', 'all'])
    parser.add_argument('--output', type=str, help='Save results to JSON')
    
    args = parser.parse_args()
    
    # Initialize inferencer
    print("Initializing model...")
    inferencer = BrainTumorInferencer(args.model_path, device=args.device)
    
    results = []
    
    # Single image
    if args.image:
        print(f"Processing: {args.image}")
        result, _, _ = inferencer.predict(args.image, return_probs=True)
        print(f"  Predicted: {result['predicted_label']} ({result['confidence']:.2%})")
        
        if args.explain:
            print("  Generating explanations...")
            explanation = inferencer.explain(args.image, method=args.method)
            results.append(explanation)
        else:
            results.append(result)
    
    # Directory of images
    elif args.image_dir:
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.PNG'}
        image_files = [f for f in os.listdir(args.image_dir) 
                      if Path(f).suffix in image_extensions]
        
        print(f"Processing {len(image_files)} images from {args.image_dir}")
        
        for i, img_file in enumerate(image_files, 1):
            img_path = os.path.join(args.image_dir, img_file)
            print(f"  [{i}/{len(image_files)}] {img_file}")
            
            try:
                result, _, _ = inferencer.predict(img_path, return_probs=True)
                print(f"    -> {result['predicted_label']} ({result['confidence']:.2%})")
                results.append({'image': img_file, **result})
            except Exception as e:
                print(f"    ERROR: {e}")
                results.append({'image': img_file, 'error': str(e)})
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Print summary
    if isinstance(results[0], dict) and 'predicted_label' in results[0]:
        class_counts = {}
        for r in results:
            if 'predicted_label' in r:
                label = r['predicted_label']
                class_counts[label] = class_counts.get(label, 0) + 1
        
        print("\n=== Summary ===")
        for label, count in class_counts.items():
            print(f"{label}: {count}")

if __name__ == '__main__':
    main()
