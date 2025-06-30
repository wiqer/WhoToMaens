"""
多模态模型基类

提供多模态模型的统一接口和基础功能。
"""

import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MultiModalModel(ABC, nn.Module):
    """多模态模型基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化多模态模型
        
        Args:
            config: 配置参数
        """
        super().__init__()
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 模型状态
        self.is_loaded = False
        self.model_path = None
        
        logger.info(f"多模态模型初始化完成，使用设备: {self.device}")
    
    @abstractmethod
    def load_model(self, model_path: Union[str, Path]) -> None:
        """
        加载模型
        
        Args:
            model_path: 模型路径
        """
        pass
    
    @abstractmethod
    def extract_image_features(self, images: Union[torch.Tensor, List[torch.Tensor]]) -> torch.Tensor:
        """
        提取图像特征
        
        Args:
            images: 输入图像
            
        Returns:
            图像特征
        """
        pass
    
    @abstractmethod
    def extract_text_features(self, texts: Union[str, List[str]]) -> torch.Tensor:
        """
        提取文本特征
        
        Args:
            texts: 输入文本
            
        Returns:
            文本特征
        """
        pass
    
    @abstractmethod
    def compute_similarity(self, image_features: torch.Tensor, 
                          text_features: torch.Tensor) -> torch.Tensor:
        """
        计算图文相似度
        
        Args:
            image_features: 图像特征
            text_features: 文本特征
            
        Returns:
            相似度分数
        """
        pass
    
    def save_model(self, save_path: Union[str, Path]) -> None:
        """
        保存模型
        
        Args:
            save_path: 保存路径
        """
        try:
            if isinstance(save_path, str):
                save_path = Path(save_path)
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存模型状态
            torch.save({
                'model_state_dict': self.state_dict(),
                'config': self.config,
                'model_path': self.model_path
            }, save_path)
            
            logger.info(f"模型保存成功: {save_path}")
            
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_path: Union[str, Path]) -> None:
        """
        加载检查点
        
        Args:
            checkpoint_path: 检查点路径
        """
        try:
            if isinstance(checkpoint_path, str):
                checkpoint_path = Path(checkpoint_path)
            
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"检查点文件不存在: {checkpoint_path}")
            
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # 加载模型状态
            self.load_state_dict(checkpoint['model_state_dict'])
            
            # 更新配置
            if 'config' in checkpoint:
                self.config.update(checkpoint['config'])
            
            # 更新模型路径
            if 'model_path' in checkpoint:
                self.model_path = checkpoint['model_path']
            
            self.is_loaded = True
            logger.info(f"检查点加载成功: {checkpoint_path}")
            
        except Exception as e:
            logger.error(f"检查点加载失败: {e}")
            raise
    
    def to_device(self, device: torch.device) -> None:
        """
        将模型移动到指定设备
        
        Args:
            device: 目标设备
        """
        try:
            self.device = device
            super().to(device)
            logger.info(f"模型已移动到设备: {device}")
            
        except Exception as e:
            logger.error(f"模型设备移动失败: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        try:
            info = {
                'model_type': self.__class__.__name__,
                'device': str(self.device),
                'is_loaded': self.is_loaded,
                'model_path': str(self.model_path) if self.model_path else None,
                'config': self.config,
                'parameters': sum(p.numel() for p in self.parameters()),
                'trainable_parameters': sum(p.numel() for p in self.parameters() if p.requires_grad)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取模型信息失败: {e}")
            return {}
    
    def freeze_parameters(self, freeze: bool = True) -> None:
        """
        冻结/解冻模型参数
        
        Args:
            freeze: 是否冻结参数
        """
        try:
            for param in self.parameters():
                param.requires_grad = not freeze
            
            logger.info(f"模型参数已{'冻结' if freeze else '解冻'}")
            
        except Exception as e:
            logger.error(f"参数冻结/解冻失败: {e}")
            raise
    
    def get_feature_dimension(self) -> int:
        """
        获取特征维度
        
        Returns:
            特征维度
        """
        try:
            # 默认实现，子类可以重写
            return self.config.get('feature_dim', 512)
            
        except Exception as e:
            logger.error(f"获取特征维度失败: {e}")
            return 512
    
    def preprocess_image(self, image: torch.Tensor) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image: 输入图像
            
        Returns:
            预处理后的图像
        """
        try:
            # 默认实现，子类可以重写
            if len(image.shape) == 3:
                image = image.unsqueeze(0)
            
            return image.to(self.device)
            
        except Exception as e:
            logger.error(f"图像预处理失败: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        预处理文本
        
        Args:
            text: 输入文本
            
        Returns:
            预处理后的文本
        """
        try:
            # 默认实现，子类可以重写
            return text.strip()
            
        except Exception as e:
            logger.error(f"文本预处理失败: {e}")
            raise
    
    def encode_image_text_pair(self, image: torch.Tensor, text: str) -> Dict[str, torch.Tensor]:
        """
        编码图像-文本对
        
        Args:
            image: 输入图像
            text: 输入文本
            
        Returns:
            编码结果字典
        """
        try:
            # 预处理
            processed_image = self.preprocess_image(image)
            processed_text = self.preprocess_text(text)
            
            # 提取特征
            image_features = self.extract_image_features(processed_image)
            text_features = self.extract_text_features(processed_text)
            
            # 计算相似度
            similarity = self.compute_similarity(image_features, text_features)
            
            return {
                'image_features': image_features,
                'text_features': text_features,
                'similarity': similarity
            }
            
        except Exception as e:
            logger.error(f"图像-文本对编码失败: {e}")
            raise
    
    def batch_encode(self, images: List[torch.Tensor], 
                    texts: List[str]) -> Dict[str, torch.Tensor]:
        """
        批量编码
        
        Args:
            images: 图像列表
            texts: 文本列表
            
        Returns:
            批量编码结果
        """
        try:
            if len(images) != len(texts):
                raise ValueError("图像和文本数量不匹配")
            
            batch_results = []
            
            for image, text in zip(images, texts):
                result = self.encode_image_text_pair(image, text)
                batch_results.append(result)
            
            # 合并结果
            combined_result = {}
            for key in batch_results[0].keys():
                combined_result[key] = torch.stack([r[key] for r in batch_results])
            
            return combined_result
            
        except Exception as e:
            logger.error(f"批量编码失败: {e}")
            raise
    
    def forward(self, images: torch.Tensor, texts: List[str]) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            images: 输入图像
            texts: 输入文本列表
            
        Returns:
            前向传播结果
        """
        try:
            if len(texts) == 1:
                # 单个文本
                return self.encode_image_text_pair(images, texts[0])
            else:
                # 多个文本
                return self.batch_encode([images], texts)
                
        except Exception as e:
            logger.error(f"前向传播失败: {e}")
            raise 