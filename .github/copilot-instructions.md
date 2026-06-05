# Brain Tumor Classification - Explainable AI Project

## Project Overview
Building an efficient, accurate, and interpretable deep learning system for brain tumor classification using MRI images with PyTorch, featuring Cross-Gated Multi-Path Attention Fusion, custom Gate-Consistency Loss, and multiple XAI techniques (Grad-CAM, SHAP, LIME).

## Setup Instructions

1. **Install Dependencies**
   - Run: `pip install -r requirements.txt`
   - Ensure CUDA is installed for GPU support

2. **Download Dataset**
   - Place brain tumor MRI dataset in `data/raw/` folder
   - Dataset should have subdirectories: `glioma/`, `meningioma/`, `pituitary/`, `no_tumor/`

3. **Configure Settings**
   - Edit `configs/config.yaml` to customize model, training, and augmentation parameters

4. **Run Training**
   - Execute: `python train.py --config configs/config.yaml`

5. **Generate Explanations**
   - After training: `python generate_explanations.py --model_path models/best_model.pth`

## Project Structure
- `src/models/`: Model architectures and attention mechanisms
- `src/data/`: Data loading and augmentation utilities
- `src/training/`: Training pipeline and loss functions
- `src/xai/`: Explainable AI implementations
- `src/evaluation/`: Metrics and evaluation utilities
- `src/visualization/`: Visualization and plotting functions
- `configs/`: Configuration files
- `data/`: Dataset storage
- `models/`: Saved model checkpoints
- `results/`: Training results and explanations
