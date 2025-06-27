# Server模块修复计划

## 一、编译错误修复

### 1.1 auth_server.py 修复
```python
# bugagaric/server/auth_server.py
from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from bugagaric.modules.database.postgresql import PostgreSQLIndex
import bcrypt
import os
import psycopg2
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import secrets
import logging
from pydantic import BaseModel, ValidationError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)

# 配置限流
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# 从环境变量获取密钥
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
if not os.getenv('JWT_SECRET_KEY'):
    logger.warning("使用临时JWT密钥，生产环境请设置JWT_SECRET_KEY环境变量")

# 数据库配置
app.config['POSTGRES_CONFIG'] = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'bugagaric'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

# 初始化数据库连接
pg_index = PostgreSQLIndex(**app.config['POSTGRES_CONFIG'])

# 请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 路由处理
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = LoginRequest(**request.json)
        username = data.username
        password = data.password
    except ValidationError as e:
        return jsonify({"error": "输入验证失败", "details": e.errors()}), 400

    try:
        # 查询用户
        with pg_index.conn.cursor() as cur:
            cur.execute("SELECT id, password_hash, hf_token FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if not user:
            return jsonify({"error": "用户不存在"}), 401

        # 验证密码
        if not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return jsonify({"error": "密码错误"}), 401

        # 生成JWT令牌
        token = jwt.encode({
            "user_id": user[0],
            "exp": datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "token": token,
            "hf_token": user[2]
        })
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500
```

### 1.2 run_server_hf_llm.py 修复
```python
# bugagaric/server/run_server_hf_llm.py
import json
import argparse
import traceback
import urllib.parse
from PIL import Image
from pathlib import Path
from loguru import logger
from flask import Flask, request, Response, stream_with_context, jsonify
from bugagaric.modules.llm.huggingface_like import HuggingFaceServer
import jwt
from functools import wraps
import os

class MicroServer:
    def __init__(self, model_path: str, device: str):
        if not Path(model_path).exists():
            raise ValueError(f"model path: {model_path} not exist!")
        
        self.llm = HuggingFaceServer(model_path=model_path, device=device)
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
        
        # 注册路由
        self.app.add_url_rule('/chat', view_func=self.process, methods=['GET', 'POST'])

    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(' ')[1]
            if not token:
                return jsonify({'error': '认证令牌缺失'}), 401
            try:
                data = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = data['user_id']
            except:
                return jsonify({'error': '无效的令牌'}), 401
            return f(current_user, *args, **kwargs)
        return decorated

    @token_required
    def process(self, current_user):
        try:
            # 解析请求数据
            data = json.loads(request.form.get("data", "{}"))
            messages = data.get('messages', [])
            stream = data.get('stream', False)
            
            # 处理图片文件
            name2img = {}
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
            ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

            for item in request.files.values():
                if item.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': f'文件 {item.filename} 超过最大限制 {MAX_FILE_SIZE} bytes'}), 413
                if item.content_type not in ALLOWED_MIME_TYPES:
                    return jsonify({'error': f'不支持的文件类型: {item.content_type}'}), 415
                if "image" not in item.content_type:
                    continue
                key = urllib.parse.unquote(item.filename)
                name2img[key] = Image.open(item)

            logger.info(f"images files: {[n for n in name2img.keys()]}")
            
            # 处理消息
            if name2img:
                img_messages = []
                for msg in messages:
                    role, content = msg["role"], msg['content']
                    new_content = [name2img.get(item, item) for item in content]
                    img_messages.append(dict(role=role, content=new_content))
            else:
                img_messages = messages

            logger.info(f"messages: {img_messages}")
            resp = self.llm.run(messages=img_messages, stream=stream)
            
            if stream:
                return Response(stream_with_context(resp), mimetype='text/event-stream')
            else:
                return resp
                
        except Exception as e:
            logger.error(f'处理请求失败: {traceback.format_exc()}')
            return jsonify({'error': '服务器内部错误'}), 500

    def run_server(self, host: str, port: int):
        try:
            self.app.run(host=host, port=port)
        except Exception as e:
            logger.error(f'服务器启动失败: {traceback.format_exc()}')
            raise
```

## 二、依赖管理

### 2.1 requirements.txt 更新
```txt
# 基础依赖
flask>=2.0.0
flask-limiter>=2.0.0
pyjwt>=2.0.0
bcrypt>=3.2.0
psycopg2-binary>=2.9.0
pydantic>=1.8.0
python-dotenv>=0.19.0
loguru>=0.5.0
pillow>=8.0.0

# 开发依赖
pytest>=6.0.0
pytest-asyncio>=0.15.0
pytest-cov>=2.12.0
black>=21.5b2
flake8>=3.9.0
mypy>=0.910
```

## 三、配置管理

### 3.1 环境变量配置
```bash
# .env
JWT_SECRET_KEY=your-secret-key
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bugagaric
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

### 3.2 配置文件
```python
# config/server_config.py
from pydantic import BaseSettings

class ServerSettings(BaseSettings):
    JWT_SECRET_KEY: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "bugagaric"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
```

## 四、测试用例

### 4.1 单元测试
```python
# tests/test_auth_server.py
import pytest
from bugagaric.server.auth_server import app, LoginRequest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    response = client.post('/login', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        'username': 'wrong_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 401
```

### 4.2 集成测试
```python
# tests/test_integration.py
import pytest
from bugagaric.server.run_server_hf_llm import MicroServer

@pytest.fixture
def server():
    return MicroServer(
        model_path="path/to/model",
        device="cpu"
    )

def test_chat_endpoint(server):
    response = server.process({
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'stream': False
    })
    assert response.status_code == 200
```

## 五、部署脚本

### 5.1 启动脚本
```python
# scripts/start_server.py
import os
from dotenv import load_dotenv
from bugagaric.server.auth_server import app
from bugagaric.server.run_server_hf_llm import MicroServer

def start_servers():
    # 加载环境变量
    load_dotenv()
    
    # 启动认证服务器
    auth_host = os.getenv('AUTH_HOST', '0.0.0.0')
    auth_port = int(os.getenv('AUTH_PORT', 5000))
    
    # 启动LLM服务器
    llm_host = os.getenv('LLM_HOST', '0.0.0.0')
    llm_port = int(os.getenv('LLM_PORT', 5001))
    model_path = os.getenv('MODEL_PATH')
    device = os.getenv('DEVICE', 'cpu')
    
    llm_server = MicroServer(model_path=model_path, device=device)
    
    # 启动服务器
    app.run(host=auth_host, port=auth_port)
    llm_server.run_server(host=llm_host, port=llm_port)

if __name__ == "__main__":
    start_servers()
```

## 六、监控方案

### 6.1 日志配置
```python
# bugagaric/server/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger
```

### 6.2 性能监控
```python
# bugagaric/server/monitor.py
import psutil
import time
from .logger import setup_logger

logger = setup_logger('server_monitor', 'logs/server.log')

def monitor_resources():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        logger.info(f"CPU Usage: {cpu_percent}%")
        logger.info(f"Memory Usage: {memory.percent}%")
        
        if cpu_percent > 80 or memory.percent > 80:
            logger.warning("High resource usage detected!")
        
        time.sleep(60)  # 每分钟检查一次
```

## 七、回滚方案

### 7.1 代码回滚
```bash
#!/bin/bash
# scripts/rollback.sh

# 回滚到指定版本
VERSION=$1
git checkout $VERSION

# 恢复环境变量
cp .env.backup .env

# 重启服务
python scripts/restart_server.py
```

### 7.2 数据回滚
```python
# scripts/restore_data.py
import json
import shutil
from pathlib import Path

def restore_data(backup_dir: str, target_dir: str):
    """恢复数据"""
    backup_path = Path(backup_dir)
    target_path = Path(target_dir)
    
    # 恢复文件
    shutil.copytree(backup_path, target_path, dirs_exist_ok=True)
    
    # 恢复配置
    with open(backup_path / "config.json") as f:
        config = json.load(f)
    with open(target_path / "config.json", "w") as f:
        json.dump(config, f, indent=2)
``` 