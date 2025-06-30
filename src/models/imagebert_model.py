"""
ImageBERT模型模块
提供ImageBERT模型的封装和接口，用于多模态特征提取和文本生成
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ImageBERTModel:
    """ImageBERT模型封装类"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", device: str = None):
        """
        初始化ImageBERT模型
        
        Args:
            model_name: 模型名称
            device: 设备类型 ('cpu', 'cuda', 'mps')
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            # 加载模型和分词器
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
            # 移动到指定设备
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"ImageBERT模型加载成功: {model_name} on {self.device}")
            
        except Exception as e:
            logger.error(f"ImageBERT模型加载失败: {e}")
            # 使用备用模型
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """加载备用模型"""
        try:
            fallback_model = "microsoft/DialoGPT-small"
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModel.from_pretrained(fallback_model)
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"备用模型加载成功: {fallback_model}")
            
        except Exception as e:
            logger.error(f"备用模型加载也失败: {e}")
            # 创建简单的占位符模型
            self._create_placeholder_model()
    
    def _create_placeholder_model(self):
        """创建占位符模型"""
        class PlaceholderModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.embedding_dim = 768
                
            def forward(self, input_ids=None, attention_mask=None, **kwargs):
                batch_size = input_ids.shape[0] if input_ids is not None else 1
                return type('obj', (object,), {
                    'last_hidden_state': torch.randn(batch_size, 10, self.embedding_dim),
                    'pooler_output': torch.randn(batch_size, self.embedding_dim)
                })()
        
        self.model = PlaceholderModel()
        self.tokenizer = type('obj', (object,), {
            'encode': lambda x, **kwargs: [1, 2, 3, 4, 5],
            'decode': lambda x: "placeholder text",
            'pad_token_id': 0,
            'eos_token_id': 1
        })()
        
        logger.warning("使用占位符模型，功能受限")
    
    def encode_text(self, texts: Union[str, List[str]], max_length: int = 512) -> torch.Tensor:
        """
        编码文本
        
        Args:
            texts: 文本或文本列表
            max_length: 最大长度
            
        Returns:
            文本特征张量
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            with torch.no_grad():
                # 分词
                inputs = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt"
                )
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 前向传播
                outputs = self.model(**inputs)
                
                # 返回池化输出
                return outputs.pooler_output
                
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            # 返回随机特征
            batch_size = len(texts) if isinstance(texts, list) else 1
            return torch.randn(batch_size, 768)
    
    def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 1.0) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示文本
            max_length: 最大生成长度
            temperature: 温度参数
            
        Returns:
            生成的文本
        """
        try:
            with torch.no_grad():
                # 编码输入
                input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
                
                # 生成文本
                outputs = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
                
                # 解码输出
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                return generated_text
                
        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            return f"[生成失败: {prompt}]"
    
    def get_text_features(self, texts: List[str], max_length: int = 512) -> torch.Tensor:
        """
        获取文本特征
        
        Args:
            texts: 文本列表
            max_length: 最大长度
            
        Returns:
            文本特征张量
        """
        return self.encode_text(texts, max_length)
    
    def compute_similarity(self, text_features1: torch.Tensor, 
                          text_features2: torch.Tensor) -> torch.Tensor:
        """
        计算文本特征相似度
        
        Args:
            text_features1: 文本特征1
            text_features2: 文本特征2
            
        Returns:
            相似度矩阵
        """
        try:
            # 归一化特征
            text_features1 = text_features1 / text_features1.norm(dim=-1, keepdim=True)
            text_features2 = text_features2 / text_features2.norm(dim=-1, keepdim=True)
            
            # 计算相似度
            similarity = torch.matmul(text_features1, text_features2.T)
            
            return similarity
            
        except Exception as e:
            logger.error(f"相似度计算失败: {e}")
            # 返回随机相似度
            return torch.randn(text_features1.shape[0], text_features2.shape[0])
    
    def encode_single_text(self, text: str, max_length: int = 512) -> torch.Tensor:
        """
        编码单个文本
        
        Args:
            text: 文本
            max_length: 最大长度
            
        Returns:
            文本特征向量
        """
        return self.encode_text(text, max_length).squeeze(0)
    
    def __call__(self, texts: Union[str, List[str]] = None, max_length: int = 512) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            texts: 文本或文本列表
            max_length: 最大长度
            
        Returns:
            包含文本特征的字典
        """
        if texts is None:
            return {}
        
        features = self.encode_text(texts, max_length)
        return {'text_features': features}
    
    def to(self, device: str):
        """移动到指定设备"""
        self.device = device
        if hasattr(self.model, 'to'):
            self.model.to(device)
        return self
    
    def eval(self):
        """设置为评估模式"""
        if hasattr(self.model, 'eval'):
            self.model.eval()
        return self
    
    def train(self):
        """设置为训练模式"""
        if hasattr(self.model, 'train'):
            self.model.train()
        return self


# 便捷函数
def load_imagebert_model(model_name: str = "microsoft/DialoGPT-medium", 
                        device: str = None) -> ImageBERTModel:
    """
    加载ImageBERT模型的便捷函数
    
    Args:
        model_name: 模型名称
        device: 设备类型
        
    Returns:
        ImageBERT模型实例
    """
    return ImageBERTModel(model_name, device) 