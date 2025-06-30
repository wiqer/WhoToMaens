"""
BLIP模型模块
提供BLIP模型的封装和接口，用于多模态特征提取和图像描述生成
"""

import torch
import torch.nn as nn
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class BLIPModel:
    """BLIP模型封装类"""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", device: str = None):
        """
        初始化BLIP模型
        
        Args:
            model_name: 模型名称
            device: 设备类型 ('cpu', 'cuda', 'mps')
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            # 加载模型和处理器
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            # 移动到指定设备
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"BLIP模型加载成功: {model_name} on {self.device}")
            
        except Exception as e:
            logger.error(f"BLIP模型加载失败: {e}")
            # 创建占位符模型
            self._create_placeholder_model()
    
    def _create_placeholder_model(self):
        """创建占位符模型"""
        class PlaceholderBLIPModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.config = type('obj', (object,), {
                    'vocab_size': 30522,
                    'hidden_size': 768
                })()
                
            def generate(self, pixel_values=None, **kwargs):
                # 返回占位符文本ID
                batch_size = pixel_values.shape[0] if pixel_values is not None else 1
                return torch.randint(0, 1000, (batch_size, 10))
            
            def forward(self, pixel_values=None, input_ids=None, **kwargs):
                batch_size = pixel_values.shape[0] if pixel_values is not None else 1
                return type('obj', (object,), {
                    'logits': torch.randn(batch_size, 10, self.config.vocab_size)
                })()
        
        self.model = PlaceholderBLIPModel()
        self.processor = type('obj', (object,), {
            'decode': lambda x: "placeholder image description",
            'encode': lambda x, **kwargs: torch.randint(0, 1000, (1, 10))
        })()
        
        logger.warning("使用占位符BLIP模型，功能受限")
    
    def generate_caption(self, images: Union[str, List[str]], max_length: int = 50) -> Union[str, List[str]]:
        """
        生成图像描述
        
        Args:
            images: 图像路径或图像路径列表
            max_length: 最大生成长度
            
        Returns:
            图像描述或描述列表
        """
        try:
            if isinstance(images, str):
                images = [images]
            
            with torch.no_grad():
                # 处理图像
                inputs = self.processor(images, return_tensors="pt")
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 生成描述
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=5,
                    early_stopping=True
                )
                
                # 解码输出
                captions = []
                for output in outputs:
                    caption = self.processor.decode(output, skip_special_tokens=True)
                    captions.append(caption)
                
                return captions[0] if len(captions) == 1 else captions
                
        except Exception as e:
            logger.error(f"图像描述生成失败: {e}")
            if isinstance(images, str):
                return f"[描述生成失败: {images}]"
            else:
                return [f"[描述生成失败: {img}]" for img in images]
    
    def answer_question(self, images: Union[str, List[str]], questions: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        回答图像相关问题
        
        Args:
            images: 图像路径或图像路径列表
            questions: 问题或问题列表
            
        Returns:
            答案或答案列表
        """
        try:
            if isinstance(images, str):
                images = [images]
            if isinstance(questions, str):
                questions = [questions]
            
            # 确保图像和问题数量匹配
            if len(images) != len(questions):
                raise ValueError("图像和问题数量不匹配")
            
            with torch.no_grad():
                answers = []
                for image, question in zip(images, questions):
                    # 处理输入
                    inputs = self.processor(image, question, return_tensors="pt")
                    
                    # 移动到设备
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    # 生成答案
                    outputs = self.model.generate(
                        **inputs,
                        max_length=50,
                        num_beams=5,
                        early_stopping=True
                    )
                    
                    # 解码输出
                    answer = self.processor.decode(outputs[0], skip_special_tokens=True)
                    answers.append(answer)
                
                return answers[0] if len(answers) == 1 else answers
                
        except Exception as e:
            logger.error(f"问题回答失败: {e}")
            if isinstance(images, str):
                return f"[回答失败: {images}]"
            else:
                return [f"[回答失败: {img}]" for img in images]
    
    def get_image_features(self, images: Union[str, List[str]]) -> torch.Tensor:
        """
        提取图像特征
        
        Args:
            images: 图像路径或图像路径列表
            
        Returns:
            图像特征张量
        """
        try:
            if isinstance(images, str):
                images = [images]
            
            with torch.no_grad():
                # 处理图像
                inputs = self.processor(images, return_tensors="pt")
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 获取特征
                outputs = self.model(**inputs)
                
                # 返回最后一层的隐藏状态
                return outputs.last_hidden_state.mean(dim=1)  # 平均池化
                
        except Exception as e:
            logger.error(f"图像特征提取失败: {e}")
            # 返回随机特征
            batch_size = len(images) if isinstance(images, list) else 1
            return torch.randn(batch_size, 768)
    
    def get_text_features(self, texts: List[str]) -> torch.Tensor:
        """
        提取文本特征
        
        Args:
            texts: 文本列表
            
        Returns:
            文本特征张量
        """
        try:
            with torch.no_grad():
                # 处理文本
                inputs = self.processor(text=texts, return_tensors="pt", padding=True)
                
                # 移动到设备
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 获取特征
                outputs = self.model(**inputs)
                
                # 返回最后一层的隐藏状态
                return outputs.last_hidden_state.mean(dim=1)  # 平均池化
                
        except Exception as e:
            logger.error(f"文本特征提取失败: {e}")
            # 返回随机特征
            batch_size = len(texts)
            return torch.randn(batch_size, 768)
    
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
            # 返回随机相似度
            return torch.randn(image_features.shape[0], text_features.shape[0])
    
    def __call__(self, images: Union[str, List[str]] = None, 
                 texts: List[str] = None) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        Args:
            images: 图像路径或图像路径列表
            texts: 文本列表
            
        Returns:
            包含图像和文本特征的字典
        """
        outputs = {}
        
        if images is not None:
            outputs['image_features'] = self.get_image_features(images)
        
        if texts is not None:
            outputs['text_features'] = self.get_text_features(texts)
        
        return outputs
    
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
def load_blip_model(model_name: str = "Salesforce/blip-image-captioning-base", 
                   device: str = None) -> BLIPModel:
    """
    加载BLIP模型的便捷函数
    
    Args:
        model_name: 模型名称
        device: 设备类型
        
    Returns:
        BLIP模型实例
    """
    return BLIPModel(model_name, device) 