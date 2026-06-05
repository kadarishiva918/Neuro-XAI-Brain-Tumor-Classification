#!/usr/bin/env python3
"""Model Registry and Versioning System."""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class ModelRegistry:
    """Central registry for managing model versions."""
    
    def __init__(self, registry_path='models/registry.json'):
        """Initialize model registry."""
        self.registry_path = registry_path
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load registry from file."""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {'models': [], 'current': None}
    
    def _save_registry(self):
        """Save registry to file."""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model_path: str, version: str, metadata: Dict) -> Dict:
        """Register a new model version."""
        print(f"Registering model version {version}...")
        
        # Calculate file hash
        file_hash = self._calculate_hash(model_path)
        
        # Get file size
        file_size_mb = os.path.getsize(model_path) / (1024*1024)
        
        # Create model entry
        model_entry = {
            'version': version,
            'path': model_path,
            'hash': file_hash,
            'size_mb': round(file_size_mb, 2),
            'created_at': datetime.now().isoformat(),
            'metadata': metadata,
            'status': 'active'
        }
        
        # Add to registry
        self.registry['models'].append(model_entry)
        if self.registry['current'] is None:
            self.registry['current'] = version
        
        self._save_registry()
        print(f"✅ Model {version} registered")
        return model_entry
    
    def get_model(self, version: Optional[str] = None) -> Optional[Dict]:
        """Get model info by version."""
        if version is None:
            version = self.registry['current']
        
        for model in self.registry['models']:
            if model['version'] == version:
                return model
        
        return None
    
    def set_current(self, version: str):
        """Set current active model."""
        if self.get_model(version) is None:
            print(f"❌ Model version {version} not found")
            return False
        
        self.registry['current'] = version
        self._save_registry()
        print(f"✅ Current model set to {version}")
        return True
    
    def list_models(self) -> List[Dict]:
        """List all registered models."""
        return self.registry['models']
    
    def get_current(self) -> Optional[Dict]:
        """Get current active model."""
        if self.registry['current'] is None:
            return None
        return self.get_model(self.registry['current'])
    
    def compare_versions(self, v1: str, v2: str):
        """Compare two model versions."""
        model1 = self.get_model(v1)
        model2 = self.get_model(v2)
        
        if not model1 or not model2:
            print("❌ One or both models not found")
            return
        
        print("\n" + "="*60)
        print("MODEL COMPARISON".center(60))
        print("="*60)
        print(f"\nModel {v1}:")
        print(f"  Size: {model1['size_mb']} MB")
        print(f"  Created: {model1['created_at']}")
        print(f"  Metadata: {model1['metadata']}")
        
        print(f"\nModel {v2}:")
        print(f"  Size: {model2['size_mb']} MB")
        print(f"  Created: {model2['created_at']}")
        print(f"  Metadata: {model2['metadata']}")
        
        size_diff = model1['size_mb'] - model2['size_mb']
        print(f"\nSize Difference: {size_diff:+.2f} MB")
    
    @staticmethod
    def _calculate_hash(file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def print_registry(self):
        """Print registry table."""
        print("\n" + "="*100)
        print("MODEL REGISTRY".center(100))
        print("="*100)
        
        for model in self.registry['models']:
            current_marker = "→ " if model['version'] == self.registry['current'] else "  "
            accuracy = model['metadata'].get('accuracy', 'N/A')
            print(f"{current_marker}{model['version']:20} | {model['size_mb']:8.1f}MB | Acc: {accuracy:6} | "
                  f"{model['created_at']}")
        
        print("="*100)
        print(f"Current: {self.registry['current']}")

class ModelVersioning:
    """Version management for models."""
    
    @staticmethod
    def generate_version() -> str:
        """Generate semantic version."""
        return datetime.now().strftime("v%Y%m%d_%H%M%S")
    
    @staticmethod
    def create_checkpoint(model_path: str, version: str, backup_dir='models/backups'):
        """Create versioned backup."""
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{version}.pth")
        shutil.copy2(model_path, backup_path)
        print(f"✅ Backup created at {backup_path}")
        return backup_path
    
    @staticmethod
    def rollback_model(version: str, source_dir='models/backups', target='models/best_model.pth'):
        """Rollback to previous model version."""
        backup_path = os.path.join(source_dir, f"{version}.pth")
        if not os.path.exists(backup_path):
            print(f"❌ Backup {version} not found")
            return False
        
        shutil.copy2(backup_path, target)
        print(f"✅ Model rolled back to {version}")
        return True

class ModelPerformanceTracker:
    """Track model performance over versions."""
    
    def __init__(self, tracking_file='models/performance_tracking.json'):
        """Initialize tracker."""
        self.tracking_file = tracking_file
        self.data = self._load_tracking()
    
    def _load_tracking(self) -> Dict:
        """Load tracking data."""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {'versions': []}
    
    def _save_tracking(self):
        """Save tracking data."""
        os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)
        with open(self.tracking_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_performance_record(self, version: str, metrics: Dict):
        """Add performance metrics for version."""
        record = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        self.data['versions'].append(record)
        self._save_tracking()
        print(f"✅ Performance record added for {version}")
    
    def get_performance_trend(self, metric: str = 'accuracy') -> List[Dict]:
        """Get performance trend over versions."""
        trend = []
        for record in self.data['versions']:
            if metric in record['metrics']:
                trend.append({
                    'version': record['version'],
                    'value': record['metrics'][metric],
                    'timestamp': record['timestamp']
                })
        return trend
    
    def detect_regression(self, metric: str = 'accuracy', threshold: float = 2.0) -> bool:
        """Detect performance regression."""
        trend = self.get_performance_trend(metric)
        if len(trend) < 2:
            return False
        
        latest = trend[-1]['value']
        previous = trend[-2]['value']
        
        regression = previous - latest
        
        if regression > threshold:
            print(f"⚠️  Performance regression detected!")
            print(f"   {metric}: {previous:.2f} → {latest:.2f} ({regression:.2f}% drop)")
            return True
        
        return False
    
    def print_performance_history(self):
        """Print performance history."""
        print("\n" + "="*80)
        print("PERFORMANCE HISTORY".center(80))
        print("="*80)
        
        for record in self.data['versions']:
            print(f"\nVersion: {record['version']}")
            print(f"Timestamp: {record['timestamp']}")
            for metric, value in record['metrics'].items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.4f}")
                else:
                    print(f"  {metric}: {value}")

def main():
    """Main model registry CLI."""
    parser = argparse.ArgumentParser(description='Model Registry and Versioning')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register new model')
    register_parser.add_argument('--path', type=str, required=True, help='Model path')
    register_parser.add_argument('--version', type=str, help='Version name')
    register_parser.add_argument('--accuracy', type=float, help='Model accuracy')
    register_parser.add_argument('--latency', type=float, help='Inference latency (ms)')
    
    # List command
    subparsers.add_parser('list', help='List all models')
    
    # Current command
    subparsers.add_parser('current', help='Show current model')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set current model')
    set_parser.add_argument('--version', type=str, required=True, help='Version to set')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare versions')
    compare_parser.add_argument('--v1', type=str, required=True)
    compare_parser.add_argument('--v2', type=str, required=True)
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create backup')
    backup_parser.add_argument('--path', type=str, required=True)
    backup_parser.add_argument('--version', type=str)
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to version')
    rollback_parser.add_argument('--version', type=str, required=True)
    
    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Track performance')
    perf_parser.add_argument('--version', type=str, required=True)
    perf_parser.add_argument('--accuracy', type=float, required=True)
    perf_parser.add_argument('--latency', type=float)
    perf_parser.add_argument('--show-history', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'register':
        registry = ModelRegistry()
        metadata = {}
        if args.accuracy:
            metadata['accuracy'] = args.accuracy
        if args.latency:
            metadata['latency_ms'] = args.latency
        
        version = args.version or ModelVersioning.generate_version()
        registry.register_model(args.path, version, metadata)
        registry.print_registry()
    
    elif args.command == 'list':
        registry = ModelRegistry()
        registry.print_registry()
    
    elif args.command == 'current':
        registry = ModelRegistry()
        current = registry.get_current()
        if current:
            print(f"Current model: {current['version']}")
            print(f"Path: {current['path']}")
    
    elif args.command == 'set':
        registry = ModelRegistry()
        registry.set_current(args.version)
    
    elif args.command == 'compare':
        registry = ModelRegistry()
        registry.compare_versions(args.v1, args.v2)
    
    elif args.command == 'backup':
        version = args.version or ModelVersioning.generate_version()
        ModelVersioning.create_checkpoint(args.path, version)
    
    elif args.command == 'rollback':
        ModelVersioning.rollback_model(args.version)
    
    elif args.command == 'performance':
        tracker = ModelPerformanceTracker()
        metrics = {'accuracy': args.accuracy}
        if args.latency:
            metrics['latency_ms'] = args.latency
        
        tracker.add_performance_record(args.version, metrics)
        
        if args.show_history:
            tracker.print_performance_history()

if __name__ == '__main__':
    main()
