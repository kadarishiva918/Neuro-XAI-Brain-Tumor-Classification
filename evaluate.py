"""Inference and evaluation script for trained models."""

import torch
import argparse
import numpy as np
from pathlib import Path
import sys
from typing import Tuple, List

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.data_loader import BrainTumorDataManager
from models.model import create_model
from evaluation.metrics import MetricsCalculator, ConfusionMatrixVisualizer, ROCCurveCalculator
from visualization.visualizer import ResultsVisualizer
from utils.config import ConfigLoader
import json


class ModelEvaluator:
    """Evaluate trained model on test set."""
    
    def __init__(self, model_path: str, config_path: str, device: str = 'cuda'):
        """Initialize evaluator."""
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # Load config and model
        self.config = ConfigLoader.load_config(config_path)
        self.checkpoint = torch.load(model_path, map_location=self.device)
        
        self.model = create_model(self.config)
        self.model.load_state_dict(self.checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded from {model_path}")
        print(f"Using device: {self.device}")
    
    def evaluate(self, test_loader, class_names: List[str]) -> dict:
        """
        Evaluate model on test set.
        
        Args:
            test_loader: Test data loader
            class_names: Names of classes
            
        Returns:
            Dictionary with metrics
        """
        metrics_calculator = MetricsCalculator(
            num_classes=self.config['model']['num_classes'],
            class_names=class_names
        )
        
        all_probs = []
        
        print("Evaluating...")
        with torch.no_grad():
            for batch_idx, (inputs, targets) in enumerate(test_loader):
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
                logits, _ = self.model(inputs)
                metrics_calculator.update(logits, targets)
                
                probs = torch.softmax(logits, dim=1)
                all_probs.append(probs.cpu().numpy())
        
        # Compute metrics
        metrics = metrics_calculator.compute_metrics()
        cm = metrics_calculator.get_confusion_matrix()
        
        all_probs = np.concatenate(all_probs, axis=0)
        
        # Compute ROC curves
        y_true = np.array(metrics_calculator.all_targets)
        roc_data = ROCCurveCalculator.compute_roc_curve(y_true, all_probs, 
                                                       self.config['model']['num_classes'])
        
        return {
            'metrics': metrics,
            'confusion_matrix': cm,
            'roc_curves': roc_data,
            'classification_report': metrics_calculator.get_classification_report()
        }
    
    def predict(self, image_tensor: torch.Tensor) -> Tuple[int, float, np.ndarray]:
        """
        Make prediction on single image.
        
        Args:
            image_tensor: Input image tensor (1, 3, 224, 224)
            
        Returns:
            Tuple of (predicted_class, confidence, probabilities)
        """
        image_tensor = image_tensor.to(self.device)
        
        with torch.no_grad():
            logits, gates = self.model(image_tensor)
            probs = torch.softmax(logits, dim=1)
            
            pred_class = torch.argmax(logits, dim=1).item()
            confidence = torch.max(probs, dim=1).values.item()
        
        return pred_class, confidence, probs.cpu().numpy()[0]


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description='Evaluate Brain Tumor Classification Model')
    parser.add_argument('--model-path', type=str, required=True,
                       help='Path to model checkpoint')
    parser.add_argument('--config', type=str, default='configs/config.yaml',
                       help='Path to config file')
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--output-dir', type=str, default='results/evaluation',
                       help='Output directory')
    parser.add_argument('--device', type=str, default='cuda',
                       help='Device to use')
    
    args = parser.parse_args()
    
    # Setup
    device = args.device if torch.cuda.is_available() else 'cpu'
    
    # Load data and model
    config = ConfigLoader.load_config(args.config)
    data_manager = BrainTumorDataManager(config)
    data_loaders = data_manager.get_data_loaders(args.data_dir)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(args.model_path, args.config, device=device)
    
    # Evaluate
    results = evaluator.evaluate(data_loaders['test'], data_manager.class_names)
    
    # Print results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    
    metrics = results['metrics']
    print(f"\nAccuracy: {metrics['accuracy']:.4f}")
    print(f"Macro Precision: {metrics['precision_macro']:.4f}")
    print(f"Macro Recall: {metrics['recall_macro']:.4f}")
    print(f"Macro F1: {metrics['f1_macro']:.4f}")
    print(f"Weighted F1: {metrics['f1_weighted']:.4f}")
    
    if 'auc_macro' in metrics:
        print(f"AUC (Macro): {metrics['auc_macro']:.4f}")
    
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    print(results['classification_report'])
    
    # Visualize results
    print("\nGenerating visualizations...")
    visualizer = ResultsVisualizer(output_dir=args.output_dir)
    
    # Confusion matrix
    visualizer.plot_confusion_matrix(results['confusion_matrix'],
                                    data_manager.class_names,
                                    normalized=True,
                                    save_path=f'{args.output_dir}/confusion_matrix_normalized.png')
    
    visualizer.plot_confusion_matrix(results['confusion_matrix'],
                                    data_manager.class_names,
                                    normalized=False,
                                    save_path=f'{args.output_dir}/confusion_matrix_counts.png')
    
    # ROC curves
    visualizer.plot_roc_curves(results['roc_curves'],
                              data_manager.class_names,
                              save_path=f'{args.output_dir}/roc_curves.png')
    
    # Save detailed results
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save metrics as JSON
    metrics_json = {k: float(v) if isinstance(v, (int, float, np.number)) else str(v)
                   for k, v in metrics.items()}
    
    with open(output_path / 'metrics.json', 'w') as f:
        json.dump(metrics_json, f, indent=4)
    
    # Save classification report
    with open(output_path / 'classification_report.txt', 'w') as f:
        f.write(results['classification_report'])
    
    print(f"\nResults saved to: {args.output_dir}")


if __name__ == '__main__':
    main()
