import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import pandas as pd
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class RecognitionThread(QThread):
    progress_updated = pyqtSignal(int, str)
    recognition_finished = pyqtSignal(list)
    
    def __init__(self, model, image_paths, classes, device, transform):
        super().__init__()
        self.model = model
        self.image_paths = image_paths
        self.classes = classes
        self.device = device
        self.transform = transform
    
    def run(self):
        results = []
        
        for i, img_path in enumerate(self.image_paths):
            try:
                image = Image.open(img_path).convert('RGB')
                image_tensor = self.transform(image).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(image_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    confidence, predicted = torch.max(probabilities, 1)
                    
                    predicted_class = self.classes[predicted.item()]
                    confidence_value = confidence.item() * 100
                
                results.append({
                    'image_path': img_path,
                    'predicted_class': predicted_class,
                    'confidence': confidence_value,
                    'all_probabilities': {
                        cls: prob.item() * 100 
                        for cls, prob in zip(self.classes, probabilities[0])
                    }
                })
                
            except Exception as e:
                results.append({
                    'image_path': img_path,
                    'predicted_class': '错误',
                    'confidence': 0,
                    'error': str(e)
                })
            
            progress = int((i + 1) / len(self.image_paths) * 100)
            self.progress_updated.emit(progress, f"识别中: {os.path.basename(img_path)}")
        
        self.recognition_finished.emit(results)


class ImageRecognizer(QObject):
    def __init__(self):
        super().__init__()
        self.model = None
        self.classes = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self, model_path):
        checkpoint = torch.load(model_path, map_location=self.device)
        
        if 'model_state_dict' in checkpoint:
            num_classes = checkpoint['model_state_dict'].get('fc.weight', 
                         checkpoint['model_state_dict'].get('classifier.6.weight')).shape[0]
        else:
            num_classes = 2
        
        self.model = models.resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        
        if 'classes' in checkpoint:
            self.classes = checkpoint['classes']
        else:
            self.classes = [f"类别{i}" for i in range(num_classes)]
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        return self.model
    
    def recognize_single(self, image_path):
        if self.model is None:
            raise ValueError("模型未加载")
        
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                predicted_class = self.classes[predicted.item()]
                confidence_value = confidence.item() * 100
                
                all_probs = {
                    cls: prob.item() * 100 
                    for cls, prob in zip(self.classes, probabilities[0])
                }
            
            return {
                'image_path': image_path,
                'predicted_class': predicted_class,
                'confidence': confidence_value,
                'all_probabilities': all_probs
            }
            
        except Exception as e:
            return {
                'image_path': image_path,
                'predicted_class': '错误',
                'confidence': 0,
                'error': str(e)
            }
    
    def recognize_batch(self, image_paths):
        if self.model is None:
            raise ValueError("模型未加载")
        
        results = []
        
        for img_path in image_paths:
            result = self.recognize_single(img_path)
            results.append(result)
        
        return results
    
    def recognize_batch_async(self, image_paths):
        if self.model is None:
            raise ValueError("模型未加载")
        
        thread = RecognitionThread(
            self.model, image_paths, self.classes, self.device, self.transform
        )
        
        return thread
    
    def export_results(self, results, output_path, format='csv'):
        if format == 'csv':
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        elif format == 'json':
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        
        return output_path
