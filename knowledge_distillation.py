#!/usr/bin/env python3
"""Knowledge Distillation for model compression."""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
import sys
from pathlib import Path
from tqdm import tqdm
import time

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.model import BrainTumorClassifier
from data.data_loader import BrainTumorDataset
from utils.config import Config

class DistillationLoss(nn.Module):
    """Knowledge Distillation Loss (KL divergence + CE)."""
    
    def __init__(self, temperature=4.0, alpha=0.7):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
        self.kl_loss = nn.KLDivLoss(reduction='batchmean')
    
    def forward(self, student_logits, teacher_logits, labels):
        """
        Compute distillation loss.
        
        Args:
            student_logits: Student model outputs
            teacher_logits: Teacher model outputs
            labels: Ground truth labels
        """
        # Hard target loss (CE)
        ce = self.ce_loss(student_logits, labels)
        
        # Soft target loss (KL divergence)
        student_soft = torch.log_softmax(student_logits / self.temperature, dim=1)
        teacher_soft = torch.softmax(teacher_logits / self.temperature, dim=1)
        kl = self.kl_loss(student_soft, teacher_soft)
        
        # Combined loss
        loss = self.alpha * ce + (1 - self.alpha) * kl * (self.temperature ** 2)
        
        return loss

class StudentModel(nn.Module):
    """Lightweight student model for knowledge distillation."""
    
    def __init__(self, num_classes=4, hidden_dim=256):
        super().__init__()
        # Lightweight architecture (4x smaller than teacher)
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AvgPool2d(kernel_size=7, stride=7),
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(64, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(hidden_dim, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

class KnowledgeDistiller:
    """Train student model from teacher model."""
    
    def __init__(self, teacher_model, device='cpu', temperature=4.0, alpha=0.7):
        """Initialize distiller."""
        self.device = torch.device(device)
        self.teacher = teacher_model.to(self.device)
        self.teacher.eval()
        
        self.temperature = temperature
        self.alpha = alpha
        
        self.criterion = DistillationLoss(temperature=temperature, alpha=alpha)
    
    def train_student(self, student_model, train_loader, val_loader, 
                     epochs=20, learning_rate=0.001, output_path='models/student_model.pth'):
        """Train student model."""
        print(f"\n{'='*60}")
        print("KNOWLEDGE DISTILLATION TRAINING".center(60))
        print(f"{'='*60}")
        print(f"Temperature: {self.temperature}, Alpha: {self.alpha}")
        
        student = student_model.to(self.device)
        student.train()
        
        optimizer = optim.Adam(student.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=3, verbose=True
        )
        
        best_val_acc = 0
        
        for epoch in range(epochs):
            # Training
            student.train()
            train_loss = 0
            train_correct = 0
            train_total = 0
            
            pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
            for images, labels in pbar:
                images, labels = images.to(self.device), labels.to(self.device)
                
                # Forward pass
                with torch.no_grad():
                    teacher_logits = self.teacher(images)
                
                student_logits = student(images)
                
                # Compute loss
                loss = self.criterion(student_logits, teacher_logits, labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                # Statistics
                train_loss += loss.item()
                _, predicted = torch.max(student_logits.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
                
                pbar.set_postfix({
                    'loss': loss.item(),
                    'acc': 100 * train_correct / train_total
                })
            
            avg_train_loss = train_loss / len(train_loader)
            train_acc = 100 * train_correct / train_total
            
            # Validation
            student.eval()
            val_loss = 0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    
                    teacher_logits = self.teacher(images)
                    student_logits = student(images)
                    
                    loss = self.criterion(student_logits, teacher_logits, labels)
                    
                    val_loss += loss.item()
                    _, predicted = torch.max(student_logits.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            
            avg_val_loss = val_loss / len(val_loader)
            val_acc = 100 * val_correct / val_total
            
            print(f"Epoch {epoch+1}: Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                  f"Val Loss={avg_val_loss:.4f}, Val Acc={val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'model_state_dict': student.state_dict(),
                    'accuracy': val_acc,
                    'epoch': epoch
                }, output_path)
                print(f"✅ Best model saved (Acc: {val_acc:.2f}%)")
            
            scheduler.step(avg_val_loss)
        
        print(f"✅ Training complete. Best accuracy: {best_val_acc:.2f}%")
        return student

class DistillationAnalyzer:
    """Analyze distillation performance."""
    
    @staticmethod
    def compare_student_teacher(teacher, student, test_loader, device='cpu'):
        """Compare student and teacher models."""
        device = torch.device(device)
        
        print("\n" + "="*60)
        print("DISTILLATION ANALYSIS".center(60))
        print("="*60)
        
        teacher = teacher.to(device)
        student = student.to(device)
        
        teacher.eval()
        student.eval()
        
        teacher_correct = 0
        student_correct = 0
        teacher_time = 0
        student_time = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                
                # Teacher inference
                start = time.perf_counter()
                teacher_outputs = teacher(images)
                teacher_time += (time.perf_counter() - start)
                
                # Student inference
                start = time.perf_counter()
                student_outputs = student(images)
                student_time += (time.perf_counter() - start)
                
                _, teacher_preds = torch.max(teacher_outputs, 1)
                _, student_preds = torch.max(student_outputs, 1)
                
                teacher_correct += (teacher_preds == labels).sum().item()
                student_correct += (student_preds == labels).sum().item()
                total += labels.size(0)
        
        teacher_acc = 100 * teacher_correct / total
        student_acc = 100 * student_correct / total
        teacher_time_ms = (teacher_time / len(test_loader)) * 1000
        student_time_ms = (student_time / len(test_loader)) * 1000
        speedup = teacher_time_ms / student_time_ms
        
        print(f"\nAccuracy:")
        print(f"  Teacher: {teacher_acc:.2f}%")
        print(f"  Student: {student_acc:.2f}%")
        print(f"  Accuracy Drop: {teacher_acc - student_acc:.2f}%")
        
        print(f"\nInference Time:")
        print(f"  Teacher: {teacher_time_ms:.2f} ms")
        print(f"  Student: {student_time_ms:.2f} ms")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Model sizes
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            torch.save(teacher, f.name)
            teacher_size = os.path.getsize(f.name) / (1024*1024)
            os.unlink(f.name)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            torch.save(student, f.name)
            student_size = os.path.getsize(f.name) / (1024*1024)
            os.unlink(f.name)
        
        compression = teacher_size / student_size
        
        print(f"\nModel Size:")
        print(f"  Teacher: {teacher_size:.2f} MB")
        print(f"  Student: {student_size:.2f} MB")
        print(f"  Compression: {compression:.2f}x")
        
        print("="*60)
        
        return {
            'teacher_accuracy': teacher_acc,
            'student_accuracy': student_acc,
            'accuracy_drop': teacher_acc - student_acc,
            'teacher_latency_ms': teacher_time_ms,
            'student_latency_ms': student_time_ms,
            'speedup': speedup,
            'teacher_size_mb': teacher_size,
            'student_size_mb': student_size,
            'compression_ratio': compression
        }

def main():
    """Main distillation pipeline."""
    parser = argparse.ArgumentParser(description='Knowledge Distillation')
    parser.add_argument('--teacher-model', type=str, default='models/best_model.pth',
                       help='Path to teacher model')
    parser.add_argument('--data-dir', type=str, default='data/raw',
                       help='Path to data directory')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'])
    parser.add_argument('--epochs', type=int, default=20,
                       help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--temperature', type=float, default=4.0,
                       help='Distillation temperature')
    parser.add_argument('--alpha', type=float, default=0.7,
                       help='Weight for CE loss (1-alpha for KL loss)')
    parser.add_argument('--output', type=str, default='models/student_model.pth',
                       help='Output student model path')
    
    args = parser.parse_args()
    
    # Load teacher model
    print("Loading teacher model...")
    config = Config('configs/config.yaml')
    
    teacher = BrainTumorClassifier(
        backbone=config.model['backbone'],
        num_classes=config.model['num_classes'],
        pretrained=False
    )
    
    checkpoint = torch.load(args.teacher_model, map_location=args.device)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        teacher.load_state_dict(checkpoint['model_state_dict'])
    else:
        teacher.load_state_dict(checkpoint)
    
    # Load data
    print("Loading training data...")
    train_dataset = BrainTumorDataset(
        data_dir=args.data_dir,
        split='train',
        image_size=config.data['image_size'],
        augment=True
    )
    
    val_dataset = BrainTumorDataset(
        data_dir=args.data_dir,
        split='test',
        image_size=config.data['image_size'],
        augment=False
    )
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Knowledge Distillation
    distiller = KnowledgeDistiller(
        teacher, 
        device=args.device,
        temperature=args.temperature,
        alpha=args.alpha
    )
    
    # Create and train student
    student = StudentModel(num_classes=config.model['num_classes'])
    distiller.train_student(
        student, 
        train_loader, 
        val_loader,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        output_path=args.output
    )
    
    # Load best student
    checkpoint = torch.load(args.output)
    student.load_state_dict(checkpoint['model_state_dict'])
    
    # Analyze
    KnowledgeDistiller.compare_student_teacher(teacher, student, val_loader, args.device)

if __name__ == '__main__':
    main()
