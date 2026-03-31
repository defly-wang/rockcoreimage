import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms, models
from PIL import Image
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class ImageDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            return torch.zeros(3, 224, 224), label


class TrainingThread(QThread):
    progress_updated = pyqtSignal(int, str)
    epoch_finished = pyqtSignal(int, float, float, float, float)
    training_finished = pyqtSignal(str, float)
    
    def __init__(self, model, train_loader, val_loader, criterion, optimizer, 
                 num_epochs, device, save_path):
        super().__init__()
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.num_epochs = num_epochs
        self.device = device
        self.save_path = save_path
        self.best_val_acc = 0.0
    
    def run(self):
        for epoch in range(self.num_epochs):
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for i, (images, labels) in enumerate(self.train_loader):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                
                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += labels.size(0)
                train_correct += predicted.eq(labels).sum().item()
                
                progress = int((i + 1) / len(self.train_loader) * 100)
                self.progress_updated.emit(progress, f"Epoch {epoch+1}/{self.num_epochs} - 训练中")
            
            train_loss = train_loss / len(self.train_loader)
            train_acc = 100.0 * train_correct / train_total
            
            val_loss, val_acc = self.validate()
            
            self.epoch_finished.emit(
                epoch + 1, 
                train_loss, 
                train_acc, 
                val_loss, 
                val_acc
            )
            
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                }, self.save_path)
        
        self.training_finished.emit(self.save_path, self.best_val_acc)
    
    def validate(self):
        self.model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in self.val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_loss = val_loss / len(self.val_loader)
        val_acc = 100.0 * val_correct / val_total
        
        return val_loss, val_acc


class ModelTrainer(QObject):
    def __init__(self):
        super().__init__()
        self.model = None
        self.train_loader = None
        self.val_loader = None
        self.classes = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_data(self, data_dir, batch_size=32, train_ratio=0.8):
        image_paths = []
        labels = []
        class_names = sorted([d for d in os.listdir(data_dir) 
                             if os.path.isdir(os.path.join(data_dir, d))])
        
        self.classes = class_names
        
        for class_idx, class_name in enumerate(class_names):
            class_dir = os.path.join(data_dir, class_name)
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    image_paths.append(os.path.join(class_dir, img_name))
                    labels.append(class_idx)
        
        if not image_paths:
            raise ValueError("未找到任何图像数据")
        
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        train_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        dataset = ImageDataset(image_paths, labels, transform)
        
        train_size = int(train_ratio * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        
        train_dataset.dataset.transform = train_transform
        
        self.train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
        )
        self.val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )
        
        return len(train_dataset), len(val_dataset), len(class_names)
    
    def create_model(self, model_name='resnet18', num_classes=2):
        if model_name == 'resnet18':
            self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        elif model_name == 'resnet50':
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        elif model_name == 'vgg16':
            self.model = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
            self.model.classifier[-1] = nn.Linear(4096, num_classes)
        elif model_name == 'efficientnet_b0':
            self.model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
            self.model.classifier[-1] = nn.Linear(self.model.classifier[-1].in_features, num_classes)
        else:
            self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        
        self.model = self.model.to(self.device)
        return self.model
    
    def start_training(self, num_epochs, learning_rate, save_path, weight_decay=0.0001):
        if self.model is None:
            raise ValueError("模型未创建")
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        
        training_thread = TrainingThread(
            self.model, self.train_loader, self.val_loader,
            criterion, optimizer, num_epochs, self.device, save_path
        )
        
        return training_thread
    
    def save_model(self, path):
        if self.model is not None:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'classes': self.classes
            }, path)
    
    def load_model(self, path):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.classes = checkpoint.get('classes', [])
        self.model = self.model.to(self.device)
        self.model.eval()
        return self.model
