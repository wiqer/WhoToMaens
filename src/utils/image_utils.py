"""
图片工具模块

包含图片处理的辅助工具函数。
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageUtils:
    """图片工具类"""
    
    @staticmethod
    def resize_image(image: Union[np.ndarray, Image.Image], 
                    target_size: Tuple[int, int]) -> Union[np.ndarray, Image.Image]:
        """调整图片尺寸"""
        try:
            if isinstance(image, np.ndarray):
                return cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
            else:
                return image.resize(target_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"图片尺寸调整失败: {e}")
            raise
    
    @staticmethod
    def crop_image(image: Union[np.ndarray, Image.Image],
                  crop_box: Tuple[int, int, int, int]) -> Union[np.ndarray, Image.Image]:
        """
        裁剪图片
        
        Args:
            image: 输入图片
            crop_box: 裁剪框 (x, y, width, height)
            
        Returns:
            裁剪后的图片
        """
        try:
            x, y, width, height = crop_box
            
            if isinstance(image, np.ndarray):
                return image[y:y+height, x:x+width]
            else:
                return image.crop((x, y, x+width, y+height))
                
        except Exception as e:
            logger.error(f"图片裁剪失败: {e}")
            raise
    
    @staticmethod
    def rotate_image(image: Union[np.ndarray, Image.Image],
                    angle: float,
                    expand: bool = True) -> Union[np.ndarray, Image.Image]:
        """
        旋转图片
        
        Args:
            image: 输入图片
            angle: 旋转角度（度）
            expand: 是否扩展画布
            
        Returns:
            旋转后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                height, width = image.shape[:2]
                center = (width // 2, height // 2)
                
                # 计算旋转矩阵
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                
                if expand:
                    # 计算新尺寸
                    cos_val = abs(rotation_matrix[0, 0])
                    sin_val = abs(rotation_matrix[0, 1])
                    new_width = int((height * sin_val) + (width * cos_val))
                    new_height = int((height * cos_val) + (width * sin_val))
                    
                    # 调整旋转矩阵
                    rotation_matrix[0, 2] += (new_width / 2) - center[0]
                    rotation_matrix[1, 2] += (new_height / 2) - center[1]
                    
                    return cv2.warpAffine(image, rotation_matrix, (new_width, new_height))
                else:
                    return cv2.warpAffine(image, rotation_matrix, (width, height))
            
            else:
                # PIL格式
                return image.rotate(angle, expand=expand, resample=Image.Resampling.BICUBIC)
                
        except Exception as e:
            logger.error(f"图片旋转失败: {e}")
            raise
    
    @staticmethod
    def flip_image(image: Union[np.ndarray, Image.Image],
                  direction: str = 'horizontal') -> Union[np.ndarray, Image.Image]:
        """
        翻转图片
        
        Args:
            image: 输入图片
            direction: 翻转方向 ('horizontal', 'vertical', 'both')
            
        Returns:
            翻转后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                if direction == 'horizontal':
                    return cv2.flip(image, 1)
                elif direction == 'vertical':
                    return cv2.flip(image, 0)
                elif direction == 'both':
                    return cv2.flip(image, -1)
                else:
                    raise ValueError(f"不支持的翻转方向: {direction}")
            
            else:
                # PIL格式
                if direction == 'horizontal':
                    return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif direction == 'vertical':
                    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                elif direction == 'both':
                    return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                else:
                    raise ValueError(f"不支持的翻转方向: {direction}")
                    
        except Exception as e:
            logger.error(f"图片翻转失败: {e}")
            raise
    
    @staticmethod
    def adjust_brightness(image: Union[np.ndarray, Image.Image],
                         factor: float) -> Union[np.ndarray, Image.Image]:
        """
        调整亮度
        
        Args:
            image: 输入图片
            factor: 亮度调整因子 (0.0-2.0)
            
        Returns:
            调整后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
                return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
            else:
                # PIL格式
                enhancer = ImageEnhance.Brightness(image)
                return enhancer.enhance(factor)
                
        except Exception as e:
            logger.error(f"亮度调整失败: {e}")
            raise
    
    @staticmethod
    def adjust_contrast(image: Union[np.ndarray, Image.Image],
                       factor: float) -> Union[np.ndarray, Image.Image]:
        """
        调整对比度
        
        Args:
            image: 输入图片
            factor: 对比度调整因子 (0.0-2.0)
            
        Returns:
            调整后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
                lab[:, :, 0] = np.clip(lab[:, :, 0] * factor, 0, 255)
                return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            else:
                # PIL格式
                enhancer = ImageEnhance.Contrast(image)
                return enhancer.enhance(factor)
                
        except Exception as e:
            logger.error(f"对比度调整失败: {e}")
            raise
    
    @staticmethod
    def adjust_saturation(image: Union[np.ndarray, Image.Image],
                         factor: float) -> Union[np.ndarray, Image.Image]:
        """
        调整饱和度
        
        Args:
            image: 输入图片
            factor: 饱和度调整因子 (0.0-2.0)
            
        Returns:
            调整后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
                return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
            else:
                # PIL格式
                enhancer = ImageEnhance.Color(image)
                return enhancer.enhance(factor)
                
        except Exception as e:
            logger.error(f"饱和度调整失败: {e}")
            raise
    
    @staticmethod
    def apply_blur(image: Union[np.ndarray, Image.Image],
                  kernel_size: int = 5) -> Union[np.ndarray, Image.Image]:
        """
        应用模糊效果
        
        Args:
            image: 输入图片
            kernel_size: 核大小
            
        Returns:
            模糊后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
            
            else:
                # PIL格式
                return image.filter(ImageFilter.GaussianBlur(radius=kernel_size/2))
                
        except Exception as e:
            logger.error(f"模糊效果应用失败: {e}")
            raise
    
    @staticmethod
    def apply_sharpen(image: Union[np.ndarray, Image.Image]) -> Union[np.ndarray, Image.Image]:
        """
        应用锐化效果
        
        Args:
            image: 输入图片
            
        Returns:
            锐化后的图片
        """
        try:
            if isinstance(image, np.ndarray):
                # OpenCV格式
                kernel = np.array([[-1, -1, -1],
                                 [-1,  9, -1],
                                 [-1, -1, -1]])
                return cv2.filter2D(image, -1, kernel)
            
            else:
                # PIL格式
                return image.filter(ImageFilter.SHARPEN)
                
        except Exception as e:
            logger.error(f"锐化效果应用失败: {e}")
            raise
    
    @staticmethod
    def convert_color_space(image: np.ndarray,
                           from_space: str,
                           to_space: str) -> np.ndarray:
        """
        转换颜色空间
        
        Args:
            image: 输入图片
            from_space: 源颜色空间
            to_space: 目标颜色空间
            
        Returns:
            转换后的图片
        """
        try:
            color_conversions = {
                ('RGB', 'HSV'): cv2.COLOR_RGB2HSV,
                ('RGB', 'LAB'): cv2.COLOR_RGB2LAB,
                ('RGB', 'GRAY'): cv2.COLOR_RGB2GRAY,
                ('HSV', 'RGB'): cv2.COLOR_HSV2RGB,
                ('LAB', 'RGB'): cv2.COLOR_LAB2RGB,
                ('GRAY', 'RGB'): cv2.COLOR_GRAY2RGB
            }
            
            conversion_key = (from_space.upper(), to_space.upper())
            if conversion_key in color_conversions:
                return cv2.cvtColor(image, color_conversions[conversion_key])
            else:
                raise ValueError(f"不支持的颜色空间转换: {from_space} -> {to_space}")
                
        except Exception as e:
            logger.error(f"颜色空间转换失败: {e}")
            raise
    
    @staticmethod
    def create_thumbnail(image: Union[np.ndarray, Image.Image],
                        max_size: Tuple[int, int]) -> Union[np.ndarray, Image.Image]:
        """
        创建缩略图
        
        Args:
            image: 输入图片
            max_size: 最大尺寸 (width, height)
            
        Returns:
            缩略图
        """
        try:
            return ImageUtils.resize_image(image, max_size)
            
        except Exception as e:
            logger.error(f"缩略图创建失败: {e}")
            raise
    
    @staticmethod
    def get_image_info(image: Union[np.ndarray, Image.Image]) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            if isinstance(image, np.ndarray):
                return {
                    'shape': image.shape,
                    'dtype': str(image.dtype),
                    'height': image.shape[0],
                    'width': image.shape[1],
                    'channels': image.shape[2] if len(image.shape) == 3 else 1
                }
            else:
                return {
                    'size': image.size,
                    'mode': image.mode,
                    'width': image.width,
                    'height': image.height
                }
        except Exception as e:
            logger.error(f"图片信息获取失败: {e}")
            raise
    
    @staticmethod
    def is_valid_image(image: Union[np.ndarray, Image.Image]) -> bool:
        """
        检查是否为有效图片
        
        Args:
            image: 输入图片
            
        Returns:
            是否为有效图片
        """
        try:
            if isinstance(image, np.ndarray):
                return (len(image.shape) in [2, 3] and 
                       image.size > 0 and 
                       not np.any(np.isnan(image)) and
                       not np.any(np.isinf(image)))
            else:
                return (image is not None and 
                       hasattr(image, 'size') and 
                       image.size[0] > 0 and 
                       image.size[1] > 0)
                
        except Exception:
            return False 