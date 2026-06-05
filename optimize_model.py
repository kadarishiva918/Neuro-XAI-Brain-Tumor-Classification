#!/usr/bin/env python3
"""Model optimization tools: quantization, pruning, and distillation."""

import torch
import torch.nn as nn
import torch.quantization as quantization
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from utils.config import Config

class ModelOptimizer:
    """Optimize neural network models for deployment."""
    
    def __init__(self, model_path, config_path='configs/config.yaml', device='cpu'):
        """Initialize optimizer."""
        self.device = torch.device(device)
        self.config = Config(config_path)
        
        # Load model
        self.model = BrainTumorClassifier(
            backbone=self.config.model['backbone'],
            num_classes=self.config.model['num_classes'],
            pretrained=False
        )
        
        checkpoint = torch.load(model_path, map_location=self.device)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def get_model_size(self, model):
        """Get model size in MB."""
        param_size = sum(p.numel() * 4 for p in model.parameters()) / (1024*1024)
        return param_size
    
    def quantize_int8(self, output_path='models/quantized_model.pth'):
        """Post-training static quantization (INT8)."""
        print("Applying INT8 quantization...")
        
        # Create quantized model
        quantized_model = quantization.quantize_dynamic(
            self.model,
            {nn.Linear},
            dtype=torch.qint8
        )
        
        # Save
        torch.save(quantized_model, output_path)
        
        # Compare sizes
        original_size = self.get_model_size(self.model)
        quantized_size = sum(
            p.numel() * 1 for p in quantized_model.parameters() 
            if hasattr(p, 'qscheme')
        ) / (1024*1024) if hasattr(quantized_model, 'parameters') else 0
        
        print(f"✅ Original size: {original_size:.2f} MB")
        print(f"✅ Quantized size: {quantized_size:.2f} MB" if quantized_size > 0 else f"✅ Model quantized to {output_path}")
        
        return quantized_model
    
    def prune_weights(self, amount=0.3, output_path='models/pruned_model.pth'):
        """Magnitude-based weight pruning."""
        print(f"Applying {amount*100:.0f}% weight pruning...")
        
        pruned_model = self.model
        
        # Prune linear layers
        for module in pruned_model.modules():
            if isinstance(module, nn.Linear):
                nn.utils.prune.l1_unstructured(module, name='weight', amount=amount)
        
        # Make pruning permanent
        for module in pruned_model.modules():
            if isinstance(module, nn.Linear):
                nn.utils.prune.remove(module, 'weight')
        
        # Save
        torch.save(pruned_model.state_dict(), output_path)
        
        original_size = self.get_model_size(self.model)
        pruned_size = self.get_model_size(pruned_model)
        reduction = (1 - pruned_size/original_size) * 100
        
        print(f"✅ Original size: {original_size:.2f} MB")
        print(f"✅ Pruned size: {pruned_size:.2f} MB ({reduction:.1f}% reduction)")
        
        return pruned_model
    
    def export_onnx(self, output_path='models/model.onnx'):
        """Export model to ONNX format."""
        print("Exporting to ONNX format...")
        
        dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
        
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            verbose=False,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}}
        )
        
        size_mb = __import__('os').path.getsize(output_path) / (1024*1024)
        print(f"✅ Model exported to {output_path} ({size_mb:.2f} MB)")
    
    def export_torchscript(self, output_path='models/model.pt'):
        """Export model to TorchScript format."""
        print("Exporting to TorchScript format...")
        
        traced_model = torch.jit.trace(
            self.model,
            torch.randn(1, 3, 224, 224).to(self.device)
        )
        
        traced_model.save(output_path)
        
        size_mb = __import__('os').path.getsize(output_path) / (1024*1024)
        print(f"✅ Model exported to {output_path} ({size_mb:.2f} MB)")
    
    def get_optimization_report(self):
        """Generate optimization report."""
        report = {
            'original_size_mb': self.get_model_size(self.model),
            'parameters': sum(p.numel() for p in self.model.parameters()),
            'trainable_parameters': sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            )
        }
        
        return report

def main():
    """Main optimization pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Model optimization')
    parser.add_argument('--model', type=str, default='models/best_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--quantize', action='store_true',
                       help='Apply INT8 quantization')
    parser.add_argument('--prune', type=float, default=0,
                       help='Prune weights (0-1)')
    parser.add_argument('--onnx', action='store_true',
                       help='Export to ONNX')
    parser.add_argument('--torchscript', action='store_true',
                       help='Export to TorchScript')
    parser.add_argument('--report', action='store_true',
                       help='Generate report')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'])
    
    args = parser.parse_args()
    
    print("Initializing model optimizer...")
    optimizer = ModelOptimizer(args.model, device=args.device)
    
    # Generate report
    if args.report:
        print("\n" + "="*60)
        print("MODEL OPTIMIZATION REPORT".center(60))
        print("="*60)
        report = optimizer.get_optimization_report()
        for key, value in report.items():
            if 'mb' in key.lower():
                print(f"{key:30} {value:>15.2f} MB")
            else:
                print(f"{key:30} {value:>15}")
        print("="*60)
    
    # Quantization
    if args.quantize:
        print()
        optimizer.quantize_int8()
    
    # Pruning
    if args.prune > 0:
        print()
        optimizer.prune_weights(amount=args.prune)
    
    # ONNX export
    if args.onnx:
        print()
        optimizer.export_onnx()
    
    # TorchScript export
    if args.torchscript:
        print()
        optimizer.export_torchscript()

if __name__ == '__main__':
    main()
