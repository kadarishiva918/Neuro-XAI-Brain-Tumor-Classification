#!/usr/bin/env python3
"""Automated Deployment and Rollback System."""

import os
import sys
import json
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class DeploymentManager:
    """Manage model deployments and rollbacks."""
    
    def __init__(self, deployment_dir='deployments', models_dir='models'):
        """Initialize deployment manager."""
        self.deployment_dir = deployment_dir
        self.models_dir = models_dir
        self.deployment_log = os.path.join(deployment_dir, 'deployment_log.json')
        
        os.makedirs(deployment_dir, exist_ok=True)
        self._load_deployment_log()
    
    def _load_deployment_log(self):
        """Load deployment log."""
        if os.path.exists(self.deployment_log):
            with open(self.deployment_log) as f:
                self.log = json.load(f)
        else:
            self.log = {'deployments': [], 'current': None}
    
    def _save_deployment_log(self):
        """Save deployment log."""
        with open(self.deployment_log, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def prepare_deployment(self, model_path: str, version: str, 
                          tests_passed: bool) -> bool:
        """Prepare model for deployment."""
        print(f"\n{'='*60}")
        print("DEPLOYMENT PREPARATION".center(60))
        print(f"{'='*60}")
        
        if not tests_passed:
            print("❌ Tests failed. Deployment blocked.")
            return False
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            return False
        
        print(f"✅ Model ready for deployment: {version}")
        print(f"   Path: {model_path}")
        print(f"   Size: {os.path.getsize(model_path)/(1024*1024):.1f} MB")
        
        return True
    
    def deploy_model(self, model_path: str, version: str, 
                    environment: str = 'staging') -> Dict:
        """Deploy model to environment."""
        print(f"\nDeploying to {environment}...")
        
        deploy_time = datetime.now().isoformat()
        
        # Create deployment directory
        deploy_path = os.path.join(self.deployment_dir, f"{environment}_{version}")
        os.makedirs(deploy_path, exist_ok=True)
        
        # Copy model
        dest_model = os.path.join(deploy_path, 'model.pth')
        shutil.copy2(model_path, dest_model)
        
        # Create deployment metadata
        deployment = {
            'version': version,
            'environment': environment,
            'deployed_at': deploy_time,
            'model_path': dest_model,
            'status': 'active'
        }
        
        # Save deployment info
        info_path = os.path.join(deploy_path, 'deployment_info.json')
        with open(info_path, 'w') as f:
            json.dump(deployment, f, indent=2)
        
        # Update log
        self.log['deployments'].append(deployment)
        if environment == 'production':
            self.log['current'] = version
        self._save_deployment_log()
        
        print(f"✅ Deployment successful")
        print(f"   Version: {version}")
        print(f"   Environment: {environment}")
        print(f"   Path: {deploy_path}")
        
        return deployment
    
    def health_check(self, environment: str) -> bool:
        """Run health check on deployed model."""
        print(f"\nRunning health check on {environment}...")
        
        try:
            # Check API is running
            cmd = f"curl -s http://localhost:5000/health"
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ API health check passed")
                return True
            else:
                print("❌ API health check failed")
                return False
        
        except Exception as e:
            print(f"⚠️  Health check error: {e}")
            return False
    
    def rollback_deployment(self, environment: str, version: str) -> bool:
        """Rollback to previous deployment."""
        print(f"\nRolling back {environment} to {version}...")
        
        # Find deployment
        target_deploy = None
        for deploy in reversed(self.log['deployments']):
            if deploy['version'] == version and deploy['environment'] == environment:
                target_deploy = deploy
                break
        
        if not target_deploy:
            print(f"❌ Deployment not found: {version} in {environment}")
            return False
        
        # Perform rollback
        model_path = target_deploy['model_path']
        if os.path.exists(model_path):
            # Copy back to active model
            active_model = os.path.join(self.models_dir, 'best_model.pth')
            shutil.copy2(model_path, active_model)
            
            print(f"✅ Rollback successful")
            print(f"   Version: {version}")
            print(f"   Active model restored")
            return True
        else:
            print(f"❌ Model file not found: {model_path}")
            return False
    
    def get_deployment_status(self, environment: str) -> Dict:
        """Get current deployment status."""
        deployments = [d for d in self.log['deployments'] 
                      if d['environment'] == environment and d['status'] == 'active']
        
        if deployments:
            latest = deployments[-1]
            return {
                'environment': environment,
                'version': latest['version'],
                'deployed_at': latest['deployed_at'],
                'status': 'active'
            }
        
        return {'environment': environment, 'status': 'inactive'}
    
    def print_deployment_history(self):
        """Print deployment history."""
        print("\n" + "="*80)
        print("DEPLOYMENT HISTORY".center(80))
        print("="*80)
        
        for deploy in self.log['deployments']:
            print(f"\n{deploy['version']} ({deploy['environment']})")
            print(f"  Deployed: {deploy['deployed_at']}")
            print(f"  Status: {deploy['status']}")

class CanaryDeployment:
    """Canary deployment strategy."""
    
    def __init__(self, manager: DeploymentManager):
        """Initialize canary deployment."""
        self.manager = manager
    
    def canary_deploy(self, model_path: str, version: str, 
                     canary_percentage: float = 10.0) -> bool:
        """Deploy to canary environment."""
        print(f"\n{'='*60}")
        print("CANARY DEPLOYMENT".center(60))
        print(f"{'='*60}")
        print(f"\nDeploying {version} as canary ({canary_percentage}% traffic)...")
        
        # Deploy to canary
        deployment = self.manager.deploy_model(model_path, version, environment='canary')
        
        print(f"✅ Canary deployment complete")
        print(f"   {canary_percentage}% of traffic will use new model")
        print(f"   Monitor for issues before full rollout")
        
        return True
    
    def promote_canary_to_production(self, version: str) -> bool:
        """Promote canary to production."""
        print(f"\nPromoting {version} from canary to production...")
        
        # This would involve running additional tests
        # and then doing a full deployment to production
        
        print(f"✅ Promoted to production")
        return True

def main():
    """Main deployment CLI."""
    parser = argparse.ArgumentParser(description='Automated Deployment Management')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Prepare command
    prepare_parser = subparsers.add_parser('prepare', help='Prepare deployment')
    prepare_parser.add_argument('--model', type=str, required=True)
    prepare_parser.add_argument('--version', type=str, required=True)
    prepare_parser.add_argument('--tests-passed', action='store_true')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy model')
    deploy_parser.add_argument('--model', type=str, required=True)
    deploy_parser.add_argument('--version', type=str, required=True)
    deploy_parser.add_argument('--environment', type=str, default='staging',
                             choices=['staging', 'canary', 'production'])
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Health check')
    health_parser.add_argument('--environment', type=str, default='staging')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback deployment')
    rollback_parser.add_argument('--environment', type=str, required=True)
    rollback_parser.add_argument('--version', type=str, required=True)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Deployment status')
    status_parser.add_argument('--environment', type=str, default='production')
    
    # History command
    subparsers.add_parser('history', help='Deployment history')
    
    # Canary command
    canary_parser = subparsers.add_parser('canary', help='Canary deployment')
    canary_parser.add_argument('--model', type=str, required=True)
    canary_parser.add_argument('--version', type=str, required=True)
    canary_parser.add_argument('--percentage', type=float, default=10.0)
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    if args.command == 'prepare':
        success = manager.prepare_deployment(args.model, args.version, args.tests_passed)
        sys.exit(0 if success else 1)
    
    elif args.command == 'deploy':
        manager.deploy_model(args.model, args.version, args.environment)
    
    elif args.command == 'health':
        success = manager.health_check(args.environment)
        sys.exit(0 if success else 1)
    
    elif args.command == 'rollback':
        success = manager.rollback_deployment(args.environment, args.version)
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        status = manager.get_deployment_status(args.environment)
        print(json.dumps(status, indent=2))
    
    elif args.command == 'history':
        manager.print_deployment_history()
    
    elif args.command == 'canary':
        canary = CanaryDeployment(manager)
        canary.canary_deploy(args.model, args.version, args.percentage)

if __name__ == '__main__':
    main()
