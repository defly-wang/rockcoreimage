import os
import cv2
import numpy as np
from PIL import Image
from PyQt6.QtCore import QObject, pyqtSignal


class DataCleaner(QObject):
    progress_updated = pyqtSignal(int, str)
    cleaning_finished = pyqtSignal(list, list, list)
    
    def __init__(self):
        super().__init__()
        self.blur_threshold = 100
        self.size_threshold = 1024
    
    def check_blur(self, image_path):
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return True, "无法读取图像"
            
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            return laplacian_var < self.blur_threshold, laplacian_var
        except Exception as e:
            return True, 0
    
    def check_corrupted(self, image_path):
        try:
            img = Image.open(image_path)
            img.verify()
            return False
        except Exception:
            return True
    
    def check_size(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return True
            height, width = img.shape[:2]
            return height < 64 or width < 64
        except Exception:
            return True
    
    def clean_dataset(self, image_paths, progress_callback=None):
        blurry_images = []
        corrupted_images = []
        small_images = []
        
        total = len(image_paths)
        
        for i, path in enumerate(image_paths):
            if progress_callback:
                progress_callback(int((i + 1) / total * 100), f"正在检查: {os.path.basename(path)}")
            
            is_blur, blur_value = self.check_blur(path)
            if is_blur:
                blurry_images.append((path, blur_value))
            
            if self.check_corrupted(path):
                corrupted_images.append(path)
            
            if self.check_size(path):
                small_images.append(path)
        
        return blurry_images, corrupted_images, small_images
    
    def detect_duplicates(self, image_paths, threshold=0.95):
        duplicates = []
        hashes = {}
        
        for i, path in enumerate(image_paths):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            
            resized = cv2.resize(img, (64, 64))
            img_hash = hash(resized.tobytes())
            
            for existing_hash, existing_path in hashes.items():
                similarity = self._calculate_similarity(resized, hashes[existing_hash])
                if similarity > threshold:
                    duplicates.append((existing_path, path, similarity))
            
            hashes[img_hash] = resized
        
        return duplicates
    
    def _calculate_similarity(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        diff = cv2.absdiff(img1, img2)
        return 1.0 - (np.mean(diff) / 255.0)
