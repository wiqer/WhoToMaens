"""
热点检测器模块

负责检测图片中的热点区域和关键元素。
"""

import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HotspotDetector:
    """热点检测器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化热点检测器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 初始化目标检测模型
        self._init_detection_models()
        
        logger.info(f"热点检测器初始化完成，使用设备: {self.device}")
    
    def _init_detection_models(self):
        """初始化检测模型"""
        try:
            # 这里可以加载预训练的目标检测模型
            # 例如YOLOv8、Faster R-CNN等
            # 暂时使用OpenCV的基础检测器
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            logger.info("检测模型初始化完成")
            
        except Exception as e:
            logger.error(f"检测模型初始化失败: {e}")
            raise
    
    def detect_faces(self, image: Union[np.ndarray, Image.Image]) -> List[Dict[str, Any]]:
        """
        检测人脸
        
        Args:
            image: 输入图片
            
        Returns:
            人脸检测结果列表
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 检测人脸
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            results = []
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                # 检测眼睛
                eyes = self.eye_cascade.detectMultiScale(face_roi)
                
                result = {
                    'bbox': [x, y, w, h],
                    'confidence': 0.8,  # 简化处理
                    'n_eyes': len(eyes),
                    'center': [x + w//2, y + h//2],
                    'area': w * h
                }
                results.append(result)
            
            logger.info(f"检测到 {len(results)} 个人脸")
            return results
            
        except Exception as e:
            logger.error(f"人脸检测失败: {e}")
            raise
    
    def detect_objects(self, image: Union[np.ndarray, Image.Image]) -> List[Dict[str, Any]]:
        """
        检测物体（使用边缘检测和轮廓分析）
        
        Args:
            image: 输入图片
            
        Returns:
            物体检测结果列表
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny边缘检测
            edges = cv2.Canny(blurred, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            min_area = 100  # 最小面积阈值
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    # 获取边界框
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算轮廓特征
                    perimeter = cv2.arcLength(contour, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                    
                    result = {
                        'bbox': [x, y, w, h],
                        'area': area,
                        'perimeter': perimeter,
                        'circularity': circularity,
                        'center': [x + w//2, y + h//2],
                        'confidence': min(area / 1000, 1.0)  # 基于面积的置信度
                    }
                    results.append(result)
            
            # 按面积排序
            results.sort(key=lambda x: x['area'], reverse=True)
            
            logger.info(f"检测到 {len(results)} 个物体")
            return results
            
        except Exception as e:
            logger.error(f"物体检测失败: {e}")
            raise
    
    def detect_text_regions(self, image: Union[np.ndarray, Image.Image]) -> List[Dict[str, Any]]:
        """
        检测文本区域
        
        Args:
            image: 输入图片
            
        Returns:
            文本区域检测结果列表
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 使用MSER检测文本区域
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            results = []
            for region in regions:
                # 获取区域边界框
                x, y, w, h = cv2.boundingRect(region)
                
                # 过滤太小的区域
                if w > 20 and h > 10:
                    result = {
                        'bbox': [x, y, w, h],
                        'area': w * h,
                        'center': [x + w//2, y + h//2],
                        'confidence': 0.7,
                        'type': 'text_region'
                    }
                    results.append(result)
            
            logger.info(f"检测到 {len(results)} 个文本区域")
            return results
            
        except Exception as e:
            logger.error(f"文本区域检测失败: {e}")
            raise
    
    def detect_salient_regions(self, image: Union[np.ndarray, Image.Image]) -> List[Dict[str, Any]]:
        """
        检测显著区域（基于视觉显著性）
        
        Args:
            image: 输入图片
            
        Returns:
            显著区域检测结果列表
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 转换为LAB颜色空间
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            # 计算L通道的局部对比度
            l_channel = lab[:, :, 0]
            
            # 使用高斯滤波计算局部均值
            local_mean = cv2.GaussianBlur(l_channel, (15, 15), 0)
            
            # 计算显著性图
            saliency = np.abs(l_channel.astype(float) - local_mean.astype(float))
            
            # 归一化
            saliency = cv2.normalize(saliency, None, 0, 255, cv2.NORM_MINMAX)
            
            # 阈值化
            _, thresh = cv2.threshold(saliency.astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            min_area = 50
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算显著性分数
                    roi_saliency = saliency[y:y+h, x:x+w]
                    saliency_score = np.mean(roi_saliency)
                    
                    result = {
                        'bbox': [x, y, w, h],
                        'area': area,
                        'saliency_score': saliency_score,
                        'center': [x + w//2, y + h//2],
                        'confidence': min(saliency_score / 255, 1.0),
                        'type': 'salient_region'
                    }
                    results.append(result)
            
            # 按显著性分数排序
            results.sort(key=lambda x: x['saliency_score'], reverse=True)
            
            logger.info(f"检测到 {len(results)} 个显著区域")
            return results
            
        except Exception as e:
            logger.error(f"显著区域检测失败: {e}")
            raise
    
    def detect_motion_regions(self, image: Union[np.ndarray, Image.Image], 
                             prev_image: Optional[Union[np.ndarray, Image.Image]] = None) -> List[Dict[str, Any]]:
        """
        检测运动区域（需要前后帧对比）
        
        Args:
            image: 当前帧
            prev_image: 前一帧
            
        Returns:
            运动区域检测结果列表
        """
        try:
            if prev_image is None:
                logger.warning("没有前一帧图像，无法检测运动区域")
                return []
            
            if isinstance(image, Image.Image):
                image = np.array(image)
            if isinstance(prev_image, Image.Image):
                prev_image = np.array(prev_image)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_RGB2GRAY)
            
            # 计算帧差
            frame_diff = cv2.absdiff(gray, prev_gray)
            
            # 阈值化
            _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            
            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            min_area = 100
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算运动强度
                    roi_diff = frame_diff[y:y+h, x:x+w]
                    motion_intensity = np.mean(roi_diff)
                    
                    result = {
                        'bbox': [x, y, w, h],
                        'area': area,
                        'motion_intensity': motion_intensity,
                        'center': [x + w//2, y + h//2],
                        'confidence': min(motion_intensity / 255, 1.0),
                        'type': 'motion_region'
                    }
                    results.append(result)
            
            # 按运动强度排序
            results.sort(key=lambda x: x['motion_intensity'], reverse=True)
            
            logger.info(f"检测到 {len(results)} 个运动区域")
            return results
            
        except Exception as e:
            logger.error(f"运动区域检测失败: {e}")
            raise
    
    def extract_hotspot_sub_images(self, image: Union[np.ndarray, Image.Image], 
                                  hotspots: List[Dict[str, Any]],
                                  padding: int = 10) -> List[Dict[str, Any]]:
        """
        提取热点子图片
        
        Args:
            image: 原始图片
            hotspots: 热点检测结果
            padding: 边界填充像素
            
        Returns:
            子图片信息列表
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            sub_images = []
            height, width = image.shape[:2]
            
            for i, hotspot in enumerate(hotspots):
                x, y, w, h = hotspot['bbox']
                
                # 添加边界填充
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(width, x + w + padding)
                y2 = min(height, y + h + padding)
                
                # 提取子图片
                sub_image = image[y1:y2, x1:x2]
                
                # 更新边界框信息
                new_bbox = [x1, y1, x2 - x1, y2 - y1]
                
                sub_info = {
                    'id': i,
                    'original_bbox': hotspot['bbox'],
                    'padded_bbox': new_bbox,
                    'sub_image': sub_image,
                    'confidence': hotspot.get('confidence', 0.0),
                    'type': hotspot.get('type', 'unknown'),
                    'area': hotspot.get('area', 0),
                    'center': hotspot.get('center', [0, 0])
                }
                
                sub_images.append(sub_info)
            
            logger.info(f"提取了 {len(sub_images)} 个子图片")
            return sub_images
            
        except Exception as e:
            logger.error(f"子图片提取失败: {e}")
            raise
    
    def detect_all_hotspots(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, List[Dict[str, Any]]]:
        """
        检测所有类型的热点
        
        Args:
            image: 输入图片
            
        Returns:
            所有热点检测结果
        """
        try:
            all_hotspots = {}
            
            # 检测人脸
            try:
                faces = self.detect_faces(image)
                all_hotspots['faces'] = faces
            except Exception as e:
                logger.warning(f"人脸检测失败: {e}")
                all_hotspots['faces'] = []
            
            # 检测物体
            try:
                objects = self.detect_objects(image)
                all_hotspots['objects'] = objects
            except Exception as e:
                logger.warning(f"物体检测失败: {e}")
                all_hotspots['objects'] = []
            
            # 检测文本区域
            try:
                text_regions = self.detect_text_regions(image)
                all_hotspots['text_regions'] = text_regions
            except Exception as e:
                logger.warning(f"文本区域检测失败: {e}")
                all_hotspots['text_regions'] = []
            
            # 检测显著区域
            try:
                salient_regions = self.detect_salient_regions(image)
                all_hotspots['salient_regions'] = salient_regions
            except Exception as e:
                logger.warning(f"显著区域检测失败: {e}")
                all_hotspots['salient_regions'] = []
            
            # 统计总数
            total_hotspots = sum(len(hotspots) for hotspots in all_hotspots.values())
            logger.info(f"热点检测完成，总共检测到 {total_hotspots} 个热点")
            
            return all_hotspots
            
        except Exception as e:
            logger.error(f"热点检测失败: {e}")
            raise
    
    def visualize_hotspots(self, image: Union[np.ndarray, Image.Image],
                          hotspots: Dict[str, List[Dict[str, Any]]],
                          save_path: Optional[Union[str, Path]] = None) -> np.ndarray:
        """
        可视化热点检测结果
        
        Args:
            image: 原始图片
            hotspots: 热点检测结果
            save_path: 保存路径
            
        Returns:
            可视化结果图片
        """
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 创建可视化图片
            vis_image = image.copy()
            
            # 定义颜色映射
            colors = {
                'faces': (255, 0, 0),      # 红色
                'objects': (0, 255, 0),    # 绿色
                'text_regions': (0, 0, 255),  # 蓝色
                'salient_regions': (255, 255, 0),  # 黄色
                'motion_regions': (255, 0, 255)  # 紫色
            }
            
            # 绘制不同类型的热点
            for hotspot_type, hotspot_list in hotspots.items():
                color = colors.get(hotspot_type, (128, 128, 128))
                
                for hotspot in hotspot_list:
                    x, y, w, h = hotspot['bbox']
                    confidence = hotspot.get('confidence', 0.0)
                    
                    # 绘制边界框
                    cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
                    
                    # 绘制标签
                    label = f"{hotspot_type}: {confidence:.2f}"
                    cv2.putText(vis_image, label, (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # 绘制中心点
                    center = hotspot.get('center', [x + w//2, y + h//2])
                    cv2.circle(vis_image, tuple(center), 3, color, -1)
            
            # 保存结果
            if save_path:
                if isinstance(save_path, str):
                    save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(save_path), cv2.cvtColor(vis_image, cv2.COLOR_RGB2BGR))
                logger.info(f"热点可视化结果保存到: {save_path}")
            
            return vis_image
            
        except Exception as e:
            logger.error(f"热点可视化失败: {e}")
            raise 