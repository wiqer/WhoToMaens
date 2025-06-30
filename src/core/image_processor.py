"""
图片处理器模块

负责图片的预处理、格式转换、质量优化等基础操作。
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化图片处理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
    def load_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        加载图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片数组
        """
        try:
            if isinstance(image_path, str):
                image_path = Path(image_path)
            
            if not image_path.exists():
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            if image_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"不支持的图片格式: {image_path.suffix}")
            
            # 使用OpenCV加载图片
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"无法加载图片: {image_path}")
            
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            logger.info(f"成功加载图片: {image_path}, 尺寸: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"加载图片失败: {image_path}, 错误: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        预处理图片
        
        Args:
            image: 输入图片
            target_size: 目标尺寸
            
        Returns:
            预处理后的图片
        """
        try:
            # 调整尺寸
            resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
            
            # 归一化
            normalized_image = resized_image.astype(np.float32) / 255.0
            
            # 标准化
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            normalized_image = (normalized_image - mean) / std
            
            logger.debug(f"图片预处理完成, 目标尺寸: {target_size}")
            return normalized_image
            
        except Exception as e:
            logger.error(f"图片预处理失败: {e}")
            raise
    
    def extract_sub_images(self, image: np.ndarray, grid_size: Tuple[int, int] = (3, 3)) -> List[np.ndarray]:
        """
        提取子图片
        
        Args:
            image: 输入图片
            grid_size: 网格大小 (rows, cols)
            
        Returns:
            子图片列表
        """
        try:
            height, width = image.shape[:2]
            sub_height = height // grid_size[0]
            sub_width = width // grid_size[1]
            
            sub_images = []
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    y1 = i * sub_height
                    y2 = (i + 1) * sub_height if i < grid_size[0] - 1 else height
                    x1 = j * sub_width
                    x2 = (j + 1) * sub_width if j < grid_size[1] - 1 else width
                    
                    sub_image = image[y1:y2, x1:x2]
                    sub_images.append(sub_image)
            
            logger.info(f"提取了 {len(sub_images)} 个子图片")
            return sub_images
            
        except Exception as e:
            logger.error(f"提取子图片失败: {e}")
            raise
    
    def enhance_image(self, image: np.ndarray, 
                     brightness: float = 1.0,
                     contrast: float = 1.0,
                     saturation: float = 1.0) -> np.ndarray:
        """
        图片增强
        
        Args:
            image: 输入图片
            brightness: 亮度调整
            contrast: 对比度调整
            saturation: 饱和度调整
            
        Returns:
            增强后的图片
        """
        try:
            # 转换为PIL图片
            pil_image = Image.fromarray(image)
            
            # 亮度调整
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(pil_image)
                pil_image = enhancer.enhance(brightness)
            
            # 对比度调整
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(contrast)
            
            # 饱和度调整
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(pil_image)
                pil_image = enhancer.enhance(saturation)
            
            # 转换回numpy数组
            enhanced_image = np.array(pil_image)
            
            logger.debug(f"图片增强完成: brightness={brightness}, contrast={contrast}, saturation={saturation}")
            return enhanced_image
            
        except Exception as e:
            logger.error(f"图片增强失败: {e}")
            raise
    
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """
        边缘检测
        
        Args:
            image: 输入图片
            
        Returns:
            边缘检测结果
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Canny边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            logger.debug("边缘检测完成")
            return edges
            
        except Exception as e:
            logger.error(f"边缘检测失败: {e}")
            raise
    
    def save_image(self, image: np.ndarray, output_path: Union[str, Path], 
                   quality: int = 95) -> None:
        """
        保存图片
        
        Args:
            image: 图片数组
            output_path: 输出路径
            quality: 图片质量 (1-100)
        """
        try:
            if isinstance(output_path, str):
                output_path = Path(output_path)
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为PIL图片并保存
            pil_image = Image.fromarray(image)
            pil_image.save(output_path, quality=quality, optimize=True)
            
            logger.info(f"图片保存成功: {output_path}")
            
        except Exception as e:
            logger.error(f"保存图片失败: {output_path}, 错误: {e}")
            raise
    
    def get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            image: 图片数组
            
        Returns:
            图片信息字典
        """
        try:
            info = {
                'shape': image.shape,
                'dtype': str(image.dtype),
                'min_value': float(np.min(image)),
                'max_value': float(np.max(image)),
                'mean_value': float(np.mean(image)),
                'std_value': float(np.std(image))
            }
            
            if len(image.shape) == 3:
                info['channels'] = image.shape[2]
                info['height'] = image.shape[0]
                info['width'] = image.shape[1]
            else:
                info['channels'] = 1
                info['height'] = image.shape[0]
                info['width'] = image.shape[1]
            
            return info
            
        except Exception as e:
            logger.error(f"获取图片信息失败: {e}")
            raise 