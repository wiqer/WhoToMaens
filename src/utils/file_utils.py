"""
文件工具模块

包含文件操作的辅助工具函数。
"""

import os
import json
import yaml
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_dir(directory: Union[str, Path]) -> Path:
        """
        确保目录存在
        
        Args:
            directory: 目录路径
            
        Returns:
            目录路径对象
        """
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            return dir_path
            
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            raise
    
    @staticmethod
    def save_json(data: Any, file_path: Union[str, Path], 
                  indent: int = 2, ensure_ascii: bool = False) -> None:
        """
        保存JSON文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: 缩进
            ensure_ascii: 是否确保ASCII编码
        """
        try:
            file_path = Path(file_path)
            FileUtils.ensure_dir(file_path.parent)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
            
            logger.info(f"JSON文件保存成功: {file_path}")
            
        except Exception as e:
            logger.error(f"JSON文件保存失败: {e}")
            raise
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Any:
        """
        加载JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"JSON文件加载成功: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"JSON文件加载失败: {e}")
            raise
    
    @staticmethod
    def save_yaml(data: Any, file_path: Union[str, Path]) -> None:
        """
        保存YAML文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        try:
            file_path = Path(file_path)
            FileUtils.ensure_dir(file_path.parent)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"YAML文件保存成功: {file_path}")
            
        except Exception as e:
            logger.error(f"YAML文件保存失败: {e}")
            raise
    
    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Any:
        """
        加载YAML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            logger.info(f"YAML文件加载成功: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"YAML文件加载失败: {e}")
            raise
    
    @staticmethod
    def save_pickle(data: Any, file_path: Union[str, Path]) -> None:
        """
        保存Pickle文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        try:
            file_path = Path(file_path)
            FileUtils.ensure_dir(file_path.parent)
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Pickle文件保存成功: {file_path}")
            
        except Exception as e:
            logger.error(f"Pickle文件保存失败: {e}")
            raise
    
    @staticmethod
    def load_pickle(file_path: Union[str, Path]) -> Any:
        """
        加载Pickle文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"Pickle文件加载成功: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Pickle文件加载失败: {e}")
            raise
    
    @staticmethod
    def get_file_extension(file_path: Union[str, Path]) -> str:
        """
        获取文件扩展名
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件扩展名
        """
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（字节）
        """
        try:
            return Path(file_path).stat().st_size
            
        except Exception as e:
            logger.error(f"获取文件大小失败: {e}")
            return 0
    
    @staticmethod
    def list_files(directory: Union[str, Path], 
                   pattern: str = "*",
                   recursive: bool = False) -> List[Path]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件模式
            recursive: 是否递归搜索
            
        Returns:
            文件路径列表
        """
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return []
            
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            # 只返回文件，不返回目录
            return [f for f in files if f.is_file()]
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    @staticmethod
    def copy_file(src_path: Union[str, Path], 
                  dst_path: Union[str, Path]) -> None:
        """
        复制文件
        
        Args:
            src_path: 源文件路径
            dst_path: 目标文件路径
        """
        try:
            src_path = Path(src_path)
            dst_path = Path(dst_path)
            
            if not src_path.exists():
                raise FileNotFoundError(f"源文件不存在: {src_path}")
            
            FileUtils.ensure_dir(dst_path.parent)
            
            import shutil
            shutil.copy2(src_path, dst_path)
            
            logger.info(f"文件复制成功: {src_path} -> {dst_path}")
            
        except Exception as e:
            logger.error(f"文件复制失败: {e}")
            raise
    
    @staticmethod
    def delete_file(file_path: Union[str, Path]) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            file_path = Path(file_path)
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件删除成功: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            stat = file_path.stat()
            
            info = {
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix,
                'size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'exists': file_path.exists()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            raise 