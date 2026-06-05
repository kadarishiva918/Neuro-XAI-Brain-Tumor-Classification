#!/usr/bin/env python3
"""Advanced Production Monitoring System."""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class MetricThreshold:
    """Threshold configuration for metrics."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    condition: str  # "greater_than" or "less_than"

@dataclass
class Alert:
    """Alert representation."""
    timestamp: str
    severity: AlertSeverity
    metric: str
    current_value: float
    threshold: float
    message: str
    resolution: str

class AdvancedMonitoring:
    """Production-grade monitoring system."""
    
    def __init__(self, alert_file='monitoring/alerts.json'):
        """Initialize monitoring."""
        self.alert_file = alert_file
        self.alerts: List[Alert] = []
        self.thresholds = self._init_thresholds()
        self.metrics_history = {}
    
    def _init_thresholds(self) -> Dict[str, MetricThreshold]:
        """Initialize metric thresholds."""
        return {
            'cpu_usage': MetricThreshold('cpu_usage', 70, 90, 'greater_than'),
            'memory_usage': MetricThreshold('memory_usage', 80, 95, 'greater_than'),
            'latency_p95': MetricThreshold('latency_p95', 1000, 2000, 'greater_than'),
            'error_rate': MetricThreshold('error_rate', 1, 5, 'greater_than'),
            'model_accuracy': MetricThreshold('model_accuracy', 85, 80, 'less_than'),
            'throughput': MetricThreshold('throughput', 100, 50, 'less_than'),
            'disk_usage': MetricThreshold('disk_usage', 80, 95, 'greater_than'),
        }
    
    def check_metric(self, metric_name: str, value: float) -> Optional[Alert]:
        """Check metric against thresholds."""
        if metric_name not in self.thresholds:
            return None
        
        threshold = self.thresholds[metric_name]
        timestamp = datetime.now().isoformat()
        
        severity = None
        alert_msg = None
        resolution = None
        
        if threshold.condition == 'greater_than':
            if value >= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                alert_msg = f"{metric_name} critically high: {value}"
                resolution = self._get_resolution(metric_name, 'high')
            elif value >= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                alert_msg = f"{metric_name} warning: {value}"
                resolution = self._get_resolution(metric_name, 'warning')
        
        elif threshold.condition == 'less_than':
            if value <= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                alert_msg = f"{metric_name} critically low: {value}"
                resolution = self._get_resolution(metric_name, 'low')
            elif value <= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                alert_msg = f"{metric_name} warning: {value}"
                resolution = self._get_resolution(metric_name, 'warning')
        
        if severity:
            alert = Alert(
                timestamp=timestamp,
                severity=severity,
                metric=metric_name,
                current_value=value,
                threshold=threshold.critical_threshold,
                message=alert_msg,
                resolution=resolution
            )
            return alert
        
        return None
    
    def _get_resolution(self, metric: str, condition: str) -> str:
        """Get resolution suggestions."""
        resolutions = {
            ('cpu_usage', 'high'): 'Scale up replicas or optimize model',
            ('memory_usage', 'high'): 'Increase pod memory or optimize memory usage',
            ('latency_p95', 'high'): 'Check GPU usage or scale horizontally',
            ('error_rate', 'high'): 'Review logs and check downstream services',
            ('model_accuracy', 'low'): 'Retrain model or check input data quality',
            ('throughput', 'low'): 'Increase replicas or optimize inference',
            ('disk_usage', 'high'): 'Clean up logs or expand storage',
        }
        return resolutions.get((metric, condition), 'Check system resources')
    
    def record_alert(self, alert: Alert):
        """Record an alert."""
        self.alerts.append(alert)
        logger.log(
            logging.WARNING if alert.severity == AlertSeverity.WARNING else logging.CRITICAL,
            f"{alert.severity.value.upper()}: {alert.message} - {alert.resolution}"
        )
        self._save_alerts()
    
    def _save_alerts(self):
        """Save alerts to file."""
        alerts_data = [asdict(alert) for alert in self.alerts[-1000:]]  # Keep last 1000
        with open(self.alert_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def get_alert_summary(self) -> Dict:
        """Get alert summary."""
        total = len(self.alerts)
        critical = sum(1 for a in self.alerts if a.severity == AlertSeverity.CRITICAL)
        warning = sum(1 for a in self.alerts if a.severity == AlertSeverity.WARNING)
        
        return {
            'total_alerts': total,
            'critical': critical,
            'warning': warning,
            'info': total - critical - warning,
            'last_24h': sum(1 for a in self.alerts 
                           if datetime.fromisoformat(a.timestamp) > 
                           datetime.now() - timedelta(hours=24))
        }

class HealthChecker:
    """System health checking."""
    
    def __init__(self):
        """Initialize health checker."""
        self.checks = {}
    
    def check_api_health(self, endpoint: str, timeout: int = 5) -> bool:
        """Check API health."""
        import subprocess
        try:
            result = subprocess.run(
                f"curl -s -f {endpoint}",
                shell=True,
                timeout=timeout,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
    
    def check_database_health(self, connection_string: str) -> bool:
        """Check database health."""
        try:
            import psycopg2
            conn = psycopg2.connect(connection_string)
            conn.close()
            return True
        except:
            return False
    
    def check_cache_health(self, redis_url: str) -> bool:
        """Check cache health."""
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            return True
        except:
            return False
    
    def get_system_health(self) -> Dict:
        """Get overall system health."""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': self.checks
        }
        
        if any(not v for v in self.checks.values()):
            health['status'] = 'degraded'
        
        if all(not v for v in self.checks.values()):
            health['status'] = 'unhealthy'
        
        return health

class MetricsCollector:
    """Collect and aggregate metrics."""
    
    def __init__(self, window_size: int = 100):
        """Initialize collector."""
        self.window_size = window_size
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, tags: Dict = None):
        """Record a metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'tags': tags or {}
        })
        
        # Keep only last N records
        if len(self.metrics[name]) > self.window_size:
            self.metrics[name] = self.metrics[name][-self.window_size:]
    
    def get_metric_stats(self, name: str) -> Dict:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}
        
        values = [m['value'] for m in self.metrics[name]]
        
        if not values:
            return {}
        
        import statistics
        return {
            'name': name,
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'latest': values[-1]
        }
    
    def export_metrics(self, output_file: str):
        """Export metrics to file."""
        metrics_data = {}
        for name in self.metrics:
            metrics_data[name] = self.get_metric_stats(name)
        
        with open(output_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)

class IncidentDetector:
    """Detect and classify incidents."""
    
    def __init__(self):
        """Initialize detector."""
        self.incidents = []
    
    def detect_incidents(self, alerts: List[Alert]) -> List[Dict]:
        """Detect incident patterns."""
        incidents = []
        
        # Group alerts by time window
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=5)
        
        recent_alerts = [
            a for a in alerts
            if datetime.fromisoformat(a.timestamp) > window_start
        ]
        
        # Incident: Multiple critical alerts
        critical_count = sum(1 for a in recent_alerts 
                            if a.severity == AlertSeverity.CRITICAL)
        
        if critical_count >= 3:
            incidents.append({
                'type': 'multiple_critical_alerts',
                'severity': 'CRITICAL',
                'count': critical_count,
                'suggested_action': 'Initiate incident response'
            })
        
        # Incident: Cascading failures
        metrics = set(a.metric for a in recent_alerts)
        if len(metrics) >= 5:
            incidents.append({
                'type': 'system_wide_degradation',
                'severity': 'CRITICAL',
                'affected_metrics': list(metrics),
                'suggested_action': 'Check infrastructure status'
            })
        
        return incidents

def main():
    """Main monitoring CLI."""
    parser = argparse.ArgumentParser(description='Advanced Production Monitoring')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Check metric
    check_parser = subparsers.add_parser('check', help='Check metric')
    check_parser.add_argument('--metric', type=str, required=True)
    check_parser.add_argument('--value', type=float, required=True)
    
    # Health check
    health_parser = subparsers.add_parser('health', help='Health check')
    health_parser.add_argument('--api', type=str, help='API endpoint')
    health_parser.add_argument('--db', type=str, help='Database connection string')
    
    # Export metrics
    export_parser = subparsers.add_parser('export', help='Export metrics')
    export_parser.add_argument('--output', type=str, default='monitoring/metrics_export.json')
    
    # Alert summary
    subparsers.add_parser('alerts', help='Alert summary')
    
    # Detect incidents
    subparsers.add_parser('incidents', help='Detect incidents')
    
    args = parser.parse_args()
    
    monitoring = AdvancedMonitoring()
    health = HealthChecker()
    collector = MetricsCollector()
    detector = IncidentDetector()
    
    if args.command == 'check':
        alert = monitoring.check_metric(args.metric, args.value)
        if alert:
            monitoring.record_alert(alert)
            print(f"🔴 ALERT: {alert.message}")
            print(f"   Resolution: {alert.resolution}")
        else:
            print(f"✅ OK: {args.metric} = {args.value}")
    
    elif args.command == 'health':
        print("Running health checks...")
        if args.api:
            api_ok = health.check_api_health(args.api)
            print(f"API Health: {'✅ OK' if api_ok else '❌ FAILED'}")
        if args.db:
            db_ok = health.check_database_health(args.db)
            print(f"DB Health: {'✅ OK' if db_ok else '❌ FAILED'}")
    
    elif args.command == 'alerts':
        summary = monitoring.get_alert_summary()
        print("\n" + "="*50)
        print("ALERT SUMMARY".center(50))
        print("="*50)
        for key, value in summary.items():
            print(f"{key}: {value}")
    
    elif args.command == 'incidents':
        incidents = detector.detect_incidents(monitoring.alerts)
        if incidents:
            print("\n🚨 INCIDENTS DETECTED:")
            for inc in incidents:
                print(f"  - {inc['type']}: {inc['suggested_action']}")
        else:
            print("✅ No incidents detected")

if __name__ == '__main__':
    main()
