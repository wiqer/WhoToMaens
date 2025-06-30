"""
配置工具模块

包含日志设置、配置加载等工具函数。
"""

import logging
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


def setup_logging(level: str = "INFO", 
                 log_file: Optional[str] = None,
                 log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s") -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        log_format: 日志格式
    """
    # 设置日志级别
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"无效的日志级别: {level}")
    
    # 配置根日志记录器
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[]
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)
    
    # 添加文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    
    logging.info(f"日志配置完成，级别: {level}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    config = {}
    
    # 默认配置文件路径
    if config_path is None:
        config_path = "config.yaml"
    
    config_file = Path(config_path)
    
    if config_file.exists():
        try:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            elif config_file.suffix.lower() == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
            
            logging.info(f"配置文件加载成功: {config_path}")
            
        except Exception as e:
            logging.warning(f"配置文件加载失败: {e}")
            config = {}
    else:
        logging.info(f"配置文件不存在: {config_path}，使用默认配置")
    
    # 合并环境变量配置
    config = merge_env_config(config)
    
    return config


def merge_env_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并环境变量配置
    
    Args:
        config: 原始配置
        
    Returns:
        合并后的配置
    """
    # 环境变量前缀
    env_prefix = "WHOTOMAENS_"
    
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # 移除前缀并转换为小写
            config_key = key[len(env_prefix):].lower()
            
            # 尝试转换值类型
            try:
                # 尝试转换为整数
                if value.isdigit():
                    config[config_key] = int(value)
                # 尝试转换为浮点数
                elif value.replace('.', '').isdigit():
                    config[config_key] = float(value)
                # 尝试转换为布尔值
                elif value.lower() in ['true', 'false']:
                    config[config_key] = value.lower() == 'true'
                else:
                    config[config_key] = value
            except:
                config[config_key] = value
    
    return config


def save_config(config: Dict[str, Any], config_path: str, format: str = "yaml") -> None:
    """
    保存配置文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
        format: 文件格式 (yaml 或 json)
    """
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "yaml":
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format.lower() == "json":
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的文件格式: {format}")
        
        logging.info(f"配置文件保存成功: {config_path}")
        
    except Exception as e:
        logging.error(f"配置文件保存失败: {e}")
        raise


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        默认配置字典
    """
    return {
        # 模型配置
        "models": {
            "clip_model": "openai/clip-vit-base-patch32",
            "imagebert_model": "microsoft/imagebert-base",
            "blip_model": "Salesforce/blip-image-captioning-base",
            "device": "auto"  # auto, cpu, cuda
        },
        
        # 特征提取配置
        "feature_extraction": {
            "target_size": [224, 224],
            "normalize": True,
            "use_augmentation": False
        },
        
        # 聚类配置
        "clustering": {
            "default_method": "auto",
            "max_clusters": 10,
            "min_cluster_size": 5,
            "eps": 0.5
        },
        
        # 热点检测配置
        "hotspot_detection": {
            "min_area": 100,
            "padding": 10,
            "confidence_threshold": 0.5
        },
        
        # API配置
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False,
            "cors_origins": ["*"]
        },
        
        # 存储配置
        "storage": {
            "output_dir": "output",
            "cache_dir": "cache",
            "temp_dir": "temp"
        },
        
        # 日志配置
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": None
        }
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置
    
    Args:
        config: 配置字典
        
    Returns:
        是否有效
    """
    try:
        # 检查必需的配置项
        required_keys = ["models", "feature_extraction", "clustering"]
        
        for key in required_keys:
            if key not in config:
                logging.error(f"缺少必需的配置项: {key}")
                return False
        
        # 验证模型配置
        models_config = config.get("models", {})
        if "clip_model" not in models_config:
            logging.warning("未指定CLIP模型")
        
        # 验证特征提取配置
        feature_config = config.get("feature_extraction", {})
        if "target_size" not in feature_config:
            logging.warning("未指定目标尺寸")
        
        # 验证聚类配置
        clustering_config = config.get("clustering", {})
        if "default_method" not in clustering_config:
            logging.warning("未指定默认聚类方法")
        
        logging.info("配置验证通过")
        return True
        
    except Exception as e:
        logging.error(f"配置验证失败: {e}")
        return False 