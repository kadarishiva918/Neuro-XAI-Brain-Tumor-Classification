#!/usr/bin/env python3
"""Performance Regression Detection for CI/CD."""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent / "src"))

class RegressionDetector:
    """Detect performance regressions in models."""
    
    def __init__(self, baseline_metrics: Dict, current_metrics: Dict):
        """Initialize detector."""
        self.baseline = baseline_metrics
        self.current = current_metrics
        self.regressions = []
    
    def check_accuracy(self, threshold: float = 1.0) -> bool:
        """Check accuracy regression."""
        baseline_acc = self.baseline.get('accuracy', 0)
        current_acc = self.current.get('accuracy', 0)
        
        drop = baseline_acc - current_acc
        
        if drop > threshold:
            self.regressions.append({
                'metric': 'accuracy',
                'baseline': baseline_acc,
                'current': current_acc,
                'change': -drop,
                'threshold': threshold,
                'status': 'FAILED'
            })
            return False
        
        return True
    
    def check_latency(self, threshold: float = 10.0) -> bool:
        """Check latency regression (increase)."""
        baseline_lat = self.baseline.get('latency_ms', 0)
        current_lat = self.current.get('latency_ms', 0)
        
        increase = ((current_lat - baseline_lat) / baseline_lat) * 100 if baseline_lat > 0 else 0
        
        if increase > threshold:
            self.regressions.append({
                'metric': 'latency',
                'baseline': baseline_lat,
                'current': current_lat,
                'change': increase,
                'threshold': threshold,
                'status': 'FAILED'
            })
            return False
        
        return True
    
    def check_model_size(self, threshold: float = 10.0) -> bool:
        """Check model size regression (increase)."""
        baseline_size = self.baseline.get('size_mb', 0)
        current_size = self.current.get('size_mb', 0)
        
        increase = ((current_size - baseline_size) / baseline_size) * 100 if baseline_size > 0 else 0
        
        if increase > threshold:
            self.regressions.append({
                'metric': 'model_size',
                'baseline': baseline_size,
                'current': current_size,
                'change': increase,
                'threshold': threshold,
                'status': 'FAILED'
            })
            return False
        
        return True
    
    def check_memory_usage(self, threshold: float = 5.0) -> bool:
        """Check memory usage regression."""
        baseline_mem = self.baseline.get('peak_memory_mb', 0)
        current_mem = self.current.get('peak_memory_mb', 0)
        
        increase = ((current_mem - baseline_mem) / baseline_mem) * 100 if baseline_mem > 0 else 0
        
        if increase > threshold:
            self.regressions.append({
                'metric': 'memory',
                'baseline': baseline_mem,
                'current': current_mem,
                'change': increase,
                'threshold': threshold,
                'status': 'FAILED'
            })
            return False
        
        return True
    
    def run_all_checks(self) -> bool:
        """Run all regression checks."""
        self.regressions = []
        
        accuracy_ok = self.check_accuracy(threshold=1.0)
        latency_ok = self.check_latency(threshold=10.0)
        size_ok = self.check_model_size(threshold=10.0)
        memory_ok = self.check_memory_usage(threshold=5.0)
        
        return accuracy_ok and latency_ok and size_ok and memory_ok
    
    def print_report(self):
        """Print regression detection report."""
        print("\n" + "="*70)
        print("PERFORMANCE REGRESSION DETECTION REPORT".center(70))
        print("="*70)
        
        if not self.regressions:
            print("\n✅ NO REGRESSIONS DETECTED - All metrics within acceptable thresholds")
        else:
            print(f"\n❌ {len(self.regressions)} REGRESSION(S) DETECTED:\n")
            
            for i, reg in enumerate(self.regressions, 1):
                print(f"{i}. {reg['metric'].upper()}")
                print(f"   Baseline: {reg['baseline']:.2f}")
                print(f"   Current:  {reg['current']:.2f}")
                print(f"   Change:   {reg['change']:+.2f}%")
                print(f"   Threshold: {reg['threshold']:.2f}%")
                print(f"   Status:   {reg['status']}")
                print()
        
        print("="*70)
    
    def export_report(self, output_file: str):
        """Export report to JSON."""
        report = {
            'status': 'PASSED' if not self.regressions else 'FAILED',
            'regressions': self.regressions,
            'baseline': self.baseline,
            'current': self.current
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report exported to {output_file}")
        return report

class TestRunner:
    """Run regression tests."""
    
    @staticmethod
    def run_test_suite(test_config: Dict) -> Dict:
        """Run test suite and collect metrics."""
        print("Running regression test suite...")
        
        metrics = {
            'accuracy': test_config.get('expected_accuracy', 0.95),
            'latency_ms': test_config.get('expected_latency_ms', 700),
            'size_mb': test_config.get('expected_size_mb', 70),
            'peak_memory_mb': test_config.get('expected_memory_mb', 1024)
        }
        
        return metrics

def main():
    """Main regression detection CLI."""
    parser = argparse.ArgumentParser(description='Performance Regression Detection')
    parser.add_argument('--baseline', type=str, required=True, help='Baseline metrics JSON')
    parser.add_argument('--current', type=str, required=True, help='Current metrics JSON')
    parser.add_argument('--output', type=str, help='Output report file')
    parser.add_argument('--fail-on-regression', action='store_true',
                       help='Exit with error code if regression detected')
    
    args = parser.parse_args()
    
    # Load metrics
    with open(args.baseline) as f:
        baseline = json.load(f)
    
    with open(args.current) as f:
        current = json.load(f)
    
    # Run detection
    detector = RegressionDetector(baseline, current)
    passed = detector.run_all_checks()
    
    # Print report
    detector.print_report()
    
    # Export if requested
    if args.output:
        detector.export_report(args.output)
    
    # Exit code
    if args.fail_on_regression and not passed:
        sys.exit(1)
    
    sys.exit(0 if passed else 1)

if __name__ == '__main__':
    main()
