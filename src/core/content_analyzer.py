"""
内容分析器模块

负责分析图片内容，生成文字描述，识别风格和布局。
"""

import torch
from transformers import CLIPProcessor, CLIPModel, AutoProcessor, AutoModel
from PIL import Image
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """内容分析器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化内容分析器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 初始化模型
        self._init_models()
        
        # 预定义风格和布局模板
        self._init_templates()
        
        logger.info(f"内容分析器初始化完成，使用设备: {self.device}")
    
    def _init_models(self):
        """初始化模型"""
        try:
            # CLIP模型用于图文匹配和描述生成
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.eval()
            self.clip_model.to(self.device)
            
            # BLIP模型用于图片描述生成
            try:
                from transformers import BlipProcessor, BlipForConditionalGeneration
                self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.blip_model.eval()
                self.blip_model.to(self.device)
            except Exception as e:
                logger.warning(f"BLIP模型加载失败: {e}")
                self.blip_processor = None
                self.blip_model = None
            
            logger.info("所有模型初始化完成")
            
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            raise
    
    def _init_templates(self):
        """初始化分析模板"""
        # 风格模板
        self.style_templates = {
            'realistic': ['realistic', 'photorealistic', 'natural', 'detailed'],
            'cartoon': ['cartoon', 'animated', 'illustrated', 'drawn'],
            'abstract': ['abstract', 'artistic', 'modern', 'creative'],
            'vintage': ['vintage', 'retro', 'classic', 'old-fashioned'],
            'minimalist': ['minimalist', 'simple', 'clean', 'minimal'],
            'dramatic': ['dramatic', 'intense', 'contrasting', 'bold'],
            'soft': ['soft', 'gentle', 'muted', 'pastel'],
            'bright': ['bright', 'vibrant', 'colorful', 'lively']
        }
        
        # 布局模板
        self.layout_templates = {
            'center': ['centered', 'center composition', 'main subject in center'],
            'rule_of_thirds': ['rule of thirds', 'off-center', 'balanced composition'],
            'symmetrical': ['symmetrical', 'balanced', 'mirror image'],
            'asymmetrical': ['asymmetrical', 'unbalanced', 'dynamic composition'],
            'close_up': ['close up', 'detailed view', 'macro'],
            'wide_shot': ['wide shot', 'landscape', 'panoramic'],
            'portrait': ['portrait orientation', 'vertical composition'],
            'landscape': ['landscape orientation', 'horizontal composition']
        }
        
        # 内容模板
        self.content_templates = {
            'people': ['person', 'people', 'human', 'face', 'portrait'],
            'nature': ['nature', 'landscape', 'tree', 'flower', 'sky'],
            'urban': ['city', 'building', 'street', 'urban', 'architecture'],
            'animal': ['animal', 'pet', 'wildlife', 'bird', 'cat', 'dog'],
            'object': ['object', 'item', 'thing', 'product'],
            'text': ['text', 'words', 'letters', 'sign', 'label'],
            'abstract': ['abstract', 'pattern', 'texture', 'design']
        }
    
    def generate_image_description(self, image: Union[np.ndarray, Image.Image]) -> str:
        """
        生成图片描述
        
        Args:
            image: 输入图片
            
        Returns:
            图片描述文字
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # 使用BLIP模型生成描述
            if self.blip_model is not None:
                try:
                    inputs = self.blip_processor(images=image, return_tensors="pt")
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.blip_model.generate(**inputs, max_length=50, num_beams=5)
                        description = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
                    
                    logger.debug(f"BLIP生成描述: {description}")
                    return description
                    
                except Exception as e:
                    logger.warning(f"BLIP描述生成失败: {e}")
            
            # 回退到CLIP模板匹配
            description = self._generate_clip_description(image)
            return description
            
        except Exception as e:
            logger.error(f"图片描述生成失败: {e}")
            return "无法生成图片描述"
    
    def _generate_clip_description(self, image: Image.Image) -> str:
        """使用CLIP生成描述"""
        try:
            # 预定义的描述模板
            templates = [
                "a photo of {}",
                "an image showing {}",
                "a picture of {}",
                "this is {}",
                "the image contains {}"
            ]
            
            # 内容关键词
            content_keywords = [
                "people", "landscape", "city", "nature", "animals", 
                "objects", "text", "abstract patterns", "buildings",
                "trees", "sky", "water", "mountains", "flowers"
            ]
            
            best_score = -1
            best_description = "an image"
            
            for template in templates:
                for keyword in content_keywords:
                    text = template.format(keyword)
                    
                    # 计算图文相似度
                    inputs = self.clip_processor(
                        images=image, 
                        text=text, 
                        return_tensors="pt", 
                        padding=True
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.clip_model(**inputs)
                        logits_per_image = outputs.logits_per_image
                        score = logits_per_image.item()
                        
                        if score > best_score:
                            best_score = score
                            best_description = text
            
            return best_description
            
        except Exception as e:
            logger.error(f"CLIP描述生成失败: {e}")
            return "an image"
    
    def analyze_style(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, float]:
        """
        分析图片风格
        
        Args:
            image: 输入图片
            
        Returns:
            风格分析结果
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            style_scores = {}
            
            for style_name, style_keywords in self.style_templates.items():
                # 计算该风格的得分
                style_score = self._calculate_style_score(image, style_keywords)
                style_scores[style_name] = style_score
            
            # 归一化得分
            max_score = max(style_scores.values()) if style_scores.values() else 1.0
            if max_score > 0:
                style_scores = {k: v / max_score for k, v in style_scores.items()}
            
            # 找出主要风格
            dominant_style = max(style_scores.items(), key=lambda x: x[1])
            
            result = {
                'style_scores': style_scores,
                'dominant_style': dominant_style[0],
                'dominant_score': dominant_style[1]
            }
            
            logger.info(f"风格分析完成，主要风格: {dominant_style[0]} (得分: {dominant_style[1]:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"风格分析失败: {e}")
            raise
    
    def _calculate_style_score(self, image: Image.Image, style_keywords: List[str]) -> float:
        """计算风格得分"""
        try:
            total_score = 0.0
            
            for keyword in style_keywords:
                # 使用CLIP计算图片与风格关键词的相似度
                inputs = self.clip_processor(
                    images=image,
                    text=f"a {keyword} image",
                    return_tensors="pt",
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.clip_model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    score = logits_per_image.item()
                    total_score += score
            
            return total_score / len(style_keywords)
            
        except Exception as e:
            logger.error(f"风格得分计算失败: {e}")
            return 0.0
    
    def analyze_layout(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, Any]:
        """
        分析图片布局
        
        Args:
            image: 输入图片
            
        Returns:
            布局分析结果
        """
        try:
            if isinstance(image, np.ndarray):
                image = np.array(image)
            else:
                image = np.array(image)
            
            layout_analysis = {}
            
            # 分析构图
            composition = self._analyze_composition(image)
            layout_analysis['composition'] = composition
            
            # 分析对称性
            symmetry = self._analyze_symmetry(image)
            layout_analysis['symmetry'] = symmetry
            
            # 分析主体位置
            subject_position = self._analyze_subject_position(image)
            layout_analysis['subject_position'] = subject_position
            
            # 分析深度
            depth = self._analyze_depth(image)
            layout_analysis['depth'] = depth
            
            # 综合布局类型
            layout_type = self._determine_layout_type(layout_analysis)
            layout_analysis['layout_type'] = layout_type
            
            logger.info(f"布局分析完成，布局类型: {layout_type}")
            return layout_analysis
            
        except Exception as e:
            logger.error(f"布局分析失败: {e}")
            raise
    
    def _analyze_composition(self, image: np.ndarray) -> Dict[str, float]:
        """分析构图"""
        try:
            height, width = image.shape[:2]
            
            # 计算黄金分割点
            golden_ratio = 1.618
            golden_x = int(width / golden_ratio)
            golden_y = int(height / golden_ratio)
            
            # 计算三分点
            third_x = width // 3
            third_y = height // 3
            
            # 分析边缘密度
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # 计算不同区域的边缘密度
            center_region = edges[third_y:2*third_y, third_x:2*third_x]
            edge_density_center = np.sum(center_region > 0) / center_region.size
            
            # 计算整体边缘密度
            edge_density_total = np.sum(edges > 0) / edges.size
            
            composition_score = edge_density_center / edge_density_total if edge_density_total > 0 else 0.5
            
            return {
                'golden_ratio_x': golden_x,
                'golden_ratio_y': golden_y,
                'third_x': third_x,
                'third_y': third_y,
                'center_density': edge_density_center,
                'total_density': edge_density_total,
                'composition_score': composition_score
            }
            
        except Exception as e:
            logger.error(f"构图分析失败: {e}")
            return {}
    
    def _analyze_symmetry(self, image: np.ndarray) -> Dict[str, float]:
        """分析对称性"""
        try:
            height, width = image.shape[:2]
            
            # 水平对称性
            mid_height = height // 2
            top_half = image[:mid_height, :]
            bottom_half = image[mid_height:, :]
            bottom_half_flipped = np.flipud(bottom_half)
            
            # 确保两个半部分大小相同
            min_height = min(top_half.shape[0], bottom_half_flipped.shape[0])
            top_half = top_half[:min_height, :]
            bottom_half_flipped = bottom_half_flipped[:min_height, :]
            
            horizontal_symmetry = 1.0 - np.mean(np.abs(top_half.astype(float) - bottom_half_flipped.astype(float))) / 255.0
            
            # 垂直对称性
            mid_width = width // 2
            left_half = image[:, :mid_width]
            right_half = image[:, mid_width:]
            right_half_flipped = np.fliplr(right_half)
            
            # 确保两个半部分大小相同
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
            
            vertical_symmetry = 1.0 - np.mean(np.abs(left_half.astype(float) - right_half_flipped.astype(float))) / 255.0
            
            return {
                'horizontal_symmetry': horizontal_symmetry,
                'vertical_symmetry': vertical_symmetry,
                'overall_symmetry': (horizontal_symmetry + vertical_symmetry) / 2
            }
            
        except Exception as e:
            logger.error(f"对称性分析失败: {e}")
            return {}
    
    def _analyze_subject_position(self, image: np.ndarray) -> Dict[str, Any]:
        """分析主体位置"""
        try:
            height, width = image.shape[:2]
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 使用边缘检测找到主要物体
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 找到最大的轮廓作为主体
                largest_contour = max(contours, key=cv2.contourArea)
                
                # 计算质心
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                else:
                    cx, cy = width // 2, height // 2
                
                # 计算相对位置
                relative_x = cx / width
                relative_y = cy / height
                
                # 判断位置类型
                if relative_x < 0.33:
                    x_position = "left"
                elif relative_x < 0.67:
                    x_position = "center"
                else:
                    x_position = "right"
                
                if relative_y < 0.33:
                    y_position = "top"
                elif relative_y < 0.67:
                    y_position = "center"
                else:
                    y_position = "bottom"
                
                return {
                    'center_x': cx,
                    'center_y': cy,
                    'relative_x': relative_x,
                    'relative_y': relative_y,
                    'x_position': x_position,
                    'y_position': y_position,
                    'position': f"{x_position}-{y_position}"
                }
            else:
                return {
                    'center_x': width // 2,
                    'center_y': height // 2,
                    'relative_x': 0.5,
                    'relative_y': 0.5,
                    'x_position': "center",
                    'y_position': "center",
                    'position': "center-center"
                }
                
        except Exception as e:
            logger.error(f"主体位置分析失败: {e}")
            return {}
    
    def _analyze_depth(self, image: np.ndarray) -> Dict[str, float]:
        """分析深度感"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 计算梯度
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # 计算梯度幅值
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # 计算深度指标
            depth_score = np.mean(gradient_magnitude) / 255.0
            
            return {
                'depth_score': depth_score,
                'gradient_mean': np.mean(gradient_magnitude),
                'gradient_std': np.std(gradient_magnitude)
            }
            
        except Exception as e:
            logger.error(f"深度分析失败: {e}")
            return {}
    
    def _determine_layout_type(self, layout_analysis: Dict[str, Any]) -> str:
        """确定布局类型"""
        try:
            composition = layout_analysis.get('composition', {})
            symmetry = layout_analysis.get('symmetry', {})
            subject_position = layout_analysis.get('subject_position', {})
            
            # 基于分析结果确定布局类型
            if symmetry.get('overall_symmetry', 0) > 0.7:
                return "symmetrical"
            elif subject_position.get('position', '') == 'center-center':
                return "center"
            elif composition.get('composition_score', 0) > 0.6:
                return "rule_of_thirds"
            else:
                return "asymmetrical"
                
        except Exception as e:
            logger.error(f"布局类型确定失败: {e}")
            return "unknown"
    
    def analyze_content(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, Any]:
        """
        分析图片内容
        
        Args:
            image: 输入图片
            
        Returns:
            内容分析结果
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            content_analysis = {}
            
            # 生成描述
            description = self.generate_image_description(image)
            content_analysis['description'] = description
            
            # 分析风格
            style_result = self.analyze_style(image)
            content_analysis['style'] = style_result
            
            # 分析布局
            layout_result = self.analyze_layout(image)
            content_analysis['layout'] = layout_result
            
            # 内容分类
            content_categories = self._classify_content(image)
            content_analysis['categories'] = content_categories
            
            # 情感分析
            emotion = self._analyze_emotion(image)
            content_analysis['emotion'] = emotion
            
            logger.info(f"内容分析完成，描述: {description[:50]}...")
            return content_analysis
            
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            raise
    
    def _classify_content(self, image: Image.Image) -> Dict[str, float]:
        """内容分类"""
        try:
            category_scores = {}
            
            for category_name, category_keywords in self.content_templates.items():
                # 计算该分类的得分
                category_score = self._calculate_category_score(image, category_keywords)
                category_scores[category_name] = category_score
            
            # 归一化得分
            max_score = max(category_scores.values()) if category_scores.values() else 1.0
            if max_score > 0:
                category_scores = {k: v / max_score for k, v in category_scores.items()}
            
            return category_scores
            
        except Exception as e:
            logger.error(f"内容分类失败: {e}")
            return {}
    
    def _calculate_category_score(self, image: Image.Image, category_keywords: List[str]) -> float:
        """计算分类得分"""
        try:
            total_score = 0.0
            
            for keyword in category_keywords:
                # 使用CLIP计算图片与分类关键词的相似度
                inputs = self.clip_processor(
                    images=image,
                    text=f"a photo of {keyword}",
                    return_tensors="pt",
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.clip_model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    score = logits_per_image.item()
                    total_score += score
            
            return total_score / len(category_keywords)
            
        except Exception as e:
            logger.error(f"分类得分计算失败: {e}")
            return 0.0
    
    def _analyze_emotion(self, image: Image.Image) -> Dict[str, float]:
        """情感分析"""
        try:
            # 简化的情感分析，基于颜色和亮度
            img_array = np.array(image)
            
            # 计算平均亮度
            if len(img_array.shape) == 3:
                brightness = np.mean(img_array)
            else:
                brightness = np.mean(img_array)
            
            # 计算颜色饱和度
            if len(img_array.shape) == 3:
                hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
                saturation = np.mean(hsv[:, :, 1])
            else:
                saturation = 0
            
            # 基于亮度和饱和度推断情感
            if brightness > 150:
                emotion = "bright"
                emotion_score = 0.8
            elif brightness < 100:
                emotion = "dark"
                emotion_score = 0.7
            else:
                emotion = "neutral"
                emotion_score = 0.5
            
            return {
                'emotion': emotion,
                'emotion_score': emotion_score,
                'brightness': brightness,
                'saturation': saturation
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {}
    
    def generate_structured_description(self, image: Union[np.ndarray, Image.Image]) -> str:
        """
        生成结构化描述
        
        Args:
            image: 输入图片
            
        Returns:
            结构化描述
        """
        try:
            content_analysis = self.analyze_content(image)
            
            # 构建结构化描述
            description_parts = []
            
            # 基本描述
            if 'description' in content_analysis:
                description_parts.append(content_analysis['description'])
            
            # 风格描述
            if 'style' in content_analysis and 'dominant_style' in content_analysis['style']:
                style = content_analysis['style']['dominant_style']
                description_parts.append(f"The image has a {style} style.")
            
            # 布局描述
            if 'layout' in content_analysis and 'layout_type' in content_analysis['layout']:
                layout_type = content_analysis['layout']['layout_type']
                description_parts.append(f"The composition is {layout_type}.")
            
            # 主体位置描述
            if 'layout' in content_analysis and 'subject_position' in content_analysis['layout']:
                position = content_analysis['layout']['subject_position'].get('position', '')
                if position and position != 'center-center':
                    description_parts.append(f"The main subject is positioned in the {position}.")
            
            # 内容分类描述
            if 'categories' in content_analysis:
                categories = content_analysis['categories']
                top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_categories:
                    category_names = [cat[0] for cat in top_categories if cat[1] > 0.3]
                    if category_names:
                        description_parts.append(f"The image contains {', '.join(category_names)}.")
            
            # 情感描述
            if 'emotion' in content_analysis and 'emotion' in content_analysis['emotion']:
                emotion = content_analysis['emotion']['emotion']
                if emotion != 'neutral':
                    description_parts.append(f"The image has a {emotion} mood.")
            
            # 组合所有描述
            structured_description = " ".join(description_parts)
            
            logger.info(f"结构化描述生成完成: {structured_description[:100]}...")
            return structured_description
            
        except Exception as e:
            logger.error(f"结构化描述生成失败: {e}")
            return "无法生成结构化描述" 