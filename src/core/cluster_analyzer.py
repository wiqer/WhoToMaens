"""
聚类分析器模块

负责对图片特征进行聚类分析，支持多种聚类算法和可视化。
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import hdbscan
import umap
from typing import Union, List, Tuple, Optional, Dict, Any
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger(__name__)


class ClusterAnalyzer:
    """聚类分析器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化聚类分析器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.scaler = StandardScaler()
        self.pca = None
        self.cluster_model = None
        self.cluster_labels = None
        self.feature_names = None
        
        # 设置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        logger.info("聚类分析器初始化完成")
    
    def prepare_features(self, features: Union[np.ndarray, List[np.ndarray], Dict[str, np.ndarray]]) -> np.ndarray:
        """
        准备特征数据
        
        Args:
            features: 特征数据
            
        Returns:
            处理后的特征矩阵
        """
        try:
            if isinstance(features, dict):
                # 字典格式：{'feature_name': feature_array}
                feature_list = []
                self.feature_names = []
                
                for name, feature_array in features.items():
                    if isinstance(feature_array, np.ndarray):
                        if len(feature_array.shape) == 1:
                            feature_list.append(feature_array.reshape(-1, 1))
                        else:
                            feature_list.append(feature_array)
                        self.feature_names.append(name)
                    else:
                        logger.warning(f"跳过非numpy数组特征: {name}")
                
                if not feature_list:
                    raise ValueError("没有有效的特征数据")
                
                # 水平拼接所有特征
                feature_matrix = np.hstack(feature_list)
                
            elif isinstance(features, list):
                # 列表格式：[feature_array1, feature_array2, ...]
                feature_list = []
                for i, feature_array in enumerate(features):
                    if isinstance(feature_array, np.ndarray):
                        if len(feature_array.shape) == 1:
                            feature_list.append(feature_array.reshape(-1, 1))
                        else:
                            feature_list.append(feature_array)
                    else:
                        logger.warning(f"跳过第{i}个非numpy数组特征")
                
                if not feature_list:
                    raise ValueError("没有有效的特征数据")
                
                feature_matrix = np.hstack(feature_list)
                self.feature_names = [f"feature_{i}" for i in range(len(feature_list))]
                
            elif isinstance(features, np.ndarray):
                # 已经是numpy数组
                feature_matrix = features
                if len(feature_matrix.shape) == 1:
                    feature_matrix = feature_matrix.reshape(-1, 1)
                self.feature_names = [f"feature_{i}" for i in range(feature_matrix.shape[1])]
            
            else:
                raise ValueError(f"不支持的特征数据类型: {type(features)}")
            
            # 检查数据维度
            if feature_matrix.shape[0] < 2:
                raise ValueError("样本数量太少，无法进行聚类分析")
            
            # 处理缺失值
            feature_matrix = self._handle_missing_values(feature_matrix)
            
            # 标准化
            feature_matrix = self.scaler.fit_transform(feature_matrix)
            
            logger.info(f"特征准备完成，形状: {feature_matrix.shape}")
            return feature_matrix
            
        except Exception as e:
            logger.error(f"特征准备失败: {e}")
            raise
    
    def _handle_missing_values(self, feature_matrix: np.ndarray) -> np.ndarray:
        """处理缺失值"""
        # 检查是否有NaN或无穷大值
        if np.any(np.isnan(feature_matrix)) or np.any(np.isinf(feature_matrix)):
            logger.warning("检测到缺失值或无穷大值，使用均值填充")
            
            # 使用均值填充NaN
            feature_matrix = np.where(np.isnan(feature_matrix), 
                                    np.nanmean(feature_matrix, axis=0), 
                                    feature_matrix)
            
            # 使用均值填充无穷大值
            feature_matrix = np.where(np.isinf(feature_matrix), 
                                    np.nanmean(feature_matrix, axis=0), 
                                    feature_matrix)
        
        return feature_matrix
    
    def reduce_dimensions(self, feature_matrix: np.ndarray, 
                         method: str = 'pca', 
                         n_components: int = 50) -> np.ndarray:
        """
        降维处理
        
        Args:
            feature_matrix: 特征矩阵
            method: 降维方法 ('pca', 'tsne', 'umap')
            n_components: 目标维度
            
        Returns:
            降维后的特征矩阵
        """
        try:
            if method.lower() == 'pca':
                self.pca = PCA(n_components=min(n_components, feature_matrix.shape[1]))
                reduced_features = self.pca.fit_transform(feature_matrix)
                explained_variance = np.sum(self.pca.explained_variance_ratio_)
                logger.info(f"PCA降维完成，解释方差: {explained_variance:.3f}")
                
            elif method.lower() == 'tsne':
                if feature_matrix.shape[1] > 50:
                    # 先用PCA降维到50维
                    pca_temp = PCA(n_components=50)
                    temp_features = pca_temp.fit_transform(feature_matrix)
                else:
                    temp_features = feature_matrix
                
                tsne = TSNE(n_components=n_components, random_state=42, perplexity=min(30, feature_matrix.shape[0]-1))
                reduced_features = tsne.fit_transform(temp_features)
                logger.info("t-SNE降维完成")
                
            elif method.lower() == 'umap':
                umap_reducer = umap.UMAP(n_components=n_components, random_state=42)
                reduced_features = umap_reducer.fit_transform(feature_matrix)
                logger.info("UMAP降维完成")
                
            else:
                raise ValueError(f"不支持的降维方法: {method}")
            
            return reduced_features
            
        except Exception as e:
            logger.error(f"降维处理失败: {e}")
            raise
    
    def kmeans_clustering(self, feature_matrix: np.ndarray, 
                         n_clusters: int = 5,
                         random_state: int = 42) -> np.ndarray:
        """
        K-means聚类
        
        Args:
            feature_matrix: 特征矩阵
            n_clusters: 聚类数量
            random_state: 随机种子
            
        Returns:
            聚类标签
        """
        try:
            self.cluster_model = KMeans(
                n_clusters=n_clusters,
                random_state=random_state,
                n_init=10
            )
            
            self.cluster_labels = self.cluster_model.fit_predict(feature_matrix)
            
            # 计算聚类质量指标
            silhouette_avg = silhouette_score(feature_matrix, self.cluster_labels)
            calinski_score = calinski_harabasz_score(feature_matrix, self.cluster_labels)
            davies_score = davies_bouldin_score(feature_matrix, self.cluster_labels)
            
            logger.info(f"K-means聚类完成，聚类数量: {n_clusters}")
            logger.info(f"聚类质量 - Silhouette: {silhouette_avg:.3f}, Calinski-Harabasz: {calinski_score:.3f}, Davies-Bouldin: {davies_score:.3f}")
            
            return self.cluster_labels
            
        except Exception as e:
            logger.error(f"K-means聚类失败: {e}")
            raise
    
    def dbscan_clustering(self, feature_matrix: np.ndarray,
                         eps: float = 0.5,
                         min_samples: int = 5) -> np.ndarray:
        """
        DBSCAN聚类
        
        Args:
            feature_matrix: 特征矩阵
            eps: 邻域半径
            min_samples: 最小样本数
            
        Returns:
            聚类标签
        """
        try:
            self.cluster_model = DBSCAN(
                eps=eps,
                min_samples=min_samples
            )
            
            self.cluster_labels = self.cluster_model.fit_predict(feature_matrix)
            
            # 统计聚类结果
            n_clusters = len(set(self.cluster_labels)) - (1 if -1 in self.cluster_labels else 0)
            n_noise = list(self.cluster_labels).count(-1)
            
            logger.info(f"DBSCAN聚类完成，聚类数量: {n_clusters}, 噪声点数量: {n_noise}")
            
            return self.cluster_labels
            
        except Exception as e:
            logger.error(f"DBSCAN聚类失败: {e}")
            raise
    
    def hdbscan_clustering(self, feature_matrix: np.ndarray,
                          min_cluster_size: int = 5,
                          min_samples: int = 5) -> np.ndarray:
        """
        HDBSCAN聚类
        
        Args:
            feature_matrix: 特征矩阵
            min_cluster_size: 最小聚类大小
            min_samples: 最小样本数
            
        Returns:
            聚类标签
        """
        try:
            self.cluster_model = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples
            )
            
            self.cluster_labels = self.cluster_model.fit_predict(feature_matrix)
            
            # 统计聚类结果
            n_clusters = len(set(self.cluster_labels)) - (1 if -1 in self.cluster_labels else 0)
            n_noise = list(self.cluster_labels).count(-1)
            
            logger.info(f"HDBSCAN聚类完成，聚类数量: {n_clusters}, 噪声点数量: {n_noise}")
            
            return self.cluster_labels
            
        except Exception as e:
            logger.error(f"HDBSCAN聚类失败: {e}")
            raise
    
    def hierarchical_clustering(self, feature_matrix: np.ndarray,
                               n_clusters: int = 5,
                               linkage: str = 'ward') -> np.ndarray:
        """
        层次聚类
        
        Args:
            feature_matrix: 特征矩阵
            n_clusters: 聚类数量
            linkage: 链接方法
            
        Returns:
            聚类标签
        """
        try:
            self.cluster_model = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage=linkage
            )
            
            self.cluster_labels = self.cluster_model.fit_predict(feature_matrix)
            
            # 计算聚类质量指标
            silhouette_avg = silhouette_score(feature_matrix, self.cluster_labels)
            calinski_score = calinski_harabasz_score(feature_matrix, self.cluster_labels)
            davies_score = davies_bouldin_score(feature_matrix, self.cluster_labels)
            
            logger.info(f"层次聚类完成，聚类数量: {n_clusters}, 链接方法: {linkage}")
            logger.info(f"聚类质量 - Silhouette: {silhouette_avg:.3f}, Calinski-Harabasz: {calinski_score:.3f}, Davies-Bouldin: {davies_score:.3f}")
            
            return self.cluster_labels
            
        except Exception as e:
            logger.error(f"层次聚类失败: {e}")
            raise
    
    def auto_clustering(self, feature_matrix: np.ndarray,
                       method: str = 'auto',
                       max_clusters: int = 10) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        自动聚类（自动选择最优参数）
        
        Args:
            feature_matrix: 特征矩阵
            method: 聚类方法
            max_clusters: 最大聚类数量
            
        Returns:
            聚类标签和最优参数
        """
        try:
            if method == 'auto':
                # 尝试多种方法，选择最优的
                methods = ['kmeans', 'hdbscan', 'dbscan']
                best_score = -1
                best_labels = None
                best_params = None
                
                for method_name in methods:
                    try:
                        if method_name == 'kmeans':
                            # 尝试不同的聚类数量
                            for n_clusters in range(2, min(max_clusters + 1, feature_matrix.shape[0])):
                                labels = self.kmeans_clustering(feature_matrix, n_clusters)
                                if len(set(labels)) > 1:  # 确保有多个聚类
                                    score = silhouette_score(feature_matrix, labels)
                                    if score > best_score:
                                        best_score = score
                                        best_labels = labels
                                        best_params = {'method': 'kmeans', 'n_clusters': n_clusters}
                        
                        elif method_name == 'hdbscan':
                            labels = self.hdbscan_clustering(feature_matrix)
                            if len(set(labels)) > 1:
                                score = silhouette_score(feature_matrix, labels)
                                if score > best_score:
                                    best_score = score
                                    best_labels = labels
                                    best_params = {'method': 'hdbscan'}
                        
                        elif method_name == 'dbscan':
                            # 尝试不同的eps值
                            for eps in [0.1, 0.3, 0.5, 0.7, 1.0]:
                                labels = self.dbscan_clustering(feature_matrix, eps=eps)
                                if len(set(labels)) > 1:
                                    score = silhouette_score(feature_matrix, labels)
                                    if score > best_score:
                                        best_score = score
                                        best_labels = labels
                                        best_params = {'method': 'dbscan', 'eps': eps}
                    
                    except Exception as e:
                        logger.warning(f"方法 {method_name} 失败: {e}")
                        continue
                
                if best_labels is not None:
                    self.cluster_labels = best_labels
                    logger.info(f"自动聚类完成，最优方法: {best_params}, 得分: {best_score:.3f}")
                    return best_labels, best_params
                else:
                    raise ValueError("所有聚类方法都失败了")
            
            else:
                # 使用指定的方法
                if method == 'kmeans':
                    labels = self.kmeans_clustering(feature_matrix, max_clusters)
                    params = {'method': 'kmeans', 'n_clusters': max_clusters}
                elif method == 'hdbscan':
                    labels = self.hdbscan_clustering(feature_matrix)
                    params = {'method': 'hdbscan'}
                elif method == 'dbscan':
                    labels = self.dbscan_clustering(feature_matrix)
                    params = {'method': 'dbscan'}
                else:
                    raise ValueError(f"不支持的聚类方法: {method}")
                
                return labels, params
                
        except Exception as e:
            logger.error(f"自动聚类失败: {e}")
            raise
    
    def analyze_clusters(self, feature_matrix: np.ndarray, 
                        cluster_labels: np.ndarray) -> Dict[str, Any]:
        """
        分析聚类结果
        
        Args:
            feature_matrix: 特征矩阵
            cluster_labels: 聚类标签
            
        Returns:
            聚类分析结果
        """
        try:
            analysis = {}
            
            # 基本统计
            unique_labels = np.unique(cluster_labels)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
            n_noise = np.sum(cluster_labels == -1)
            
            analysis['n_clusters'] = n_clusters
            analysis['n_noise'] = n_noise
            analysis['cluster_sizes'] = {}
            
            for label in unique_labels:
                if label != -1:
                    size = np.sum(cluster_labels == label)
                    analysis['cluster_sizes'][f'cluster_{label}'] = size
            
            # 聚类质量指标
            if n_clusters > 1:
                analysis['silhouette_score'] = silhouette_score(feature_matrix, cluster_labels)
                analysis['calinski_harabasz_score'] = calinski_harabasz_score(feature_matrix, cluster_labels)
                analysis['davies_bouldin_score'] = davies_bouldin_score(feature_matrix, cluster_labels)
            
            # 特征重要性分析
            if self.feature_names is not None:
                feature_importance = self._analyze_feature_importance(feature_matrix, cluster_labels)
                analysis['feature_importance'] = feature_importance
            
            logger.info(f"聚类分析完成，聚类数量: {n_clusters}")
            return analysis
            
        except Exception as e:
            logger.error(f"聚类分析失败: {e}")
            raise
    
    def _analyze_feature_importance(self, feature_matrix: np.ndarray, 
                                   cluster_labels: np.ndarray) -> Dict[str, float]:
        """分析特征重要性"""
        try:
            importance = {}
            unique_labels = np.unique(cluster_labels)
            
            for i in range(feature_matrix.shape[1]):
                feature_name = self.feature_names[i] if self.feature_names else f"feature_{i}"
                
                # 计算每个特征在不同聚类中的方差
                variances = []
                for label in unique_labels:
                    if label != -1:  # 排除噪声点
                        cluster_data = feature_matrix[cluster_labels == label, i]
                        if len(cluster_data) > 1:
                            variances.append(np.var(cluster_data))
                
                if variances:
                    # 使用方差的标准差作为重要性指标
                    importance[feature_name] = np.std(variances)
                else:
                    importance[feature_name] = 0.0
            
            # 归一化重要性分数
            max_importance = max(importance.values()) if importance.values() else 1.0
            if max_importance > 0:
                importance = {k: v / max_importance for k, v in importance.items()}
            
            return importance
            
        except Exception as e:
            logger.error(f"特征重要性分析失败: {e}")
            return {}
    
    def visualize_clusters(self, feature_matrix: np.ndarray,
                          cluster_labels: np.ndarray,
                          save_path: Optional[Union[str, Path]] = None,
                          figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        可视化聚类结果
        
        Args:
            feature_matrix: 特征矩阵
            cluster_labels: 聚类标签
            save_path: 保存路径
            figsize: 图片大小
        """
        try:
            # 如果特征维度大于2，先降维
            if feature_matrix.shape[1] > 2:
                logger.info("特征维度大于2，使用PCA降维到2维进行可视化")
                pca_vis = PCA(n_components=2)
                vis_features = pca_vis.fit_transform(feature_matrix)
            else:
                vis_features = feature_matrix
            
            # 创建图形
            fig, axes = plt.subplots(2, 2, figsize=figsize)
            fig.suptitle('聚类分析结果可视化', fontsize=16)
            
            # 1. 散点图
            unique_labels = np.unique(cluster_labels)
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
            
            for label, color in zip(unique_labels, colors):
                if label == -1:
                    # 噪声点用黑色
                    mask = cluster_labels == label
                    axes[0, 0].scatter(vis_features[mask, 0], vis_features[mask, 1], 
                                     c='black', marker='x', s=20, alpha=0.6, label='噪声')
                else:
                    mask = cluster_labels == label
                    axes[0, 0].scatter(vis_features[mask, 0], vis_features[mask, 1], 
                                     c=[color], s=30, alpha=0.7, label=f'聚类 {label}')
            
            axes[0, 0].set_title('聚类散点图')
            axes[0, 0].set_xlabel('特征1')
            axes[0, 0].set_ylabel('特征2')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. 聚类大小分布
            cluster_sizes = []
            cluster_names = []
            for label in unique_labels:
                if label != -1:
                    size = np.sum(cluster_labels == label)
                    cluster_sizes.append(size)
                    cluster_names.append(f'聚类 {label}')
            
            if cluster_sizes:
                axes[0, 1].bar(cluster_names, cluster_sizes, color=colors[:-1])
                axes[0, 1].set_title('聚类大小分布')
                axes[0, 1].set_ylabel('样本数量')
                axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. 特征重要性（如果有）
            if hasattr(self, 'feature_importance') and self.feature_importance:
                feature_names = list(self.feature_importance.keys())
                importance_values = list(self.feature_importance.values())
                
                # 选择前10个最重要的特征
                if len(feature_names) > 10:
                    indices = np.argsort(importance_values)[-10:]
                    feature_names = [feature_names[i] for i in indices]
                    importance_values = [importance_values[i] for i in indices]
                
                axes[1, 0].barh(feature_names, importance_values)
                axes[1, 0].set_title('特征重要性')
                axes[1, 0].set_xlabel('重要性分数')
            
            # 4. 聚类质量指标
            if len(unique_labels) > 1:
                metrics = {}
                try:
                    metrics['Silhouette'] = silhouette_score(feature_matrix, cluster_labels)
                except:
                    metrics['Silhouette'] = 0
                
                try:
                    metrics['Calinski-Harabasz'] = calinski_harabasz_score(feature_matrix, cluster_labels)
                except:
                    metrics['Calinski-Harabasz'] = 0
                
                try:
                    metrics['Davies-Bouldin'] = davies_bouldin_score(feature_matrix, cluster_labels)
                except:
                    metrics['Davies-Bouldin'] = 0
                
                metric_names = list(metrics.keys())
                metric_values = list(metrics.values())
                
                axes[1, 1].bar(metric_names, metric_values, color=['skyblue', 'lightgreen', 'lightcoral'])
                axes[1, 1].set_title('聚类质量指标')
                axes[1, 1].set_ylabel('分数')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_path:
                if isinstance(save_path, str):
                    save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"聚类可视化结果保存到: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"聚类可视化失败: {e}")
            raise
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """
        获取聚类结果摘要
        
        Returns:
            聚类摘要信息
        """
        try:
            if self.cluster_labels is None:
                raise ValueError("还没有进行聚类分析")
            
            summary = {
                'n_samples': len(self.cluster_labels),
                'n_clusters': len(set(self.cluster_labels)) - (1 if -1 in self.cluster_labels else 0),
                'n_noise': np.sum(self.cluster_labels == -1),
                'cluster_distribution': {}
            }
            
            unique_labels = np.unique(self.cluster_labels)
            for label in unique_labels:
                if label == -1:
                    summary['cluster_distribution']['noise'] = int(np.sum(self.cluster_labels == label))
                else:
                    summary['cluster_distribution'][f'cluster_{label}'] = int(np.sum(self.cluster_labels == label))
            
            return summary
            
        except Exception as e:
            logger.error(f"获取聚类摘要失败: {e}")
            raise 