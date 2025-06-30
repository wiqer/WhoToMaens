"""
可视化工具模块

包含数据可视化和结果展示的工具函数。
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VisualizationUtils:
    """可视化工具类"""
    
    def __init__(self):
        """初始化可视化工具"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置Seaborn样式
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def plot_cluster_results(self, feature_matrix: np.ndarray,
                           cluster_labels: np.ndarray,
                           save_path: Optional[str] = None,
                           figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        绘制聚类结果
        
        Args:
            feature_matrix: 特征矩阵
            cluster_labels: 聚类标签
            save_path: 保存路径
            figsize: 图片大小
        """
        try:
            # 如果特征维度大于2，先降维
            if feature_matrix.shape[1] > 2:
                from sklearn.decomposition import PCA
                pca = PCA(n_components=2)
                vis_features = pca.fit_transform(feature_matrix)
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
            
            # 3. 特征分布
            if feature_matrix.shape[1] > 1:
                feature_means = np.mean(feature_matrix, axis=0)
                feature_stds = np.std(feature_matrix, axis=0)
                
                axes[1, 0].errorbar(range(len(feature_means)), feature_means, 
                                  yerr=feature_stds, fmt='o-', capsize=5)
                axes[1, 0].set_title('特征分布')
                axes[1, 0].set_xlabel('特征索引')
                axes[1, 0].set_ylabel('特征值')
            
            # 4. 聚类质量指标
            if len(unique_labels) > 1:
                from sklearn.metrics import silhouette_score
                try:
                    silhouette_avg = silhouette_score(feature_matrix, cluster_labels)
                    axes[1, 1].bar(['Silhouette Score'], [silhouette_avg], 
                                  color='skyblue')
                    axes[1, 1].set_title('聚类质量指标')
                    axes[1, 1].set_ylabel('分数')
                    axes[1, 1].set_ylim(0, 1)
                except:
                    pass
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"聚类可视化结果保存到: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"聚类结果可视化失败: {e}")
            raise
    
    def plot_feature_importance(self, feature_names: List[str],
                               importance_scores: List[float],
                               save_path: Optional[str] = None,
                               top_k: int = 20) -> None:
        """
        绘制特征重要性
        
        Args:
            feature_names: 特征名称列表
            importance_scores: 重要性分数列表
            save_path: 保存路径
            top_k: 显示前k个特征
        """
        try:
            # 选择前k个最重要的特征
            if len(feature_names) > top_k:
                indices = np.argsort(importance_scores)[-top_k:]
                feature_names = [feature_names[i] for i in indices]
                importance_scores = [importance_scores[i] for i in indices]
            
            # 创建图形
            plt.figure(figsize=(12, 8))
            
            # 水平条形图
            y_pos = np.arange(len(feature_names))
            plt.barh(y_pos, importance_scores, color='skyblue', alpha=0.7)
            
            plt.yticks(y_pos, feature_names)
            plt.xlabel('重要性分数')
            plt.title('特征重要性排序')
            plt.grid(True, alpha=0.3)
            
            # 添加数值标签
            for i, v in enumerate(importance_scores):
                plt.text(v + 0.01, i, f'{v:.3f}', va='center')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"特征重要性图保存到: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"特征重要性可视化失败: {e}")
            raise
    
    def plot_analysis_results(self, results: Dict[str, Any],
                            save_path: Optional[str] = None) -> None:
        """
        绘制分析结果
        
        Args:
            results: 分析结果字典
            save_path: 保存路径
        """
        try:
            # 创建子图
            n_plots = len(results)
            fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 5))
            
            if n_plots == 1:
                axes = [axes]
            
            for i, (key, value) in enumerate(results.items()):
                if isinstance(value, (list, np.ndarray)):
                    # 绘制列表/数组数据
                    axes[i].plot(value)
                    axes[i].set_title(key)
                    axes[i].set_xlabel('索引')
                    axes[i].set_ylabel('值')
                elif isinstance(value, dict):
                    # 绘制字典数据
                    keys = list(value.keys())
                    values = list(value.values())
                    axes[i].bar(keys, values)
                    axes[i].set_title(key)
                    axes[i].tick_params(axis='x', rotation=45)
                else:
                    # 绘制单个值
                    axes[i].text(0.5, 0.5, f'{key}: {value}', 
                               ha='center', va='center', transform=axes[i].transAxes)
                    axes[i].set_title(key)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"分析结果图保存到: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"分析结果可视化失败: {e}")
            raise
    
    def create_dashboard(self, data: Dict[str, Any],
                        save_path: Optional[str] = None) -> None:
        """
        创建数据仪表板
        
        Args:
            data: 数据字典
            save_path: 保存路径
        """
        try:
            # 创建仪表板布局
            fig = plt.figure(figsize=(16, 12))
            
            # 根据数据类型创建不同的可视化
            plot_index = 1
            
            for key, value in data.items():
                if isinstance(value, dict) and 'type' in value:
                    # 根据类型创建特定可视化
                    if value['type'] == 'clustering':
                        self._plot_clustering_dashboard(fig, value, plot_index)
                        plot_index += 1
                    elif value['type'] == 'features':
                        self._plot_features_dashboard(fig, value, plot_index)
                        plot_index += 1
                    elif value['type'] == 'statistics':
                        self._plot_statistics_dashboard(fig, value, plot_index)
                        plot_index += 1
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"仪表板保存到: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"仪表板创建失败: {e}")
            raise
    
    def _plot_clustering_dashboard(self, fig, data: Dict[str, Any], plot_index: int) -> None:
        """绘制聚类仪表板"""
        try:
            ax = fig.add_subplot(2, 3, plot_index)
            
            if 'cluster_sizes' in data:
                cluster_names = list(data['cluster_sizes'].keys())
                cluster_sizes = list(data['cluster_sizes'].values())
                
                ax.bar(cluster_names, cluster_sizes, color='lightcoral')
                ax.set_title('聚类大小分布')
                ax.set_ylabel('样本数量')
                ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.error(f"聚类仪表板绘制失败: {e}")
    
    def _plot_features_dashboard(self, fig, data: Dict[str, Any], plot_index: int) -> None:
        """绘制特征仪表板"""
        try:
            ax = fig.add_subplot(2, 3, plot_index)
            
            if 'feature_importance' in data:
                feature_names = list(data['feature_importance'].keys())
                importance_scores = list(data['feature_importance'].values())
                
                # 选择前10个特征
                if len(feature_names) > 10:
                    indices = np.argsort(importance_scores)[-10:]
                    feature_names = [feature_names[i] for i in indices]
                    importance_scores = [importance_scores[i] for i in indices]
                
                ax.barh(feature_names, importance_scores, color='lightblue')
                ax.set_title('特征重要性')
                ax.set_xlabel('重要性分数')
            
        except Exception as e:
            logger.error(f"特征仪表板绘制失败: {e}")
    
    def _plot_statistics_dashboard(self, fig, data: Dict[str, Any], plot_index: int) -> None:
        """绘制统计仪表板"""
        try:
            ax = fig.add_subplot(2, 3, plot_index)
            
            if 'metrics' in data:
                metric_names = list(data['metrics'].keys())
                metric_values = list(data['metrics'].values())
                
                ax.bar(metric_names, metric_values, color='lightgreen')
                ax.set_title('性能指标')
                ax.set_ylabel('分数')
                ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.error(f"统计仪表板绘制失败: {e}")
    
    def save_plot(self, save_path: str, dpi: int = 300) -> None:
        """
        保存当前图形
        
        Args:
            save_path: 保存路径
            dpi: 分辨率
        """
        try:
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
            logger.info(f"图形保存到: {save_path}")
            
        except Exception as e:
            logger.error(f"图形保存失败: {e}")
            raise
    
    def clear_plot(self) -> None:
        """清除当前图形"""
        try:
            plt.clf()
            plt.close('all')
            
        except Exception as e:
            logger.error(f"图形清除失败: {e}")
            raise 