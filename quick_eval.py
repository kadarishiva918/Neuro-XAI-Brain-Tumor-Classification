#!/usr/bin/env python3
"""Quick evaluation on a sample of test data."""

import os
import sys
import torch
import argparse
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.data_loader import BrainTumorDataset
from models.model import BrainTumorClassifier
from utils.config import Config

def main():
    parser = argparse.ArgumentParser(description='Quick evaluation')
    parser.add_argument('--model-path', type=str, default='models/best_model.pth')
    parser.add_argument('--data-dir', type=str, default='data/raw')
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--num-samples', type=int, default=100)
    args = parser.parse_args()

    # Load config
    config = Config('configs/config.yaml')
    
    # Device
    device = torch.device(args.device)
    
    # Create model
    print("Creating model...")
    model = BrainTumorClassifier(
        backbone=config.model['backbone'],
        num_classes=config.model['num_classes'],
        pretrained=config.model['pretrained'],
        use_attention=config.model['use_attention']
    )
    
    # Load checkpoint
    print(f"Loading model from {args.model_path}...")
    checkpoint = torch.load(args.model_path, map_location=device)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()
    
    # Load test data
    print("Loading test dataset...")
    test_dataset = BrainTumorDataset(
        data_dir=args.data_dir,
        split='test',
        image_size=config.data['image_size'],
        augment=False
    )
    
    # Sample subset
    indices = np.random.choice(len(test_dataset), min(args.num_samples, len(test_dataset)), replace=False)
    
    # Evaluate
    correct = 0
    total = 0
    
    print(f"Evaluating on {len(indices)} samples...")
    with torch.no_grad():
        for i, idx in enumerate(indices):
            if (i + 1) % 10 == 0:
                print(f"  {i + 1}/{len(indices)}")
            
            image, label = test_dataset[idx]
            image = image.unsqueeze(0).to(device)
            
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            
            if predicted.item() == label:
                correct += 1
            total += 1
    
    accuracy = 100 * correct / total
    print(f"\n=== Quick Evaluation Results ===")
    print(f"Accuracy on {total} samples: {accuracy:.2f}%")
    print(f"Correct: {correct}/{total}")

if __name__ == '__main__':
    main()
