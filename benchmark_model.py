#!/usr/bin/env python3
"""Performance benchmarking for Brain Tumor Classification model."""

import torch
import time
import numpy as np
import psutil
import os
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from utils.config import Config

class ModelBenchmark:
    """Benchmark model performance."""
    
    def __init__(self, model_path, device='cpu', config_path='configs/config.yaml'):
        """Initialize benchmark."""
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
        
        # Get process for memory tracking
        self.process = psutil.Process(os.getpid())
    
    def benchmark_latency(self, batch_size=1, num_iterations=100, warmup=10):
        """Benchmark inference latency."""
        print(f"\nBenchmarking latency (batch_size={batch_size})...")
        
        # Warmup
        with torch.no_grad():
            for _ in range(warmup):
                x = torch.randn(batch_size, 3, 224, 224).to(self.device)
                _ = self.model(x)
        
        # Benchmark
        torch.cuda.synchronize() if self.device.type == 'cuda' else None
        
        latencies = []
        for _ in range(num_iterations):
            x = torch.randn(batch_size, 3, 224, 224).to(self.device)
            
            torch.cuda.synchronize() if self.device.type == 'cuda' else None
            start = time.perf_counter()
            
            with torch.no_grad():
                _ = self.model(x)
            
            torch.cuda.synchronize() if self.device.type == 'cuda' else None
            end = time.perf_counter()
            
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
        
        latencies = np.array(latencies)
        
        results = {
            'batch_size': batch_size,
            'num_iterations': num_iterations,
            'total_time_ms': latencies.sum(),
            'mean_latency_ms': latencies.mean(),
            'std_latency_ms': latencies.std(),
            'min_latency_ms': latencies.min(),
            'max_latency_ms': latencies.max(),
            'p50_latency_ms': np.percentile(latencies, 50),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99),
            'throughput_images_per_sec': (batch_size / latencies.mean()) * 1000
        }
        
        return results
    
    def benchmark_throughput(self, batch_sizes=[1, 4, 8, 16, 32], num_iterations=50):
        """Benchmark throughput with different batch sizes."""
        print("\nBenchmarking throughput...")
        
        results = {}
        for batch_size in batch_sizes:
            try:
                result = self.benchmark_latency(batch_size, num_iterations)
                results[batch_size] = result
                print(f"  Batch {batch_size}: {result['throughput_images_per_sec']:.1f} img/s")
            except RuntimeError as e:
                print(f"  Batch {batch_size}: Out of memory")
                break
        
        return results
    
    def benchmark_memory(self, batch_size=1, num_iterations=10):
        """Benchmark memory usage."""
        print(f"\nBenchmarking memory usage (batch_size={batch_size})...")
        
        if self.device.type == 'cuda':
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
        
        # Get baseline memory
        gc_before = self.process.memory_info().rss / (1024*1024)
        
        # Run inference
        with torch.no_grad():
            for _ in range(num_iterations):
                x = torch.randn(batch_size, 3, 224, 224).to(self.device)
                _ = self.model(x)
        
        # Get memory after
        gc_after = self.process.memory_info().rss / (1024*1024)
        
        results = {
            'batch_size': batch_size,
            'cpu_memory_before_mb': gc_before,
            'cpu_memory_after_mb': gc_after,
            'cpu_memory_used_mb': gc_after - gc_before
        }
        
        if self.device.type == 'cuda':
            peak_gpu_memory = torch.cuda.max_memory_allocated() / (1024*1024)
            current_gpu_memory = torch.cuda.memory_allocated() / (1024*1024)
            results['peak_gpu_memory_mb'] = peak_gpu_memory
            results['current_gpu_memory_mb'] = current_gpu_memory
        
        return results
    
    def benchmark_model_size(self):
        """Benchmark model size."""
        print("\nBenchmarking model size...")
        
        # Parameter count
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        
        # Model size in memory
        param_size_mb = sum(
            p.numel() * p.element_size() for p in self.model.parameters()
        ) / (1024*1024)
        
        results = {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'parameter_size_mb': param_size_mb
        }
        
        return results
    
    def run_full_benchmark(self, batch_sizes=[1, 4, 8]):
        """Run full benchmark suite."""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE BENCHMARK".center(60))
        print("="*60)
        print(f"Device: {self.device.type.upper()}")
        print(f"Model: {self.config.model['backbone']}")
        
        # Model size
        model_size = self.benchmark_model_size()
        print(f"\nModel Size:")
        print(f"  Total Parameters: {model_size['total_parameters']:,}")
        print(f"  Trainable Parameters: {model_size['trainable_parameters']:,}")
        print(f"  Parameter Size: {model_size['parameter_size_mb']:.2f} MB")
        
        # Latency for each batch size
        print(f"\nLatency by Batch Size:")
        for batch_size in batch_sizes:
            try:
                result = self.benchmark_latency(batch_size, num_iterations=50)
                print(f"\n  Batch Size {batch_size}:")
                print(f"    Mean Latency: {result['mean_latency_ms']:.3f} ms")
                print(f"    P95 Latency: {result['p95_latency_ms']:.3f} ms")
                print(f"    P99 Latency: {result['p99_latency_ms']:.3f} ms")
                print(f"    Throughput: {result['throughput_images_per_sec']:.1f} img/s")
            except RuntimeError:
                print(f"\n  Batch Size {batch_size}: Out of memory")
                break
        
        # Memory usage
        memory = self.benchmark_memory(batch_size=1)
        print(f"\nMemory Usage (batch_size=1):")
        print(f"  CPU Memory Used: {memory['cpu_memory_used_mb']:.2f} MB")
        if 'peak_gpu_memory_mb' in memory:
            print(f"  GPU Peak Memory: {memory['peak_gpu_memory_mb']:.2f} MB")
            print(f"  GPU Current Memory: {memory['current_gpu_memory_mb']:.2f} MB")
        
        print("\n" + "="*60)
    
    def export_benchmark_results(self, output_file='benchmark_results.json'):
        """Export benchmark results to JSON."""
        import json
        
        model_size = self.benchmark_model_size()
        latency = self.benchmark_latency(batch_size=1, num_iterations=50)
        memory = self.benchmark_memory(batch_size=1)
        
        results = {
            'device': str(self.device),
            'model': self.config.model['backbone'],
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'model_size': model_size,
            'latency': latency,
            'memory': memory
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results exported to {output_file}")

def main():
    """Main benchmarking script."""
    parser = argparse.ArgumentParser(description='Benchmark model performance')
    parser.add_argument('--model', type=str, default='models/best_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to use')
    parser.add_argument('--batch-sizes', type=int, nargs='+',
                       default=[1, 4, 8],
                       help='Batch sizes to benchmark')
    parser.add_argument('--export', type=str,
                       help='Export results to JSON file')
    parser.add_argument('--full', action='store_true',
                       help='Run full benchmark suite')
    
    args = parser.parse_args()
    
    # Check device availability
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("⚠️  CUDA not available, falling back to CPU")
        args.device = 'cpu'
    
    benchmark = ModelBenchmark(args.model, device=args.device)
    
    if args.full:
        benchmark.run_full_benchmark(batch_sizes=args.batch_sizes)
    
    if args.export:
        benchmark.export_benchmark_results(args.export)

if __name__ == '__main__':
    main()
