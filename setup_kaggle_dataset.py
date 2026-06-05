"""
Script to download and prepare Kaggle Brain Tumor MRI dataset.

Dataset: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List
import subprocess
import sys


class KaggleDatasetSetup:
    """Setup and prepare Kaggle Brain Tumor MRI dataset."""
    
    DATASET_NAME = "masoudnickparvar/brain-tumor-mri-dataset"
    CLASSES = ['glioma', 'meningioma', 'pituitary', 'no_tumor']
    DATA_DIR = Path('data/raw')
    
    def __init__(self):
        """Initialize dataset setup."""
        self.data_dir = self.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def check_kaggle_api(self) -> bool:
        """Check if Kaggle API is installed and configured."""
        try:
            import kaggle
            
            # Check if credentials exist
            credentials_path = Path.home() / '.kaggle' / 'kaggle.json'
            if not credentials_path.exists():
                print("❌ Kaggle credentials not found!")
                print(f"   Expected path: {credentials_path}")
                return False
            
            print("✅ Kaggle API found and configured")
            return True
        except ImportError:
            print("❌ Kaggle API not installed")
            return False
    
    def setup_kaggle_credentials(self):
        """
        Guide user to set up Kaggle credentials.
        """
        print("\n" + "="*70)
        print("KAGGLE CREDENTIALS SETUP")
        print("="*70)
        print("""
1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New API Token"
   - This downloads kaggle.json
4. Move kaggle.json to ~/.kaggle/kaggle.json
5. Set permissions: chmod 600 ~/.kaggle/kaggle.json (Linux/Mac)

On Windows, the path is typically:
  C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
        """)
    
    def install_kaggle_api(self) -> bool:
        """Install Kaggle API."""
        try:
            print("Installing Kaggle API...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
            print("✅ Kaggle API installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Kaggle API")
            return False
    
    def download_dataset(self) -> bool:
        """Download dataset from Kaggle."""
        try:
            import kaggle
            
            print(f"\n📥 Downloading dataset: {self.DATASET_NAME}")
            print(f"   Destination: {self.data_dir}")
            
            # Download dataset
            kaggle.api.dataset_download_files(
                self.DATASET_NAME,
                path=str(self.data_dir),
                unzip=True
            )
            
            print("✅ Dataset downloaded successfully")
            return True
        
        except Exception as e:
            print(f"❌ Download failed: {e}")
            print("\nTroubleshooting:")
            print("1. Verify Kaggle credentials are set up correctly")
            print("2. Check internet connection")
            print("3. Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset")
            print("   and accept the dataset terms")
            return False
    
    def organize_dataset(self) -> bool:
        """Organize downloaded dataset into class subdirectories."""
        try:
            print("\n📁 Organizing dataset...")
            
            # Find the extracted folder
            extracted_folders = [
                d for d in self.data_dir.iterdir() 
                if d.is_dir() and d.name != '__MACOSX'
            ]
            
            if not extracted_folders:
                print("❌ No extracted folders found")
                return False
            
            source_dir = extracted_folders[0]
            print(f"   Source: {source_dir}")
            
            # Check for typical Kaggle dataset structure
            if (source_dir / 'Training').exists():
                # Dataset has Training/Testing structure
                return self._organize_training_testing_structure(source_dir)
            elif (source_dir / self.CLASSES[0]).exists():
                # Dataset already has class subdirectories
                return self._organize_existing_structure(source_dir)
            else:
                print("❌ Unknown dataset structure")
                print(f"   Contents: {list(source_dir.iterdir())}")
                return False
        
        except Exception as e:
            print(f"❌ Organization failed: {e}")
            return False
    
    def _organize_training_testing_structure(self, source_dir: Path) -> bool:
        """Organize Training/Testing structure into class folders."""
        try:
            training_dir = source_dir / 'Training'
            
            for class_name in self.CLASSES:
                class_source = training_dir / class_name
                class_target = self.data_dir / class_name
                
                if not class_source.exists():
                    print(f"   ⚠️  Missing class: {class_name}")
                    continue
                
                # Create target directory
                class_target.mkdir(exist_ok=True)
                
                # Copy images
                image_count = 0
                for img_file in class_source.glob('*'):
                    if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        target_file = class_target / img_file.name
                        shutil.copy2(img_file, target_file)
                        image_count += 1
                
                print(f"   ✅ {class_name}: {image_count} images")
            
            # Cleanup
            shutil.rmtree(source_dir)
            return True
        
        except Exception as e:
            print(f"❌ Structure organization failed: {e}")
            return False
    
    def _organize_existing_structure(self, source_dir: Path) -> bool:
        """Move existing class folders to data/raw."""
        try:
            for class_name in self.CLASSES:
                class_source = source_dir / class_name
                class_target = self.data_dir / class_name
                
                if class_source.exists():
                    if class_target.exists():
                        shutil.rmtree(class_target)
                    shutil.move(str(class_source), str(class_target))
                    image_count = len(list(class_target.glob('*')))
                    print(f"   ✅ {class_name}: {image_count} images")
            
            # Cleanup
            shutil.rmtree(source_dir)
            return True
        
        except Exception as e:
            print(f"❌ Existing structure organization failed: {e}")
            return False
    
    def validate_dataset(self) -> Dict[str, int]:
        """Validate dataset structure and count images."""
        print("\n✓ Validating dataset...")
        
        stats = {}
        total_images = 0
        
        for class_name in self.CLASSES:
            class_dir = self.data_dir / class_name
            
            if not class_dir.exists():
                print(f"   ❌ Missing: {class_name}/")
                stats[class_name] = 0
                continue
            
            # Count images
            images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
            count = len(images)
            total_images += count
            stats[class_name] = count
            
            print(f"   ✅ {class_name:12s}: {count:4d} images")
        
        print(f"\n   Total images: {total_images}")
        
        # Save stats
        stats_file = self.data_dir / 'dataset_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=4)
        
        return stats
    
    def run_setup(self) -> bool:
        """Run complete setup pipeline."""
        print("\n" + "="*70)
        print("KAGGLE BRAIN TUMOR MRI DATASET SETUP")
        print("="*70)
        
        # Step 1: Check/Install Kaggle API
        if not self.check_kaggle_api():
            print("\n" + "-"*70)
            self.setup_kaggle_credentials()
            
            if not self.install_kaggle_api():
                return False
            
            print("\n⚠️  After setting up credentials, run this script again.")
            return False
        
        # Step 2: Download dataset
        print("\n" + "-"*70)
        if not self.download_dataset():
            return False
        
        # Step 3: Organize dataset
        print("\n" + "-"*70)
        if not self.organize_dataset():
            return False
        
        # Step 4: Validate dataset
        print("\n" + "-"*70)
        stats = self.validate_dataset()
        
        if sum(stats.values()) == 0:
            print("\n❌ Dataset validation failed!")
            return False
        
        print("\n" + "="*70)
        print("✅ DATASET SETUP COMPLETE!")
        print("="*70)
        print("\nYou can now train the model with:")
        print("  python train.py --data-dir data/raw")
        
        return True


def main():
    """Main entry point."""
    setup = KaggleDatasetSetup()
    
    if setup.run_setup():
        print("\n🎉 Ready to start training!")
        sys.exit(0)
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
