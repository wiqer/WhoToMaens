"""
FastAPI应用程序

提供RESTful API接口。
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import numpy as np
from PIL import Image
import io
import json
from pathlib import Path

from ..core import ImageProcessor, FeatureExtractor, ClusterAnalyzer, HotspotDetector, ContentAnalyzer

logger = logging.getLogger(__name__)


class ImageAnalysisRequest(BaseModel):
    """图片分析请求模型"""
    image_path: Optional[str] = None
    analysis_type: str = "all"  # all, features, clustering, hotspots, content
    clustering_method: str = "auto"
    n_clusters: Optional[int] = None


class ImageAnalysisResponse(BaseModel):
    """图片分析响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FastAPIApp:
    """FastAPI应用程序类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化FastAPI应用
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 初始化核心组件
        self.image_processor = ImageProcessor()
        self.feature_extractor = FeatureExtractor()
        self.cluster_analyzer = ClusterAnalyzer()
        self.hotspot_detector = HotspotDetector()
        self.content_analyzer = ContentAnalyzer()
        
        # 创建FastAPI应用
        self.app = FastAPI(
            title="WhoToMaens 图片分析系统",
            description="多功能融合图片BERT分析系统API",
            version="1.0.0"
        )
        
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
        self._register_routes()
        
        logger.info("FastAPI应用初始化完成")
    
    def _register_routes(self):
        """注册API路由"""
        
        @self.app.get("/")
        async def root():
            """根路径"""
            return {
                "message": "WhoToMaens 图片分析系统",
                "version": "1.0.0",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy"}
        
        @self.app.post("/analyze/image", response_model=ImageAnalysisResponse)
        async def analyze_image(
            file: UploadFile = File(...),
            analysis_type: str = Form("all"),
            clustering_method: str = Form("auto"),
            n_clusters: Optional[int] = Form(None)
        ):
            """分析上传的图片"""
            try:
                # 读取图片
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data))
                
                # 转换为numpy数组
                image_array = np.array(image)
                
                # 根据分析类型执行不同的分析
                result = await self._perform_analysis(
                    image_array, analysis_type, clustering_method, n_clusters
                )
                
                return ImageAnalysisResponse(
                    success=True,
                    message="图片分析完成",
                    data=result
                )
                
            except Exception as e:
                logger.error(f"图片分析失败: {e}")
                return ImageAnalysisResponse(
                    success=False,
                    message="图片分析失败",
                    error=str(e)
                )
        
        @self.app.post("/extract/features")
        async def extract_features(file: UploadFile = File(...)):
            """提取图片特征"""
            try:
                # 读取图片
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data))
                image_array = np.array(image)
                
                # 提取特征
                features = self.feature_extractor.extract_all_features(image_array)
                
                # 转换为可序列化的格式
                serializable_features = {}
                for key, value in features.items():
                    if isinstance(value, np.ndarray):
                        serializable_features[key] = value.tolist()
                    else:
                        serializable_features[key] = value
                
                return {
                    "success": True,
                    "message": "特征提取完成",
                    "features": serializable_features
                }
                
            except Exception as e:
                logger.error(f"特征提取失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/detect/hotspots")
        async def detect_hotspots(file: UploadFile = File(...)):
            """检测热点区域"""
            try:
                # 读取图片
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data))
                image_array = np.array(image)
                
                # 检测热点
                hotspots = self.hotspot_detector.detect_all_hotspots(image_array)
                
                # 提取子图片
                all_sub_images = []
                for hotspot_type, hotspot_list in hotspots.items():
                    if hotspot_list:
                        sub_images = self.hotspot_detector.extract_hotspot_sub_images(
                            image_array, hotspot_list
                        )
                        all_sub_images.extend(sub_images)
                
                # 转换为可序列化的格式
                serializable_hotspots = {}
                for key, value in hotspots.items():
                    serializable_hotspots[key] = [
                        {k: v for k, v in item.items() if k != 'sub_image'}
                        for item in value
                    ]
                
                return {
                    "success": True,
                    "message": "热点检测完成",
                    "hotspots": serializable_hotspots,
                    "n_sub_images": len(all_sub_images)
                }
                
            except Exception as e:
                logger.error(f"热点检测失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analyze/content")
        async def analyze_content(file: UploadFile = File(...)):
            """分析图片内容"""
            try:
                # 读取图片
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data))
                image_array = np.array(image)
                
                # 分析内容
                content_analysis = self.content_analyzer.analyze_content(image_array)
                
                # 生成结构化描述
                structured_description = self.content_analyzer.generate_structured_description(image_array)
                content_analysis['structured_description'] = structured_description
                
                return {
                    "success": True,
                    "message": "内容分析完成",
                    "content_analysis": content_analysis
                }
                
            except Exception as e:
                logger.error(f"内容分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/cluster/images")
        async def cluster_images(files: List[UploadFile] = File(...)):
            """对多张图片进行聚类"""
            try:
                if len(files) < 2:
                    raise HTTPException(status_code=400, detail="至少需要2张图片进行聚类")
                
                # 读取所有图片
                images = []
                for file in files:
                    image_data = await file.read()
                    image = Image.open(io.BytesIO(image_data))
                    image_array = np.array(image)
                    images.append(image_array)
                
                # 提取特征
                all_features = []
                for image in images:
                    features = self.feature_extractor.extract_all_features(image)
                    # 合并所有特征
                    combined_features = np.concatenate([
                        features.get('resnet', np.array([])).flatten(),
                        features.get('clip', np.array([])).flatten(),
                        features.get('hsv_histogram', np.array([])).flatten(),
                        features.get('color_moments', np.array([])).flatten()
                    ])
                    all_features.append(combined_features)
                
                # 转换为numpy数组
                feature_matrix = np.array(all_features)
                
                # 聚类分析
                cluster_labels, params = self.cluster_analyzer.auto_clustering(feature_matrix)
                
                # 分析聚类结果
                analysis = self.cluster_analyzer.analyze_clusters(feature_matrix, cluster_labels)
                
                return {
                    "success": True,
                    "message": "图片聚类完成",
                    "cluster_labels": cluster_labels.tolist(),
                    "cluster_params": params,
                    "analysis": analysis
                }
                
            except Exception as e:
                logger.error(f"图片聚类失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/search/similar")
        async def search_similar_images(
            query_image: UploadFile = File(...),
            reference_images: List[UploadFile] = File(...),
            top_k: int = Form(5)
        ):
            """搜索相似图片"""
            try:
                # 读取查询图片
                query_data = await query_image.read()
                query_img = Image.open(io.BytesIO(query_data))
                query_array = np.array(query_img)
                
                # 提取查询图片特征
                query_features = self.feature_extractor.extract_all_features(query_array)
                query_combined = np.concatenate([
                    query_features.get('resnet', np.array([])).flatten(),
                    query_features.get('clip', np.array([])).flatten(),
                    query_features.get('hsv_histogram', np.array([])).flatten(),
                    query_features.get('color_moments', np.array([])).flatten()
                ])
                
                # 读取参考图片
                reference_features = []
                for ref_file in reference_images:
                    ref_data = await ref_file.read()
                    ref_img = Image.open(io.BytesIO(ref_data))
                    ref_array = np.array(ref_img)
                    
                    features = self.feature_extractor.extract_all_features(ref_array)
                    combined = np.concatenate([
                        features.get('resnet', np.array([])).flatten(),
                        features.get('clip', np.array([])).flatten(),
                        features.get('hsv_histogram', np.array([])).flatten(),
                        features.get('color_moments', np.array([])).flatten()
                    ])
                    reference_features.append(combined)
                
                # 计算相似度
                similarities = []
                for i, ref_feat in enumerate(reference_features):
                    # 使用余弦相似度
                    similarity = np.dot(query_combined, ref_feat) / (
                        np.linalg.norm(query_combined) * np.linalg.norm(ref_feat)
                    )
                    similarities.append((i, similarity))
                
                # 排序并返回top_k
                similarities.sort(key=lambda x: x[1], reverse=True)
                top_results = similarities[:top_k]
                
                return {
                    "success": True,
                    "message": "相似图片搜索完成",
                    "results": [
                        {"index": idx, "similarity": float(sim)} 
                        for idx, sim in top_results
                    ]
                }
                
            except Exception as e:
                logger.error(f"相似图片搜索失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _perform_analysis(self, image_array: np.ndarray, 
                               analysis_type: str, 
                               clustering_method: str,
                               n_clusters: Optional[int]) -> Dict[str, Any]:
        """执行图片分析"""
        try:
            result = {}
            
            if analysis_type in ["all", "features"]:
                # 特征提取
                features = self.feature_extractor.extract_all_features(image_array)
                result["features"] = {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in features.items()
                }
            
            if analysis_type in ["all", "hotspots"]:
                # 热点检测
                hotspots = self.hotspot_detector.detect_all_hotspots(image_array)
                result["hotspots"] = {
                    k: [{kk: vv for kk, vv in item.items() if kk != 'sub_image'}
                        for item in v]
                    for k, v in hotspots.items()
                }
            
            if analysis_type in ["all", "content"]:
                # 内容分析
                content_analysis = self.content_analyzer.analyze_content(image_array)
                structured_description = self.content_analyzer.generate_structured_description(image_array)
                content_analysis['structured_description'] = structured_description
                result["content"] = content_analysis
            
            if analysis_type in ["all", "clustering"] and "features" in result:
                # 聚类分析（需要特征数据）
                # 这里简化处理，只对单张图片进行特征分析
                feature_matrix = np.array([list(result["features"].values())[0]])
                cluster_summary = self.cluster_analyzer.get_cluster_summary()
                result["clustering"] = {
                    "feature_matrix_shape": feature_matrix.shape,
                    "summary": cluster_summary
                }
            
            return result
            
        except Exception as e:
            logger.error(f"图片分析执行失败: {e}")
            raise
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """
        运行FastAPI应用
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否开启调试模式
        """
        try:
            logger.info(f"启动FastAPI应用: http://{host}:{port}")
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                log_level="info"
            )
            
        except Exception as e:
            logger.error(f"FastAPI应用启动失败: {e}")
            raise 