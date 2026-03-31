import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms import functional as F


class ImagePreprocessor:
    def __init__(self):
        self.target_size = (224, 224)
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.mean, std=self.std)
        ])
        
        self.train_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.mean, std=self.std)
        ])
    
    def set_target_size(self, size):
        if isinstance(size, int):
            self.target_size = (size, size)
        else:
            self.target_size = size
        
        self.transform = transforms.Compose([
            transforms.Resize(self.target_size[0] + 32),
            transforms.CenterCrop(self.target_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.mean, std=self.std)
        ])
    
    def load_image(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"无法加载图像: {e}")
    
    def preprocess(self, image_path, is_training=False):
        image = self.load_image(image_path)
        
        if is_training:
            return self.train_transform(image)
        else:
            return self.transform(image)
    
    def preprocess_pil(self, image, is_training=False):
        if is_training:
            return self.train_transform(image)
        else:
            return self.transform(image)
    
    def denormalize(self, tensor):
        mean = torch.tensor(self.mean).view(3, 1, 1)
        std = torch.tensor(self.std).view(3, 1, 1)
        return tensor * std + mean
    
    def tensor_to_pil(self, tensor):
        if tensor.dim() == 4:
            tensor = tensor[0]
        tensor = self.denormalize(tensor)
        tensor = torch.clamp(tensor, 0, 1)
        return F.to_pil_image(tensor)
    
    def enhance_image(self, image_path, method='adaptive'):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("无法读取图像")
        
        if method == 'adaptive':
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        elif method == 'histogram':
            for i in range(3):
                img[:, :, i] = cv2.equalizeHist(img[:, :, i])
        elif method == 'denoise':
            img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        return img
    
    def augment_batch(self, image_path, num_augmentations=5):
        image = self.load_image(image_path)
        augmented = []
        
        for _ in range(num_augmentations):
            aug_img = image.copy()
            
            if np.random.random() > 0.5:
                aug_img = F.hflip(aug_img)
            
            if np.random.random() > 0.5:
                angle = np.random.uniform(-15, 15)
                aug_img = F.rotate(aug_img, angle)
            
            if np.random.random() > 0.5:
                brightness = np.random.uniform(0.8, 1.2)
                aug_img = F.adjust_brightness(aug_img, brightness)
            
            if np.random.random() > 0.5:
                contrast = np.random.uniform(0.8, 1.2)
                aug_img = F.adjust_contrast(aug_img, contrast)
            
            augmented.append(aug_img)
        
        return augmented
