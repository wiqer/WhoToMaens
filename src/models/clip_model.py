"""
CLIP模型模块
提供CLIP模型的封装和接口，用于多模态特征提取
"""

import torch
import torch.nn as nn
from transformers import CLIPProcessor, CLIPModel as TransformersCLIPModel
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class CLIPModel:
    """CLIP模型封装类"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str = None):
        """
        初始化CLIP模型
        
        Args:
            model_name: CLIP模型名称
            device: 设备类型 ('cpu', 'cuda', 'mps')
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            # 加载模型和处理器
            self.model = TransformersCLIPModel.from_pretrained(model_name)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            
            # 移动到指定设备
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"CLIP模型加载成功: {model_name} on {self.device}")
            
        except Exception as e:
            logger.error(f"CLIP模型加载失败: {e}")
            raise
    
    def get_image_features(self, images: Union[List[str], List[torch.Tensor]], 
                          return_tensors: str = "pt") -> torch.Tensor:
        """
        提取图像特征
        
        Args:
            images: 图像列表（文件路径或张量）
            return_tensors: 返回张量类型
            
        Returns:
            图像特征张量
        """
        try:
            with torch.no_grad():
                # 处理输入
                if isinstance(images[0], str):
                    # 文件路径
                    inputs = self.processor(images=images, return_tensors=return_tensors)
                else:
                    # 张量
                    inputs = {"pixel_values": torch.stack(images)}
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 提取特征
                outputs = self.model.get_image_features(**inputs)
                
                return outputs
                
        except Exception as e:
            logger.error(f"图像特征提取失败: {e}")
            raise
    
    def get_text_features(self, texts: List[str], return_tensors: str = "pt") -> torch.Tensor:
        """
        提取文本特征
        
        Args:
            texts: 文本列表
            return_tensors: 返回张量类型
            
        Returns:
            文本特征张量
        """
        try:
            with torch.no_grad():
                # 处理输入
                inputs = self.processor(text=texts, return_tensors=return_tensors, padding=True)
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 提取特征
                outputs = self.model.get_text_features(**inputs)
                
                return outputs
                
        except Exception as e:
            logger.error(f"文本特征提取失败: {e}")
            raise
    
    def __call__(self, images: Union[List[str], List[torch.Tensor]] = None,
                 texts: List[str] = None, return_tensors: str = "pt") -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            images: 图像列表
            texts: 文本列表
            return_tensors: 返回张量类型
            
        Returns:
            包含图像和文本特征的字典
        """
        outputs = {}
        
        if images is not None:
            outputs['image_features'] = self.get_image_features(images, return_tensors)
        
        if texts is not None:
            outputs['text_features'] = self.get_text_features(texts, return_tensors)
        
        return outputs
    
    def compute_similarity(self, image_features: torch.Tensor, 
                          text_features: torch.Tensor) -> torch.Tensor:
        """
        计算图像和文本特征的相似度
        
        Args:
            image_features: 图像特征
            text_features: 文本特征
            
        Returns:
            相似度矩阵
        """
        try:
            # 归一化特征
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # 计算相似度
            similarity = torch.matmul(image_features, text_features.T)
            
            return similarity
            
        except Exception as e:
            logger.error(f"相似度计算失败: {e}")
            raise
    
    def encode_image(self, image: Union[str, torch.Tensor]) -> torch.Tensor:
        """
        编码单个图像
        
        Args:
            image: 图像（文件路径或张量）
            
        Returns:
            图像特征向量
        """
        return self.get_image_features([image]).squeeze(0)
    
    def encode_text(self, text: str) -> torch.Tensor:
        """
        编码单个文本
        
        Args:
            text: 文本
            
        Returns:
            文本特征向量
        """
        return self.get_text_features([text]).squeeze(0)
    
    def to(self, device: str):
        """移动到指定设备"""
        self.device = device
        self.model.to(device)
        return self
    
    def eval(self):
        """设置为评估模式"""
        self.model.eval()
        return self
    
    def train(self):
        """设置为训练模式"""
        self.model.train()
        return self


# 便捷函数
def load_clip_model(model_name: str = "openai/clip-vit-base-patch32", 
                   device: str = None) -> CLIPModel:
    """
    加载CLIP模型的便捷函数
    
    Args:
        model_name: 模型名称
        device: 设备类型
        
    Returns:
        CLIP模型实例
    """
    return CLIPModel(model_name, device) 