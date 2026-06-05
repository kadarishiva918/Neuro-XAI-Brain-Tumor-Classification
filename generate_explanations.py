"""Script for generating XAI explanations."""

import torch
import argparse
from pathlib import Path
import sys
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.data_loader import BrainTumorDataManager
from models.model import create_model
from xai.explainers import ExplainabilityPipeline
from visualization.visualizer import ResultsVisualizer
from utils.config import ConfigLoader


def main():
    """Generate XAI explanations."""
    parser = argparse.ArgumentParser(description='Generate XAI Explanations')
    parser.add_argument('--config', type=str, default='configs/config.yaml',
                       help='Path to config file')
    parser.add_argument('--model-path', type=str, required=True,
                       help='Path to model checkpoint')
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--output-dir', type=str, default='results/xai',
                       help='Output directory')
    parser.add_argument('--num-samples', type=int, default=5,
                       help='Number of samples to explain per class')
    parser.add_argument('--device', type=str, default='cuda',
                       help='Device to use')
    
    args = parser.parse_args()
    
    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load config and data
    config = ConfigLoader.load_config(args.config)
    data_manager = BrainTumorDataManager(config)
    data_loaders = data_manager.get_data_loaders(args.data_dir)
    
    # Load model
    print(f"Loading model from {args.model_path}...")
    model = create_model(config)
    checkpoint = torch.load(args.model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    # Initialize explainer
    print("Initializing explainability pipeline...")
    explainer_pipeline = ExplainabilityPipeline(model, config)
    
    # Initialize visualizer
    visualizer = ResultsVisualizer(output_dir=args.output_dir)
    
    # Generate explanations
    print("Generating explanations...")
    test_loader = data_loaders['test']
    
    explanations_by_class = {i: [] for i in range(config['model']['num_classes'])}
    
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(test_loader):
            if batch_idx * len(inputs) >= args.num_samples * config['model']['num_classes']:
                break
            
            inputs = inputs.to(device)
            logits, _ = model(inputs)
            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(logits, dim=1)
            confidences = torch.max(probs, dim=1).values
            
            for i in range(len(inputs)):
                pred_class = preds[i].item()
                confidence = confidences[i].item()
                
                if len(explanations_by_class[pred_class]) < args.num_samples:
                    # Generate explanations
                    image = inputs[i:i+1]
                    explanations = explainer_pipeline.explain(image, pred_class)
                    
                    explanations['target'] = targets[i].item()
                    explanations['prediction'] = pred_class
                    explanations['confidence'] = confidence
                    
                    explanations_by_class[pred_class].append(explanations)
    
    # Save explanations
    print(f"Saving explanations to {args.output_dir}...")
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON (only serializable data)
    xai_summary = {
        'total_samples_explained': sum(len(v) for v in explanations_by_class.values()),
        'samples_per_class': {str(k): len(v) for k, v in explanations_by_class.items()},
        'config': config
    }
    
    with open(output_path / 'xai_summary.json', 'w') as f:
        json.dump(xai_summary, f, indent=4)
    
    print(f"XAI explanations completed!")
    print(f"Total samples explained: {xai_summary['total_samples_explained']}")
    print(f"Samples per class: {xai_summary['samples_per_class']}")


if __name__ == '__main__':
    main()
