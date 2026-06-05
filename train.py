"""Main training script for brain tumor classification."""

import torch
import torch.nn as nn
import argparse
from pathlib import Path
import sys
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.data_loader import BrainTumorDataManager
from models.model import create_model
from training.trainer import Trainer
from evaluation.metrics import MetricsCalculator
from visualization.visualizer import ResultsVisualizer
from utils.config import ConfigLoader, PathManager


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Brain Tumor Classification Training')
    parser.add_argument('--config', type=str, default='configs/config.yaml',
                       help='Path to config file')
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory')
    parser.add_argument('--device', type=str, default='cuda',
                       help='Device to use (cuda or cpu)')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to checkpoint to resume from')
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading config from {args.config}...")
    config = ConfigLoader.load_config(args.config)
    
    # Initialize path manager
    path_manager = PathManager(project_root=Path.cwd())
    
    # Check device
    device = args.device if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load data
    print("Loading data...")
    data_manager = BrainTumorDataManager(config)
    data_loaders = data_manager.get_data_loaders(args.data_dir)
    
    print(f"Train samples: {data_loaders['num_samples']['train']}")
    print(f"Val samples: {data_loaders['num_samples']['val']}")
    print(f"Test samples: {data_loaders['num_samples']['test']}")
    
    # Create model
    print("Creating model...")
    model = create_model(config)
    print(f"Model created: {model.__class__.__name__}")
    
    # Initialize trainer
    print("Initializing trainer...")
    trainer = Trainer(model, config, device=device)
    
    # Load checkpoint if provided
    if args.resume:
        print(f"Loading checkpoint from {args.resume}...")
        trainer.load_checkpoint(args.resume)
    
    # Train model
    print("Starting training...")
    trainer.train(data_loaders['train'], data_loaders['val'])
    
    # Test on test set
    print("Testing on test set...")
    model.load_state_dict(torch.load('models/best_model.pth', 
                                     map_location=device)['model_state_dict'])
    
    test_loader = data_loaders['test']
    metrics_calculator = MetricsCalculator(
        num_classes=config['model']['num_classes'],
        class_names=data_manager.class_names
    )
    
    model.eval()
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)
            logits, _ = model(inputs)
            metrics_calculator.update(logits, targets)
    
    # Compute metrics
    metrics = metrics_calculator.compute_metrics()
    cm = metrics_calculator.get_confusion_matrix()
    
    print("\n" + "="*50)
    print("Test Metrics")
    print("="*50)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['f1_macro']:.4f}")
    print(f"Macro Recall: {metrics['recall_macro']:.4f}")
    print(f"Macro Precision: {metrics['precision_macro']:.4f}")
    
    # Visualize results
    print("\nGenerating visualizations...")
    visualizer = ResultsVisualizer(output_dir='results/visualizations')
    
    # Plot training history
    visualizer.plot_training_history(trainer.history,
                                    save_path='results/visualizations/training_history.png')
    
    # Plot confusion matrix
    visualizer.plot_confusion_matrix(cm, data_manager.class_names,
                                    save_path='results/visualizations/confusion_matrix.png')
    
    # Save metrics
    import json
    with open('results/test_metrics.json', 'w') as f:
        # Convert numpy arrays to lists
        metrics_serializable = {k: float(v) if isinstance(v, (int, float)) else v 
                               for k, v in metrics.items()}
        json.dump(metrics_serializable, f, indent=4)
    
    print("\n" + "="*50)
    print("Training completed!")
    print(f"Best model saved to: models/best_model.pth")
    print(f"Results saved to: results/")
    print("="*50)


if __name__ == '__main__':
    main()
