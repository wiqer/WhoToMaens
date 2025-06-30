#!/usr/bin/env python3
"""
WhoToMaens 主程序入口

多功能融合图片BERT分析系统
"""

import argparse
import logging
import sys
import numpy as np
from pathlib import Path
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api import FastAPIApp
from src.core import ImageProcessor, FeatureExtractor, ClusterAnalyzer, HotspotDetector, ContentAnalyzer
from src.utils import setup_logging, load_config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="WhoToMaens - 多功能融合图片BERT分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 启动FastAPI服务
  python main.py --api fastapi --port 8000
  
  # 分析单张图片
  python main.py --analyze-image path/to/image.jpg
  
  # 批量分析图片
  python main.py --analyze-batch path/to/image/directory
        """
    )
    
    # API相关参数
    parser.add_argument(
        "--api", 
        choices=["fastapi"], 
        default="fastapi",
        help="选择API类型 (默认: fastapi)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="端口号 (默认: 8000)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="开启调试模式"
    )
    
    # 分析相关参数
    parser.add_argument(
        "--analyze-image",
        type=str,
        help="分析单张图片"
    )
    parser.add_argument(
        "--analyze-batch",
        type=str,
        help="批量分析图片目录"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="输出目录 (默认: output)"
    )
    
    # 配置相关参数
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(level=args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        config = load_config(args.config) if args.config else {}
        
        # 根据参数执行不同的操作
        if args.analyze_image:
            # 分析单张图片
            analyze_single_image(args.analyze_image, args.output_dir, config)
            
        elif args.analyze_batch:
            # 批量分析图片
            analyze_batch_images(args.analyze_batch, args.output_dir, config)
            
        else:
            # 启动API服务
            if args.api == "fastapi":
                start_fastapi_server(args.host, args.port, args.debug, config)
                
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


def analyze_single_image(image_path: str, output_dir: str, config: dict):
    """分析单张图片"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"开始分析图片: {image_path}")
        
        # 初始化组件
        image_processor = ImageProcessor(config)
        feature_extractor = FeatureExtractor(config)
        hotspot_detector = HotspotDetector(config)
        content_analyzer = ContentAnalyzer(config)
        
        # 加载图片
        image = image_processor.load_image(image_path)
        
        # 提取特征
        logger.info("提取图片特征...")
        features = feature_extractor.extract_all_features(image)
        
        # 检测热点
        logger.info("检测热点区域...")
        hotspots = hotspot_detector.detect_all_hotspots(image)
        
        # 分析内容
        logger.info("分析图片内容...")
        content_analysis = content_analyzer.analyze_content(image)
        
        # 生成结构化描述
        structured_description = content_analyzer.generate_structured_description(image)
        
        # 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存分析结果
        import json
        result = {
            "image_path": image_path,
            "features": {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in features.items()},
            "hotspots": {k: [{kk: vv for kk, vv in item.items() if kk != 'sub_image'} 
                           for item in v] for k, v in hotspots.items()},
            "content_analysis": content_analysis,
            "structured_description": structured_description
        }
        
        result_file = output_path / f"{Path(image_path).stem}_analysis.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存热点可视化
        vis_image = hotspot_detector.visualize_hotspots(image, hotspots)
        vis_file = output_path / f"{Path(image_path).stem}_hotspots.jpg"
        image_processor.save_image(vis_image, vis_file)
        
        logger.info(f"分析完成，结果保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"图片分析失败: {e}")
        raise


def analyze_batch_images(image_dir: str, output_dir: str, config: dict):
    """批量分析图片"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"开始批量分析图片目录: {image_dir}")
        
        # 初始化组件
        image_processor = ImageProcessor(config)
        feature_extractor = FeatureExtractor(config)
        cluster_analyzer = ClusterAnalyzer(config)
        
        # 获取所有图片文件
        image_dir_path = Path(image_dir)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = [f for f in image_dir_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not image_files:
            logger.warning(f"在目录 {image_dir} 中没有找到图片文件")
            return
        
        logger.info(f"找到 {len(image_files)} 张图片")
        
        # 提取所有图片的特征
        all_features = []
        image_info = []
        
        for i, image_file in enumerate(image_files):
            try:
                logger.info(f"处理图片 {i+1}/{len(image_files)}: {image_file.name}")
                
                # 加载图片
                image = image_processor.load_image(image_file)
                
                # 提取特征
                features = feature_extractor.extract_all_features(image)
                
                # 合并特征
                combined_features = []
                for feature_name, feature_value in features.items():
                    if isinstance(feature_value, np.ndarray):
                        combined_features.extend(feature_value.flatten())
                    else:
                        combined_features.append(feature_value)
                
                all_features.append(combined_features)
                image_info.append({
                    "index": i,
                    "filename": image_file.name,
                    "path": str(image_file)
                })
                
            except Exception as e:
                logger.error(f"处理图片 {image_file.name} 失败: {e}")
                continue
        
        if not all_features:
            logger.error("没有成功提取到任何特征")
            return
        
        # 聚类分析
        logger.info("进行聚类分析...")
        feature_matrix = np.array(all_features)
        cluster_labels, params = cluster_analyzer.auto_clustering(feature_matrix)
        
        # 分析聚类结果
        analysis = cluster_analyzer.analyze_clusters(feature_matrix, cluster_labels)
        
        # 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存聚类结果
        import json
        cluster_result = {
            "n_images": len(image_files),
            "cluster_params": params,
            "analysis": analysis,
            "images": [
                {**info, "cluster_label": int(cluster_labels[i])}
                for i, info in enumerate(image_info)
            ]
        }
        
        cluster_file = output_path / "batch_clustering_result.json"
        with open(cluster_file, 'w', encoding='utf-8') as f:
            json.dump(cluster_result, f, ensure_ascii=False, indent=2)
        
        # 可视化聚类结果
        vis_file = output_path / "clustering_visualization.png"
        cluster_analyzer.visualize_clusters(feature_matrix, cluster_labels, vis_file)
        
        logger.info(f"批量分析完成，结果保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise


def start_fastapi_server(host: str, port: int, debug: bool, config: dict):
    """启动FastAPI服务器"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("启动FastAPI服务器...")
        app = FastAPIApp(config)
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"FastAPI服务器启动失败: {e}")
        raise


if __name__ == "__main__":
    main() 