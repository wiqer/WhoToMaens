"""
特征提取器模块

负责从图片中提取多种类型的特征，包括视觉特征、风格特征、布局特征等。
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from transformers import CLIPProcessor, CLIPModel, AutoProcessor, AutoModel
import numpy as np
import cv2
from PIL import Image
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """特征提取器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化特征提取器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 初始化模型
        self._init_models()
        
        # 初始化预处理器
        self._init_preprocessors()
        
        logger.info(f"特征提取器初始化完成，使用设备: {self.device}")
    
    def _init_models(self):
        """初始化各种模型"""
        try:
            # ResNet模型
            self.resnet = models.resnet50(pretrained=True)
            self.resnet.eval()
            self.resnet.to(self.device)
            
            # VGG模型（用于风格特征）
            self.vgg = models.vgg19(pretrained=True)
            self.vgg.eval()
            self.vgg.to(self.device)
            
            # CLIP模型
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.eval()
            self.clip_model.to(self.device)
            
            # ImageBERT模型
            try:
                self.imagebert_model = AutoModel.from_pretrained("microsoft/imagebert-base")
                self.imagebert_processor = AutoProcessor.from_pretrained("microsoft/imagebert-base")
                self.imagebert_model.eval()
                self.imagebert_model.to(self.device)
            except Exception as e:
                logger.warning(f"ImageBERT模型加载失败: {e}")
                self.imagebert_model = None
                self.imagebert_processor = None
            
            logger.info("所有模型初始化完成")
            
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            raise
    
    def _init_preprocessors(self):
        """初始化预处理器"""
        # ResNet预处理器
        self.resnet_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # VGG预处理器
        self.vgg_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def extract_visual_features(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, np.ndarray]:
        """
        提取视觉特征
        
        Args:
            image: 输入图片
            
        Returns:
            视觉特征字典
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            features = {}
            
            # ResNet特征
            resnet_features = self._extract_resnet_features(image)
            features['resnet'] = resnet_features
            
            # VGG特征
            vgg_features = self._extract_vgg_features(image)
            features['vgg'] = vgg_features
            
            # CLIP特征
            clip_features = self._extract_clip_features(image)
            features['clip'] = clip_features
            
            # ImageBERT特征
            if self.imagebert_model is not None:
                imagebert_features = self._extract_imagebert_features(image)
                features['imagebert'] = imagebert_features
            
            logger.debug(f"视觉特征提取完成，特征维度: {[f'{k}: {v.shape}' for k, v in features.items()]}")
            return features
            
        except Exception as e:
            logger.error(f"视觉特征提取失败: {e}")
            raise
    
    def _extract_resnet_features(self, image: Image.Image) -> np.ndarray:
        """提取ResNet特征"""
        try:
            # 预处理
            input_tensor = self.resnet_transform(image).unsqueeze(0).to(self.device)
            
            # 提取特征（去掉最后的分类层）
            with torch.no_grad():
                features = self.resnet.forward(input_tensor)
                # 使用全局平均池化
                features = torch.nn.functional.adaptive_avg_pool2d(features, (1, 1))
                features = features.view(features.size(0), -1)
            
            return features.cpu().numpy()
            
        except Exception as e:
            logger.error(f"ResNet特征提取失败: {e}")
            raise
    
    def _extract_vgg_features(self, image: Image.Image) -> np.ndarray:
        """提取VGG特征"""
        try:
            # 预处理
            input_tensor = self.vgg_transform(image).unsqueeze(0).to(self.device)
            
            # 提取特征（使用VGG的中间层）
            with torch.no_grad():
                x = input_tensor
                features = []
                
                # 提取多个层的特征
                for i, layer in enumerate(self.vgg.features):
                    x = layer(x)
                    if isinstance(layer, nn.ReLU):
                        features.append(x)
                
                # 使用最后一个特征图
                final_features = torch.nn.functional.adaptive_avg_pool2d(features[-1], (1, 1))
                final_features = final_features.view(final_features.size(0), -1)
            
            return final_features.cpu().numpy()
            
        except Exception as e:
            logger.error(f"VGG特征提取失败: {e}")
            raise
    
    def _extract_clip_features(self, image: Image.Image) -> np.ndarray:
        """提取CLIP特征"""
        try:
            # 预处理
            inputs = self.clip_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 提取特征
            with torch.no_grad():
                outputs = self.clip_model.get_image_features(**inputs)
            
            return outputs.cpu().numpy()
            
        except Exception as e:
            logger.error(f"CLIP特征提取失败: {e}")
            raise
    
    def _extract_imagebert_features(self, image: Image.Image) -> np.ndarray:
        """提取ImageBERT特征"""
        try:
            # 预处理
            inputs = self.imagebert_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 提取特征
            with torch.no_grad():
                outputs = self.imagebert_model(**inputs)
                # 使用[CLS]标记的特征
                features = outputs.last_hidden_state[:, 0, :]
            
            return features.cpu().numpy()
            
        except Exception as e:
            logger.error(f"ImageBERT特征提取失败: {e}")
            raise
    
    def extract_style_features(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, np.ndarray]:
        """
        提取风格特征
        
        Args:
            image: 输入图片
            
        Returns:
            风格特征字典
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            features = {}
            
            # HSV直方图
            hsv_features = self._extract_hsv_histogram(image)
            features['hsv_histogram'] = hsv_features
            
            # Gabor纹理特征
            gabor_features = self._extract_gabor_features(image)
            features['gabor'] = gabor_features
            
            # 颜色矩
            color_moments = self._extract_color_moments(image)
            features['color_moments'] = color_moments
            
            logger.debug(f"风格特征提取完成，特征维度: {[f'{k}: {v.shape}' for k, v in features.items()]}")
            return features
            
        except Exception as e:
            logger.error(f"风格特征提取失败: {e}")
            raise
    
    def _extract_hsv_histogram(self, image: Image.Image) -> np.ndarray:
        """提取HSV直方图特征"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            
            # 计算直方图
            hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
            
            # 归一化
            hist = cv2.normalize(hist, hist).flatten()
            
            return hist
            
        except Exception as e:
            logger.error(f"HSV直方图提取失败: {e}")
            raise
    
    def _extract_gabor_features(self, image: Image.Image) -> np.ndarray:
        """提取Gabor纹理特征"""
        try:
            # 转换为灰度图
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Gabor滤波器参数
            ksize = 31
            sigma = 4.0
            theta = np.pi/4
            lambda_ = 10.0
            gamma = 0.5
            psi = 0
            
            # 创建Gabor滤波器
            kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambda_, gamma, psi, ktype=cv2.CV_32F)
            
            # 应用滤波器
            filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
            
            # 计算统计特征
            features = [
                np.mean(filtered),
                np.std(filtered),
                np.var(filtered),
                np.max(filtered),
                np.min(filtered)
            ]
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Gabor特征提取失败: {e}")
            raise
    
    def _extract_color_moments(self, image: Image.Image) -> np.ndarray:
        """提取颜色矩特征"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 计算每个通道的矩
            moments = []
            for i in range(3):  # RGB三个通道
                channel = img_array[:, :, i]
                moments.extend([
                    np.mean(channel),
                    np.std(channel),
                    np.var(channel)
                ])
            
            return np.array(moments)
            
        except Exception as e:
            logger.error(f"颜色矩提取失败: {e}")
            raise
    
    def extract_layout_features(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, np.ndarray]:
        """
        提取布局特征
        
        Args:
            image: 输入图片
            
        Returns:
            布局特征字典
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            features = {}
            
            # 边缘密度
            edge_density = self._extract_edge_density(image)
            features['edge_density'] = edge_density
            
            # 对称性特征
            symmetry_features = self._extract_symmetry_features(image)
            features['symmetry'] = symmetry_features
            
            # 空间分布特征
            spatial_features = self._extract_spatial_features(image)
            features['spatial'] = spatial_features
            
            logger.debug(f"布局特征提取完成，特征维度: {[f'{k}: {v.shape}' for k, v in features.items()]}")
            return features
            
        except Exception as e:
            logger.error(f"布局特征提取失败: {e}")
            raise
    
    def _extract_edge_density(self, image: Image.Image) -> np.ndarray:
        """提取边缘密度特征"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 转换为灰度图
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Canny边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 计算边缘密度
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            return np.array([edge_density])
            
        except Exception as e:
            logger.error(f"边缘密度提取失败: {e}")
            raise
    
    def _extract_symmetry_features(self, image: Image.Image) -> np.ndarray:
        """提取对称性特征"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 水平对称性
            height, width = img_array.shape[:2]
            mid_height = height // 2
            
            top_half = img_array[:mid_height, :]
            bottom_half = img_array[mid_height:, :]
            bottom_half_flipped = np.flipud(bottom_half)
            
            # 确保两个半部分大小相同
            min_height = min(top_half.shape[0], bottom_half_flipped.shape[0])
            top_half = top_half[:min_height, :]
            bottom_half_flipped = bottom_half_flipped[:min_height, :]
            
            horizontal_symmetry = np.mean(np.abs(top_half.astype(float) - bottom_half_flipped.astype(float)))
            
            # 垂直对称性
            mid_width = width // 2
            
            left_half = img_array[:, :mid_width]
            right_half = img_array[:, mid_width:]
            right_half_flipped = np.fliplr(right_half)
            
            # 确保两个半部分大小相同
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
            
            vertical_symmetry = np.mean(np.abs(left_half.astype(float) - right_half_flipped.astype(float)))
            
            return np.array([horizontal_symmetry, vertical_symmetry])
            
        except Exception as e:
            logger.error(f"对称性特征提取失败: {e}")
            raise
    
    def _extract_spatial_features(self, image: Image.Image) -> np.ndarray:
        """提取空间分布特征"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 转换为灰度图
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 计算质心
            moments = cv2.moments(gray)
            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
            else:
                cx, cy = gray.shape[1] // 2, gray.shape[0] // 2
            
            # 计算质心相对于图像中心的位置
            center_x, center_y = gray.shape[1] // 2, gray.shape[0] // 2
            relative_x = (cx - center_x) / center_x
            relative_y = (cy - center_y) / center_y
            
            return np.array([relative_x, relative_y])
            
        except Exception as e:
            logger.error(f"空间分布特征提取失败: {e}")
            raise
    
    def extract_all_features(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, np.ndarray]:
        """
        提取所有特征
        
        Args:
            image: 输入图片
            
        Returns:
            所有特征的字典
        """
        try:
            all_features = {}
            
            # 视觉特征
            visual_features = self.extract_visual_features(image)
            all_features.update(visual_features)
            
            # 风格特征
            style_features = self.extract_style_features(image)
            all_features.update(style_features)
            
            # 布局特征
            layout_features = self.extract_layout_features(image)
            all_features.update(layout_features)
            
            logger.info(f"所有特征提取完成，共 {len(all_features)} 种特征")
            return all_features
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            raise 