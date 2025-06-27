import ast
import re
from typing import List, Dict, Set
import os
from dataclasses import dataclass
from enum import Enum

class IssueLevel(Enum):
    RED = "🔴"
    YELLOW = "🟡"
    BLUE = "🔵"

@dataclass
class Issue:
    level: IssueLevel
    message: str
    line: int
    file: str

class ServerCodeAnalyzer:
    def __init__(self):
        self.issues: List[Issue] = []
        self.imported_modules: Set[str] = set()
        
    def analyze_file(self, file_path: str) -> List[Issue]:
        """分析单个文件的问题"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        # 重置状态
        self.issues = []
        self.imported_modules = set()
        
        # 收集导入的模块
        self._collect_imports(tree)
        
        # 执行各种检查
        self._check_security_issues(tree, file_path)
        self._check_error_handling(tree, file_path)
        self._check_performance_issues(tree, file_path)
        self._check_code_quality(tree, file_path)
        
        return self.issues
    
    def _collect_imports(self, tree: ast.AST):
        """收集所有导入的模块"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.imported_modules.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imported_modules.add(node.module)
    
    def _check_security_issues(self, tree: ast.AST, file_path: str):
        """检查安全性问题"""
        for node in ast.walk(tree):
            # 检查文件上传
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['save', 'open']:
                        self.issues.append(Issue(
                            level=IssueLevel.RED,
                            message="文件操作缺少安全检查",
                            line=node.lineno,
                            file=file_path
                        ))
            
            # 检查环境变量使用
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'getenv':
                        self.issues.append(Issue(
                            level=IssueLevel.RED,
                            message="环境变量使用缺少默认值",
                            line=node.lineno,
                            file=file_path
                        ))
    
    def _check_error_handling(self, tree: ast.AST, file_path: str):
        """检查错误处理"""
        for node in ast.walk(tree):
            # 检查异常处理
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['get', 'post', 'put', 'delete']:
                        if not self._has_try_except(node):
                            self.issues.append(Issue(
                                level=IssueLevel.RED,
                                message="API请求缺少异常处理",
                                line=node.lineno,
                                file=file_path
                            ))
            
            # 检查数据库操作
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'commit']:
                        if not self._has_try_except(node):
                            self.issues.append(Issue(
                                level=IssueLevel.RED,
                                message="数据库操作缺少异常处理",
                                line=node.lineno,
                                file=file_path
                            ))
    
    def _check_performance_issues(self, tree: ast.AST, file_path: str):
        """检查性能问题"""
        for node in ast.walk(tree):
            # 检查资源管理
            if isinstance(node, ast.With):
                if not self._has_resource_cleanup(node):
                    self.issues.append(Issue(
                        level=IssueLevel.YELLOW,
                        message="资源管理不完善",
                        line=node.lineno,
                        file=file_path
                    ))
            
            # 检查图片处理
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'Image.open':
                        self.issues.append(Issue(
                            level=IssueLevel.YELLOW,
                            message="图片处理缺少大小限制",
                            line=node.lineno,
                            file=file_path
                        ))
    
    def _check_code_quality(self, tree: ast.AST, file_path: str):
        """检查代码质量问题"""
        for node in ast.walk(tree):
            # 检查配置管理
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name):
                    if node.targets[0].id.isupper():
                        self.issues.append(Issue(
                            level=IssueLevel.YELLOW,
                            message="配置应该移到配置文件中",
                            line=node.lineno,
                            file=file_path
                        ))
            
            # 检查日志记录
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['info', 'error', 'warning']:
                        if not self._has_structured_logging(node):
                            self.issues.append(Issue(
                                level=IssueLevel.YELLOW,
                                message="日志记录不够结构化",
                                line=node.lineno,
                                file=file_path
                            ))
    
    def _has_try_except(self, node: ast.AST) -> bool:
        """检查节点是否在try-except块中"""
        current = node
        while hasattr(current, 'parent'):
            if isinstance(current.parent, ast.Try):
                return True
            current = current.parent
        return False
    
    def _has_resource_cleanup(self, node: ast.AST) -> bool:
        """检查是否有资源清理"""
        return any(isinstance(child, ast.Call) for child in ast.walk(node))
    
    def _has_structured_logging(self, node: ast.AST) -> bool:
        """检查是否是结构化日志"""
        if not isinstance(node, ast.Call):
            return False
        if not isinstance(node.func, ast.Attribute):
            return False
        if not node.args:
            return False
        return isinstance(node.args[0], ast.Dict)

def analyze_directory(directory: str) -> Dict[str, List[Issue]]:
    """分析整个目录的代码问题"""
    analyzer = ServerCodeAnalyzer()
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                issues = analyzer.analyze_file(file_path)
                if issues:
                    results[file_path] = issues
    
    return results

def print_report(results: Dict[str, List[Issue]]):
    """打印分析报告"""
    print("# 服务器代码分析报告\n")
    
    # 按问题级别统计
    level_counts = {level: 0 for level in IssueLevel}
    
    for file_path, issues in results.items():
        print(f"\n## {os.path.basename(file_path)}\n")
        
        # 按问题级别分组
        issues_by_level = {level: [] for level in IssueLevel}
        for issue in issues:
            issues_by_level[issue.level].append(issue)
            level_counts[issue.level] += 1
        
        # 打印每个级别的问题
        for level in IssueLevel:
            if issues_by_level[level]:
                print(f"\n### {level.value} {level.name} 级别问题\n")
                for issue in issues_by_level[level]:
                    print(f"- 第 {issue.line} 行: {issue.message}")
    
    # 打印统计信息
    print("\n## 统计信息\n")
    for level, count in level_counts.items():
        print(f"- {level.value} {level.name} 级别问题: {count} 个")

def main():
    # 使用示例
    directory = "bugagaric/server"
    results = analyze_directory(directory)
    print_report(results)

if __name__ == '__main__':
    main() 