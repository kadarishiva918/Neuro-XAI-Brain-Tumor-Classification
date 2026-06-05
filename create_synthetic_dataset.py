"""
Generate synthetic brain tumor MRI dataset for testing the pipeline.
Creates realistic synthetic MRI images using noise and patterns.
"""

import os
import numpy as np
from pathlib import Path
import cv2
from tqdm import tqdm


class SyntheticMRIGenerator:
    """Generate synthetic brain tumor MRI images."""
    
    CLASSES = ['glioma', 'meningioma', 'pituitary', 'no_tumor']
    IMG_SIZE = 256
    IMAGES_PER_CLASS = 80  # 80 images per class for quick demo
    
    def __init__(self, output_dir='data/raw'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_mri_image(self, tumor_type='no_tumor'):
        """Generate a synthetic MRI image."""
        # Create base brain structure
        img = np.zeros((self.IMG_SIZE, self.IMG_SIZE), dtype=np.uint8)
        
        # Add brain tissue (circular region)
        center = (self.IMG_SIZE // 2, self.IMG_SIZE // 2)
        radius = self.IMG_SIZE // 2 - 20
        cv2.circle(img, center, radius, 150, -1)
        
        # Add texture/noise
        noise = np.random.normal(0, 10, img.shape)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        
        # Add tumor-specific patterns
        if tumor_type == 'glioma':
            # Glioma: irregular bright region in brain
            x, y = np.random.randint(80, 176, 2)
            cv2.ellipse(img, (x, y), (30, 25), np.random.randint(0, 180), 
                       0, 360, 200, -1)
            cv2.ellipse(img, (x+5, y+5), (20, 15), np.random.randint(0, 180),
                       0, 360, 220, -1)
        
        elif tumor_type == 'meningioma':
            # Meningioma: smooth bounded mass
            x, y = np.random.randint(80, 176, 2)
            cv2.circle(img, (x, y), 25, 180, -1)
            cv2.circle(img, (x, y), 15, 210, -1)
        
        elif tumor_type == 'pituitary':
            # Pituitary: small region in center
            x, y = self.IMG_SIZE // 2, self.IMG_SIZE // 2
            cv2.circle(img, (x + np.random.randint(-10, 10), 
                            y + np.random.randint(-10, 10)), 
                      12, 200, -1)
        
        # Add realistic MRI artifacts
        img = self._add_artifacts(img)
        
        return img
    
    def _add_artifacts(self, img):
        """Add realistic MRI artifacts."""
        # Add Gaussian blur
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Add subtle gradient
        gradient = np.linspace(0, 30, self.IMG_SIZE)
        gradient = np.tile(gradient, (self.IMG_SIZE, 1))
        img = np.clip(img.astype(float) + gradient * 0.3, 0, 255).astype(np.uint8)
        
        return img
    
    def create_dataset(self):
        """Create synthetic dataset."""
        print("\n🧠 Creating Synthetic Brain Tumor MRI Dataset")
        print("=" * 60)
        
        for class_name in self.CLASSES:
            class_dir = self.output_dir / class_name
            class_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📁 Generating {class_name.upper()} images...")
            
            for i in tqdm(range(self.IMAGES_PER_CLASS), desc=class_name):
                # Generate image
                img = self.generate_mri_image(class_name)
                
                # Save image
                filename = f"{class_name}_{i:04d}.jpg"
                filepath = class_dir / filename
                cv2.imwrite(str(filepath), img)
        
        self.print_summary()
    
    def print_summary(self):
        """Print dataset summary."""
        print("\n" + "=" * 60)
        print("✅ SYNTHETIC DATASET CREATED SUCCESSFULLY")
        print("=" * 60)
        
        total_images = 0
        for class_name in self.CLASSES:
            class_dir = self.output_dir / class_name
            image_count = len(list(class_dir.glob('*.jpg')))
            total_images += image_count
            print(f"  {class_name:12} : {image_count:3} images")
        
        print("-" * 60)
        print(f"  {'TOTAL':12} : {total_images:3} images")
        print("=" * 60)
        print(f"\n📁 Dataset location: {self.output_dir.absolute()}")
        print("✅ Ready for training!")


if __name__ == '__main__':
    generator = SyntheticMRIGenerator()
    generator.create_dataset()
