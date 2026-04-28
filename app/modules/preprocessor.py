import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms import functional as F
import os


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
    
    def split_image(self, image_path, target_size=None, cols=2):
        if target_size is None:
            target_size = self.target_size
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        h, w = img.shape[:2]
        target_w, target_h = target_size
        
        max_rows = h // target_h
        if max_rows == 0:
            max_rows = 1
        
        if max_rows > 50:
            max_rows = 50
        
        total_needed_w = cols * target_w
        total_needed_h = max_rows * target_h
        
        start_x = max(0, (w - total_needed_w) // 2)
        start_y = max(0, (h - total_needed_h) // 2)
        
        split_images = []
        for row in range(max_rows):
            for col in range(cols):
                x = start_x + col * target_w
                y = start_y + row * target_h
                
                if x + target_w <= w and y + target_h <= h:
                    crop = img[y:y+target_h, x:x+target_w]
                    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                    split_images.append(Image.fromarray(crop_rgb))
        
        return split_images
    
    def augment_image_with_options(self, image, brightness=True, contrast=True, 
                                  saturation=True, flip=True, rotation=True,
                                  noise=False, blur=False):
        augmented = []
        
        for _ in range(5):
            aug_img = image.copy()
            
            if flip and np.random.random() > 0.5:
                aug_img = F.hflip(aug_img)
            
            if rotation and np.random.random() > 0.5:
                angle = np.random.uniform(-15, 15)
                aug_img = F.rotate(aug_img, angle)
            
            if brightness and np.random.random() > 0.5:
                brightness_factor = np.random.uniform(0.8, 1.2)
                aug_img = F.adjust_brightness(aug_img, brightness_factor)
            
            if contrast and np.random.random() > 0.5:
                contrast_factor = np.random.uniform(0.8, 1.2)
                aug_img = F.adjust_contrast(aug_img, contrast_factor)
            
            if saturation and np.random.random() > 0.5:
                saturation_factor = np.random.uniform(0.8, 1.2)
                aug_img = F.adjust_saturation(aug_img, saturation_factor)
            
            if noise and np.random.random() > 0.5:
                img_array = np.array(aug_img)
                noise_arr = np.random.normal(0, 25, img_array.shape).astype(np.uint8)
                img_array = cv2.add(img_array, noise_arr)
                aug_img = Image.fromarray(img_array)
            
            if blur and np.random.random() > 0.5:
                img_array = np.array(aug_img)
                img_array = cv2.GaussianBlur(img_array, (5, 5), 1.0)
                aug_img = Image.fromarray(img_array)
            
            augmented.append(aug_img)
        
        return augmented
    
    def process_image(self, image_path, target_size=None, num_augmentations=5):
        if target_size is None:
            target_size = self.target_size
        
        split_images = self.split_image(image_path, target_size)
        
        all_processed = []
        for split_img in split_images:
            all_processed.append(split_img)
            
            augmented = self.augment_image(split_img, num_augmentations)
            all_processed.extend(augmented)
        
        return all_processed
    
    def process_and_save(self, input_dir, output_dir, target_size=None, num_augmentations=5, progress_callback=None):
        if target_size is None:
            target_size = self.target_size
        
        images_dir = os.path.join(input_dir, 'images')
        if not os.path.exists(images_dir):
            raise ValueError(f"输入目录中没有images子目录: {images_dir}")
        
        output_images_dir = os.path.join(output_dir, 'images')
        os.makedirs(output_images_dir, exist_ok=True)
        
        image_files = []
        for f in os.listdir(images_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(os.path.join(images_dir, f))
        
        total_processed = 0
        for idx, img_path in enumerate(image_files):
            try:
                processed_images = self.process_image(img_path, target_size, num_augmentations)
                
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                for aug_idx, proc_img in enumerate(processed_images):
                    output_path = os.path.join(output_images_dir, f"{base_name}_{aug_idx:04d}.jpg")
                    proc_img.save(output_path, 'JPEG', quality=95)
                    total_processed += 1
                
                if progress_callback:
                    progress = int((idx + 1) / len(image_files) * 100)
                    progress_callback(progress, f"处理中: {idx + 1}/{len(image_files)}")
                    
            except Exception as e:
                print(f"处理图像失败 {img_path}: {e}")
        
        return total_processed, len(image_files)
    
    def process_and_save_with_options(self, input_dir, output_dir, target_size=None,
                                     brightness=True, contrast=True, saturation=True,
                                     flip=True, rotation=True, noise=False, blur=False,
                                     progress_callback=None):
        if target_size is None:
            target_size = self.target_size
        
        images_dir = os.path.join(input_dir, 'images')
        if not os.path.exists(images_dir):
            raise ValueError(f"输入目录中没有images子目录: {images_dir}")
        
        output_images_dir = os.path.join(output_dir, 'images')
        os.makedirs(output_images_dir, exist_ok=True)
        
        image_files = []
        for f in os.listdir(images_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(os.path.join(images_dir, f))
        
        total_processed = 0
        for idx, img_path in enumerate(image_files):
            try:
                split_images = self.split_image(img_path, target_size)
                
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                img_idx = 0
                
                for split_img in split_images:
                    output_path = os.path.join(output_images_dir, f"{base_name}_{img_idx:04d}.jpg")
                    split_img.save(output_path, 'JPEG', quality=95)
                    total_processed += 1
                    img_idx += 1
                    
                    augmented = self.augment_image_with_options(
                        split_img, brightness, contrast, saturation,
                        flip, rotation, noise, blur
                    )
                    
                    for aug_img in augmented:
                        output_path = os.path.join(output_images_dir, f"{base_name}_{img_idx:04d}.jpg")
                        aug_img.save(output_path, 'JPEG', quality=95)
                        total_processed += 1
                        img_idx += 1
                
                if progress_callback:
                    progress = int((idx + 1) / len(image_files) * 100)
                    progress_callback(progress, f"处理中: {idx + 1}/{len(image_files)}")
                    
            except Exception as e:
                print(f"处理图像失败 {img_path}: {e}")
        
        return total_processed, len(image_files)
    
    def augment_image(self, image, num_augmentations=5):
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
