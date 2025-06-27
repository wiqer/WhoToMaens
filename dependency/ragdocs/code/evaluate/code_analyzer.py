import ast
import os
from typing import List, Dict, Any
import re
from dataclasses import dataclass
from enum import Enum
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IssueLevel(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    BLUE = "BLUE"

@dataclass
class Issue:
    level: IssueLevel
    message: str
    file: str
    line: int
    code: str

class CodeAnalyzer:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.issues: List[Issue] = []
        
    def analyze(self):
        """分析目标目录下的所有Python文件"""
        logger.info(f"开始分析目录: {self.target_dir}")
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    logger.info(f"分析文件: {file_path}")
                    self._analyze_file(file_path)
    
    def _analyze_file(self, file_path: str):
        """分析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            self._check_memory_management(tree, file_path, content)
            self._check_error_handling(tree, file_path, content)
            self._check_concurrency(tree, file_path, content)
            self._check_code_structure(tree, file_path, content)
            self._check_performance(tree, file_path, content)
            self._check_maintainability(tree, file_path, content)
            self._check_security(tree, file_path, content)
        except SyntaxError as e:
            self.issues.append(Issue(
                level=IssueLevel.RED,
                message=f"语法错误: {str(e)}",
                file=file_path,
                line=e.lineno,
                code=""
            ))
        except Exception as e:
            logger.error(f"分析文件 {file_path} 时发生错误: {str(e)}")
    
    def _check_memory_management(self, tree: ast.AST, file_path: str, content: str):
        """检查内存管理问题"""
        # 检查LLM模型加载
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'LLM':
                    self.issues.append(Issue(
                        level=IssueLevel.RED,
                        message="LLM模型加载没有内存限制",
                        file=file_path,
                        line=node.lineno,
                        code=ast.unparse(node)
                    ))
        
        # 检查批量处理
        batch_pattern = r'batch_size\s*=\s*\d+'
        if re.search(batch_pattern, content):
            self.issues.append(Issue(
                level=IssueLevel.RED,
                message="固定批量大小没有考虑内存限制",
                file=file_path,
                line=0,
                code=""
            ))
    
    def _check_error_handling(self, tree: ast.AST, file_path: str, content: str):
        """检查错误处理"""
        # 检查异常处理
        has_try_except = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_try_except = True
                break
        
        if not has_try_except:
            self.issues.append(Issue(
                level=IssueLevel.RED,
                message="缺少错误处理",
                file=file_path,
                line=0,
                code=""
            ))
    
    def _check_concurrency(self, tree: ast.AST, file_path: str, content: str):
        """检查并发安全问题"""
        # 检查异步操作
        has_async = False
        has_lock = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                has_async = True
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'Lock':
                    has_lock = True
        
        if has_async and not has_lock:
            self.issues.append(Issue(
                level=IssueLevel.RED,
                message="异步操作缺少同步保护",
                file=file_path,
                line=0,
                code=""
            ))
    
    def _check_code_structure(self, tree: ast.AST, file_path: str, content: str):
        """检查代码结构问题"""
        # 检查类继承
        has_base_class = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.bases:
                    has_base_class = True
                    break
        
        if not has_base_class:
            self.issues.append(Issue(
                level=IssueLevel.YELLOW,
                message="类缺少基类或接口",
                file=file_path,
                line=0,
                code=""
            ))
    
    def _check_performance(self, tree: ast.AST, file_path: str, content: str):
        """检查性能问题"""
        # 检查循环中的重复计算
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == 'sorted':
                            self.issues.append(Issue(
                                level=IssueLevel.YELLOW,
                                message="循环中存在重复排序",
                                file=file_path,
                                line=child.lineno,
                                code=ast.unparse(child)
                            ))
    
    def _check_maintainability(self, tree: ast.AST, file_path: str, content: str):
        """检查可维护性问题"""
        # 检查文档字符串
        has_docstring = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                if ast.get_docstring(node):
                    has_docstring = True
                    break
        
        if not has_docstring:
            self.issues.append(Issue(
                level=IssueLevel.YELLOW,
                message="缺少文档字符串",
                file=file_path,
                line=0,
                code=""
            ))
    
    def _check_security(self, tree: ast.AST, file_path: str, content: str):
        """检查安全问题"""
        # 检查文件操作
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    self.issues.append(Issue(
                        level=IssueLevel.RED,
                        message="文件操作缺少安全检查",
                        file=file_path,
                        line=node.lineno,
                        code=ast.unparse(node)
                    ))
    
    def get_report(self) -> Dict[str, List[Issue]]:
        """生成分析报告"""
        report = {
            IssueLevel.RED.value: [],
            IssueLevel.YELLOW.value: [],
            IssueLevel.BLUE.value: []
        }
        
        for issue in self.issues:
            report[issue.level.value].append(issue)
        
        return report

def main():
    try:
        analyzer = CodeAnalyzer("bugagaric/evaluate")
        analyzer.analyze()
        report = analyzer.get_report()
        
        print("\n=== 代码分析报告 ===")
        for level in [IssueLevel.RED, IssueLevel.YELLOW, IssueLevel.BLUE]:
            print(f"\n{level.value} 级别问题:")
            for issue in report[level.value]:
                print(f"\n文件: {issue.file}")
                print(f"行号: {issue.line}")
                print(f"问题: {issue.message}")
                if issue.code:
                    print(f"代码: {issue.code}")
        
        # 保存报告到文件
        with open("docs/code/evaluate/analysis_report.txt", "w", encoding="utf-8") as f:
            f.write("=== 代码分析报告 ===\n")
            for level in [IssueLevel.RED, IssueLevel.YELLOW, IssueLevel.BLUE]:
                f.write(f"\n{level.value} 级别问题:\n")
                for issue in report[level.value]:
                    f.write(f"\n文件: {issue.file}\n")
                    f.write(f"行号: {issue.line}\n")
                    f.write(f"问题: {issue.message}\n")
                    if issue.code:
                        f.write(f"代码: {issue.code}\n")
        
        logger.info("分析完成，报告已保存到 docs/code/evaluate/analysis_report.txt")
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main() 