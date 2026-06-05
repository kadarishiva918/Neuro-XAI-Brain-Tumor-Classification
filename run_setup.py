"""
Interactive Kaggle setup and dataset download for Brain Tumor Classification.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_step(step_num: int, title: str):
    """Print step header."""
    print(f"\n[STEP {step_num}] {title}")
    print("-" * 80)


def check_kaggle_installed() -> bool:
    """Check if kaggle is installed."""
    try:
        import kaggle
        return True
    except ImportError:
        return False


def install_kaggle() -> bool:
    """Install kaggle package."""
    try:
        print("Installing kaggle...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        print("✅ Kaggle installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install kaggle")
        return False


def check_credentials() -> bool:
    """Check if Kaggle credentials exist."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return kaggle_json.exists()


def setup_credentials_guide():
    """Print guide to set up Kaggle credentials."""
    print_step(1, "SET UP KAGGLE CREDENTIALS")
    
    print("""
FOLLOW THESE STEPS:

1. Open: https://www.kaggle.com/settings/account

2. Scroll to "API" section

3. Click "Create New API Token"
   → This downloads kaggle.json file

4. Move the file to the correct location:
   
   📍 Windows:
   C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
   
   📍 Linux/Mac:
   ~/.kaggle/kaggle.json

5. Set permissions (Linux/Mac only):
   chmod 600 ~/.kaggle/kaggle.json

⏭️  After placing the file, press Enter to continue...
    """)
    
    input("Press Enter when credentials are in place...")


def verify_credentials() -> bool:
    """Verify Kaggle credentials work."""
    try:
        import kaggle
        print("Testing Kaggle API...")
        # This will fail silently if credentials are wrong
        kaggle.api.dataset_list(search='brain', max_size=1)
        print("✅ Credentials verified!")
        return True
    except Exception as e:
        print(f"❌ Credentials verification failed: {e}")
        print("\nMake sure:")
        print("  1. kaggle.json exists in ~/.kaggle/")
        print("  2. File contains valid API credentials")
        print("  3. You've accepted dataset terms on Kaggle")
        return False


def download_dataset() -> bool:
    """Download Brain Tumor MRI dataset."""
    print_step(2, "DOWNLOAD KAGGLE DATASET")
    
    print("This will download the Brain Tumor MRI dataset (~5GB)")
    print("Destination: data/raw/")
    print("\n⏳ Starting download...\n")
    
    try:
        import kaggle
        
        # Create data directory
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            "masoudnickparvar/brain-tumor-mri-dataset",
            path="data/raw",
            unzip=True
        )
        
        print("\n✅ Dataset downloaded successfully!")
        return True
    
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify Kaggle credentials")
        print("  3. Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset")
        print("     and accept the dataset terms")
        return False


def organize_dataset() -> bool:
    """Organize downloaded dataset."""
    print_step(3, "ORGANIZE DATASET")
    
    try:
        print("Organizing dataset into class directories...\n")
        
        data_dir = Path("data/raw")
        classes = ['glioma', 'meningioma', 'pituitary', 'no_tumor']
        
        # Find the extracted folder
        extracted_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name != '__MACOSX']
        
        if not extracted_dirs:
            print("❌ No extracted dataset found")
            return False
        
        source_dir = extracted_dirs[0]
        
        # Check structure
        if (source_dir / 'Training').exists():
            print("Detected Training/Testing structure")
            organize_training_testing(source_dir, classes)
        elif (source_dir / classes[0]).exists():
            print("Detected existing class structure")
            organize_existing(source_dir, classes)
        else:
            print("❌ Unknown dataset structure")
            print(f"Contents: {list(source_dir.iterdir())}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Organization failed: {e}")
        return False


def organize_training_testing(source_dir: Path, classes: list):
    """Organize Training/Testing structure."""
    import shutil
    
    data_dir = Path("data/raw")
    training_dir = source_dir / 'Training'
    
    for class_name in classes:
        class_source = training_dir / class_name
        class_target = data_dir / class_name
        
        if class_source.exists():
            class_target.mkdir(exist_ok=True)
            
            # Copy images
            count = 0
            for img_file in class_source.glob('*'):
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    shutil.copy2(img_file, class_target / img_file.name)
                    count += 1
            
            print(f"  ✅ {class_name:12s}: {count:4d} images")
    
    # Cleanup
    shutil.rmtree(source_dir)


def organize_existing(source_dir: Path, classes: list):
    """Move existing class folders."""
    import shutil
    
    data_dir = Path("data/raw")
    
    for class_name in classes:
        class_source = source_dir / class_name
        class_target = data_dir / class_name
        
        if class_source.exists():
            if class_target.exists():
                shutil.rmtree(class_target)
            shutil.move(str(class_source), str(class_target))
            
            count = len(list(class_target.glob('*')))
            print(f"  ✅ {class_name:12s}: {count:4d} images")
    
    # Cleanup
    shutil.rmtree(source_dir)


def validate_dataset() -> dict:
    """Validate dataset structure."""
    print_step(4, "VALIDATE DATASET")
    
    data_dir = Path("data/raw")
    classes = ['glioma', 'meningioma', 'pituitary', 'no_tumor']
    stats = {}
    total = 0
    
    print("Checking dataset structure:\n")
    
    for class_name in classes:
        class_dir = data_dir / class_name
        
        if class_dir.exists():
            count = len(list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png')))
            stats[class_name] = count
            total += count
            print(f"  ✅ {class_name:12s}: {count:5d} images")
        else:
            print(f"  ❌ {class_name:12s}: NOT FOUND")
            stats[class_name] = 0
    
    print(f"\n  📊 Total images: {total}")
    
    # Save stats
    stats_file = data_dir / 'dataset_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    if total > 0:
        print("  ✅ Dataset validation successful!")
        return stats
    else:
        print("  ❌ Dataset validation failed!")
        return {}


def test_training():
    """Offer to run test training."""
    print_step(5, "READY TO TRAIN")
    
    print("""
✅ Dataset setup complete!

You can now train the model with:

    python train.py --data-dir data/raw

OPTIONS:
  
  Quick test (1 epoch, minimal data):
    python train.py --data-dir data/raw --config configs/config.yaml
  
  Full training (GPU recommended):
    python train.py --data-dir data/raw
  
  Monitor training with TensorBoard (in another terminal):
    tensorboard --logdir=results/logs
    Then visit: http://localhost:6006

Run training now? (y/n): """)
    
    response = input().strip().lower()
    
    if response == 'y':
        print("\n🚀 Starting training...")
        os.system("python train.py --data-dir data/raw")
    else:
        print("\n✅ Ready when you are! Run 'python train.py --data-dir data/raw' to start.")


def main():
    """Main execution."""
    print_header("BRAIN TUMOR CLASSIFICATION - KAGGLE DATASET SETUP")
    
    print("""
This script will:
  1. Install Kaggle API (if needed)
  2. Guide you to set up credentials
  3. Download Brain Tumor MRI dataset
  4. Organize dataset structure
  5. Validate and show statistics
""")
    
    # Step 1: Check/Install Kaggle
    print_step(0, "CHECK KAGGLE API")
    
    if not check_kaggle_installed():
        print("Kaggle not installed. Installing now...")
        if not install_kaggle():
            print("❌ Setup failed")
            sys.exit(1)
    else:
        print("✅ Kaggle API already installed")
    
    # Step 2: Setup credentials
    if not check_credentials():
        setup_credentials_guide()
    else:
        print_step(1, "CREDENTIALS FOUND")
        print("✅ Kaggle credentials already configured")
    
    # Verify credentials work
    if not verify_credentials():
        print("❌ Credentials verification failed. Please check and try again.")
        sys.exit(1)
    
    # Step 3: Download
    if not download_dataset():
        print("❌ Dataset download failed")
        sys.exit(1)
    
    # Step 4: Organize
    if not organize_dataset():
        print("⚠️  Dataset organization had issues, but continuing...")
    
    # Step 5: Validate
    stats = validate_dataset()
    if not stats or sum(stats.values()) == 0:
        print("❌ Dataset validation failed")
        sys.exit(1)
    
    # Step 6: Offer training
    print()
    test_training()
    
    print_header("✅ SETUP COMPLETE!")
    print("\nYou're ready to train the Brain Tumor Classification model!")
    print("\nFor more information, see:")
    print("  - README.md")
    print("  - QUICKSTART.md")
    print("  - KAGGLE_SETUP.md")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
