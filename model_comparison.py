#!/usr/bin/env python3
"""Model comparison and optimization analysis."""

import torch
import time
import numpy as np
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from data.data_loader import BrainTumorDataset
from torch.utils.data import DataLoader
from utils.config import Config

class ModelComparator:
    """Compare multiple model variants."""
    
    def __init__(self, device='cpu'):
        """Initialize comparator."""
        self.device = torch.device(device)
        self.config = Config('configs/config.yaml')
        self.results = defaultdict(dict)
    
    def load_model(self, model_path, model_type='full'):
        """Load a model variant."""
        print(f"Loading {model_type} model from {model_path}...")
        
        if model_type == 'full':
            model = BrainTumorClassifier(
                backbone=self.config.model['backbone'],
                num_classes=self.config.model['num_classes'],
                pretrained=False
            )
            
            checkpoint = torch.load(model_path, map_location=self.device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
        else:
            model = torch.load(model_path, map_location=self.device)
        
        return model.to(self.device).eval()
    
    def evaluate_model(self, model, test_loader, model_name='Model'):
        """Evaluate model on test set."""
        print(f"\nEvaluating {model_name}...")
        
        model.eval()
        correct = 0
        total = 0
        latencies = []
        
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                # Measure latency
                torch.cuda.synchronize() if self.device.type == 'cuda' else None
                start = time.perf_counter()
                
                outputs = model(images)
                
                torch.cuda.synchronize() if self.device.type == 'cuda' else None
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        latencies = np.array(latencies)
        
        stats = {
            'accuracy': accuracy,
            'latency_mean_ms': latencies.mean(),
            'latency_std_ms': latencies.std(),
            'latency_p95_ms': np.percentile(latencies, 95),
            'latency_p99_ms': np.percentile(latencies, 99),
            'throughput_images_per_sec': 1000 / latencies.mean()
        }
        
        self.results[model_name] = stats
        return stats
    
    def get_model_size(self, model_path):
        """Get model file size."""
        import os
        size_mb = os.path.getsize(model_path) / (1024*1024)
        return size_mb
    
    def get_parameter_count(self, model):
        """Get model parameter count."""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        return total_params, trainable_params
    
    def compare_models(self, model_configs, test_loader):
        """Compare multiple model variants.
        
        Args:
            model_configs: List of dicts with 'name', 'path', 'type' keys
            test_loader: Test data loader
        """
        print("="*80)
        print("MODEL COMPARISON ANALYSIS".center(80))
        print("="*80)
        
        comparison_data = []
        
        for config in model_configs:
            name = config['name']
            path = config['path']
            model_type = config.get('type', 'full')
            
            try:
                # Load model
                model = self.load_model(path, model_type)
                
                # Get metrics
                stats = self.evaluate_model(model, test_loader, name)
                
                # Get size
                size_mb = self.get_model_size(path)
                total_params, trainable_params = self.get_parameter_count(model)
                
                comparison_data.append({
                    'Model': name,
                    'Accuracy (%)': f"{stats['accuracy']:.2f}",
                    'Latency (ms)': f"{stats['latency_mean_ms']:.2f}",
                    'P95 (ms)': f"{stats['latency_p95_ms']:.2f}",
                    'Throughput': f"{stats['throughput_images_per_sec']:.1f}",
                    'Size (MB)': f"{size_mb:.2f}",
                    'Parameters (M)': f"{total_params/1e6:.2f}",
                })
                
            except Exception as e:
                print(f"❌ Error evaluating {name}: {e}")
        
        # Print comparison table
        self._print_comparison_table(comparison_data)
        
        return comparison_data
    
    def _print_comparison_table(self, data):
        """Print comparison table."""
        if not data:
            print("No models to compare")
            return
        
        print("\n" + "="*80)
        print("COMPARISON RESULTS".center(80))
        print("="*80)
        
        # Print header
        headers = list(data[0].keys())
        col_widths = [max(len(h), max(len(str(row[h])) for row in data)) for h in headers]
        
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in data:
            row_str = " | ".join(str(row[h]).ljust(w) for h, w in zip(headers, col_widths))
            print(row_str)
        
        print("="*80)
    
    def export_comparison(self, data, output_file='model_comparison.json'):
        """Export comparison results."""
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Comparison exported to {output_file}")

class OptimizationRecommendations:
    """Generate optimization recommendations."""
    
    @staticmethod
    def analyze_model(model, latency_ms, accuracy, model_size_mb):
        """Generate optimization recommendations."""
        recommendations = []
        
        # Latency analysis
        if latency_ms > 1000:
            recommendations.append({
                'issue': 'High latency',
                'value': f"{latency_ms:.0f}ms",
                'recommendation': 'Apply quantization or knowledge distillation'
            })
        
        if latency_ms > 500:
            recommendations.append({
                'issue': 'Moderate latency',
                'value': f"{latency_ms:.0f}ms",
                'recommendation': 'Consider INT8 quantization'
            })
        
        # Accuracy analysis
        if accuracy < 85:
            recommendations.append({
                'issue': 'Low accuracy',
                'value': f"{accuracy:.2f}%",
                'recommendation': 'Retrain with more data or longer training'
            })
        
        # Model size analysis
        if model_size_mb > 300:
            recommendations.append({
                'issue': 'Large model size',
                'value': f"{model_size_mb:.0f}MB",
                'recommendation': 'Apply pruning or knowledge distillation'
            })
        
        if model_size_mb > 500:
            recommendations.append({
                'issue': 'Very large model size',
                'value': f"{model_size_mb:.0f}MB",
                'recommendation': 'Apply aggressive quantization + pruning'
            })
        
        # Parameter count analysis
        total_params = sum(p.numel() for p in model.parameters())
        if total_params > 10e6:
            recommendations.append({
                'issue': 'Many parameters',
                'value': f"{total_params/1e6:.1f}M",
                'recommendation': 'Use knowledge distillation for compression'
            })
        
        return recommendations
    
    @staticmethod
    def print_recommendations(recommendations):
        """Print recommendations."""
        if not recommendations:
            print("✅ Model is well-optimized! No major recommendations.")
            return
        
        print("\n" + "="*60)
        print("OPTIMIZATION RECOMMENDATIONS".center(60))
        print("="*60)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['issue'].upper()}")
            print(f"   Current: {rec['value']}")
            print(f"   Action: {rec['recommendation']}")
        
        print("\n" + "="*60)

def main():
    """Main comparison pipeline."""
    parser = argparse.ArgumentParser(description='Model Comparison and Analysis')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'])
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for evaluation')
    parser.add_argument('--models', type=str, nargs='+',
                       default=['models/best_model.pth'],
                       help='Paths to models to compare')
    parser.add_argument('--names', type=str, nargs='+',
                       help='Model names for display')
    parser.add_argument('--output', type=str, default='model_comparison.json',
                       help='Output file for comparison results')
    parser.add_argument('--recommendations', action='store_true',
                       help='Generate optimization recommendations')
    
    args = parser.parse_args()
    
    # Load test data
    print("Loading test data...")
    config = Config('configs/config.yaml')
    test_dataset = BrainTumorDataset(
        data_dir=args.data_dir,
        split='test',
        image_size=config.data['image_size'],
        augment=False
    )
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size)
    
    # Prepare model configs
    model_configs = []
    names = args.names if args.names else [f"Model_{i}" for i in range(len(args.models))]
    
    for model_path, name in zip(args.models, names):
        model_configs.append({
            'name': name,
            'path': model_path,
            'type': 'full'
        })
    
    # Compare models
    comparator = ModelComparator(device=args.device)
    results = comparator.compare_models(model_configs, test_loader)
    
    # Export results
    comparator.export_comparison(results, args.output)
    
    # Generate recommendations if requested
    if args.recommendations and len(args.models) > 0:
        model = comparator.load_model(args.models[0])
        stats = comparator.results[names[0]]
        size_mb = comparator.get_model_size(args.models[0])
        
        recommendations = OptimizationRecommendations.analyze_model(
            model,
            stats['latency_mean_ms'],
            stats['accuracy'],
            size_mb
        )
        OptimizationRecommendations.print_recommendations(recommendations)

if __name__ == '__main__':
    main()
