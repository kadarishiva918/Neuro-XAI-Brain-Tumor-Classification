#!/usr/bin/env python3
"""Quantization-Aware Training (QAT) for brain tumor classification model."""

import torch
import torch.nn as nn
import torch.quantization as quantization
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from data.data_loader import BrainTumorDataset
from utils.config import Config

class QuantizationAwareTrainer:
    """Train model with quantization awareness."""
    
    def __init__(self, model, config_path='configs/config.yaml', device='cpu'):
        """Initialize QAT trainer."""
        self.model = model
        self.device = torch.device(device)
        self.config = Config(config_path)
        self.model = self.model.to(self.device)
        
        # Prepare model for QAT
        self.model.qconfig = quantization.get_default_qat_qconfig('fbgemm')
        quantization.prepare_qat(self.model, inplace=True)
    
    def calibrate(self, train_loader, num_batches=100):
        """Calibrate model on training data."""
        print(f"Calibrating on {num_batches} batches...")
        
        self.model.eval()
        with torch.no_grad():
            for i, (images, _) in enumerate(train_loader):
                if i >= num_batches:
                    break
                images = images.to(self.device)
                _ = self.model(images)
        
        print("✅ Calibration complete")
    
    def convert_to_quantized(self):
        """Convert QAT model to quantized model."""
        print("Converting to quantized model...")
        
        quantization.convert(self.model, inplace=True)
        self.model.eval()
        
        print("✅ Model converted to quantized version")
        return self.model
    
    def fine_tune(self, train_loader, epochs=5, learning_rate=1e-5):
        """Fine-tune quantized model."""
        print(f"Fine-tuning quantized model for {epochs} epochs...")
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
            for images, labels in pbar:
                images, labels = images.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                pbar.set_postfix({'loss': loss.item()})
            
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}: Average Loss = {avg_loss:.4f}")
        
        print("✅ Fine-tuning complete")

class QuantizationAnalyzer:
    """Analyze quantization effects on model."""
    
    @staticmethod
    def compare_models(original_model, quantized_model, test_loader, device='cpu'):
        """Compare original and quantized models."""
        device = torch.device(device)
        
        print("\n" + "="*60)
        print("QUANTIZATION ANALYSIS".center(60))
        print("="*60)
        
        original_model = original_model.to(device)
        quantized_model = quantized_model.to(device)
        
        original_model.eval()
        quantized_model.eval()
        
        correct_original = 0
        correct_quantized = 0
        total = 0
        differences = []
        
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                
                # Original predictions
                orig_outputs = original_model(images)
                orig_preds = torch.argmax(orig_outputs, dim=1)
                
                # Quantized predictions
                quant_outputs = quantized_model(images)
                quant_preds = torch.argmax(quant_outputs, dim=1)
                
                correct_original += (orig_preds == labels).sum().item()
                correct_quantized += (quant_preds == labels).sum().item()
                total += labels.size(0)
                
                # Calculate differences
                diff = torch.abs(orig_outputs - quant_outputs).mean().item()
                differences.append(diff)
        
        orig_acc = 100 * correct_original / total
        quant_acc = 100 * correct_quantized / total
        acc_drop = orig_acc - quant_acc
        avg_diff = sum(differences) / len(differences)
        
        print(f"\nModel Accuracies:")
        print(f"  Original Model: {orig_acc:.2f}%")
        print(f"  Quantized Model: {quant_acc:.2f}%")
        print(f"  Accuracy Drop: {acc_drop:.2f}%")
        
        print(f"\nOutput Differences:")
        print(f"  Average Difference: {avg_diff:.6f}")
        print(f"  Max Difference: {max(differences):.6f}")
        print(f"  Min Difference: {min(differences):.6f}")
        
        print("\n" + "="*60)
        
        return {
            'original_accuracy': orig_acc,
            'quantized_accuracy': quant_acc,
            'accuracy_drop': acc_drop,
            'avg_output_diff': avg_diff,
            'max_output_diff': max(differences),
            'min_output_diff': min(differences)
        }
    
    @staticmethod
    def get_model_sizes(original_model, quantized_model):
        """Compare model sizes."""
        import tempfile
        import os
        
        # Save models
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pth') as f:
            torch.save(original_model, f.name)
            original_size = os.path.getsize(f.name) / (1024*1024)
            os.unlink(f.name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pth') as f:
            torch.save(quantized_model, f.name)
            quantized_size = os.path.getsize(f.name) / (1024*1024)
            os.unlink(f.name)
        
        compression_ratio = original_size / quantized_size
        size_reduction = (1 - quantized_size / original_size) * 100
        
        print("\nModel Sizes:")
        print(f"  Original: {original_size:.2f} MB")
        print(f"  Quantized: {quantized_size:.2f} MB")
        print(f"  Compression Ratio: {compression_ratio:.2f}x")
        print(f"  Size Reduction: {size_reduction:.1f}%")
        
        return {
            'original_size_mb': original_size,
            'quantized_size_mb': quantized_size,
            'compression_ratio': compression_ratio,
            'size_reduction_percent': size_reduction
        }

class StaticQuantizer:
    """Post-training static quantization."""
    
    @staticmethod
    def quantize_static(model, calibration_loader, device='cpu'):
        """Perform static quantization."""
        device = torch.device(device)
        
        print("Performing static quantization...")
        
        # Set quantization config
        model.qconfig = quantization.get_default_qconfig('fbgemm')
        quantization.prepare(model, inplace=True)
        
        # Calibrate on data
        model.eval()
        with torch.no_grad():
            for images, _ in calibration_loader:
                images = images.to(device)
                _ = model(images)
        
        # Convert to quantized model
        quantization.convert(model, inplace=True)
        
        print("✅ Static quantization complete")
        return model

def main():
    """Main QAT pipeline."""
    parser = argparse.ArgumentParser(description='Quantization-Aware Training')
    parser.add_argument('--model', type=str, default='models/best_model.pth',
                       help='Path to original model')
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'])
    parser.add_argument('--qat', action='store_true',
                       help='Perform QAT fine-tuning')
    parser.add_argument('--static', action='store_true',
                       help='Perform static quantization')
    parser.add_argument('--epochs', type=int, default=5,
                       help='Fine-tuning epochs')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--output', type=str, default='models/quantized_model.pth',
                       help='Output quantized model path')
    
    args = parser.parse_args()
    
    # Load config and model
    print("Loading model...")
    config = Config('configs/config.yaml')
    
    model = BrainTumorClassifier(
        backbone=config.model['backbone'],
        num_classes=config.model['num_classes'],
        pretrained=False
    )
    
    checkpoint = torch.load(args.model, map_location=args.device)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    # Quantization-Aware Training
    if args.qat:
        print("\n" + "="*60)
        print("QUANTIZATION-AWARE TRAINING (QAT)".center(60))
        print("="*60)
        
        # Load training data
        print("Loading training data...")
        train_dataset = BrainTumorDataset(
            data_dir=args.data_dir,
            split='train',
            image_size=config.data['image_size'],
            augment=True
        )
        train_loader = DataLoader(train_dataset, batch_size=args.batch_size)
        
        # QAT training
        trainer = QuantizationAwareTrainer(model, device=args.device)
        trainer.calibrate(train_loader)
        quantized_model = trainer.convert_to_quantized()
        trainer.fine_tune(train_loader, epochs=args.epochs)
        
        # Save quantized model
        torch.save(quantized_model, args.output)
        print(f"✅ Quantized model saved to {args.output}")
    
    # Static Quantization
    elif args.static:
        print("\n" + "="*60)
        print("STATIC QUANTIZATION".center(60))
        print("="*60)
        
        # Load calibration data
        print("Loading calibration data...")
        calib_dataset = BrainTumorDataset(
            data_dir=args.data_dir,
            split='test',
            image_size=config.data['image_size'],
            augment=False
        )
        calib_loader = DataLoader(calib_dataset, batch_size=args.batch_size)
        
        # Static quantization
        quantized_model = StaticQuantizer.quantize_static(
            model, calib_loader, device=args.device
        )
        
        # Save quantized model
        torch.save(quantized_model, args.output)
        print(f"✅ Quantized model saved to {args.output}")

if __name__ == '__main__':
    main()
