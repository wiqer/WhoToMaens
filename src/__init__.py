"""
WhoToMaens - 多功能融合图片BERT分析系统

一个基于多模态深度学习的图片特征提取、聚类分析和内容识别系统。
支持非文字图片的风格、布局、热点元素等多维度分析。
"""

__version__ = "1.0.0"
__author__ = "WhoToMaens Team"
__description__ = "多功能融合图片BERT分析系统"

from .core import ImageProcessor, FeatureExtractor, ClusterAnalyzer
from .models import MultiModalModel, CLIPModel, ImageBERTModel
from .api import FastAPIApp
from .utils import ImageUtils, VisualizationUtils

__all__ = [
    "ImageProcessor",
    "FeatureExtractor", 
    "ClusterAnalyzer",
    "MultiModalModel",
    "CLIPModel",
    "ImageBERTModel",
    "FastAPIApp",
    "ImageUtils",
    "VisualizationUtils"
] 