# MaoOCR 多平台部署指南

## 📋 概述

本文档详细说明如何将MaoOCR部署到不同平台，包括手机软件、PC软件和Docker容器部署。

## 📱 手机软件部署

### 1. 移动端架构设计

#### 技术栈选择
- **前端框架**: React Native / Flutter
- **后端服务**: FastAPI + vLLM
- **图像处理**: OpenCV Mobile
- **模型部署**: TensorFlow Lite / ONNX Runtime Mobile

#### 架构设计
```
移动端架构
├── 前端层 (Frontend)
│   ├── 图像采集
│   ├── 用户界面
│   └── 结果展示
├── 通信层 (Communication)
│   ├── HTTP API
│   ├── WebSocket
│   └── 离线模式
├── 后端层 (Backend)
│   ├── OCR服务
│   ├── 模型管理
│   └── 结果处理
└── 存储层 (Storage)
    ├── 本地缓存
    ├── 云端存储
    └── 历史记录
```

### 2. React Native 实现

#### 项目结构
```
maoocr-mobile/
├── src/
│   ├── components/          # UI组件
│   ├── screens/            # 页面
│   ├── services/           # API服务
│   ├── utils/              # 工具函数
│   └── navigation/         # 导航
├── android/                # Android配置
├── ios/                    # iOS配置
└── package.json
```

#### 核心组件实现

##### 图像采集组件
```javascript
// src/components/ImageCapture.js
import React, { useState } from 'react';
import { View, TouchableOpacity, Image, Text } from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';

const ImageCapture = ({ onImageSelected }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const takePhoto = async () => {
    const result = await launchCamera({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setSelectedImage(result.assets[0]);
      onImageSelected(result.assets[0]);
    }
  };

  const selectFromGallery = async () => {
    const result = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
    });

    if (result.assets && result.assets[0]) {
      setSelectedImage(result.assets[0]);
      onImageSelected(result.assets[0]);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.button} onPress={takePhoto}>
        <Text>拍照</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={selectFromGallery}>
        <Text>选择图片</Text>
      </TouchableOpacity>
      {selectedImage && (
        <Image source={{ uri: selectedImage.uri }} style={styles.preview} />
      )}
    </View>
  );
};
```

##### OCR服务调用
```javascript
// src/services/OCRService.js
import axios from 'axios';

class OCRService {
  constructor(baseURL) {
    this.api = axios.create({
      baseURL,
      timeout: 30000,
    });
  }

  async recognizeImage(imageFile) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageFile.uri,
      type: 'image/jpeg',
      name: 'image.jpg',
    });

    try {
      const response = await this.api.post('/api/ocr/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw new Error(`OCR识别失败: ${error.message}`);
    }
  }

  async recognizeWithRequirements(imageFile, requirements) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageFile.uri,
      type: 'image/jpeg',
      name: 'image.jpg',
    });
    formData.append('requirements', JSON.stringify(requirements));

    try {
      const response = await this.api.post('/api/ocr/recognize-with-requirements', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw new Error(`OCR识别失败: ${error.message}`);
    }
  }
}

export default OCRService;
```

##### 主页面实现
```javascript
// src/screens/OCRScreen.js
import React, { useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView } from 'react-native';
import ImageCapture from '../components/ImageCapture';
import OCRService from '../services/OCRService';

const OCRScreen = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const ocrService = new OCRService('http://your-server:8000');

  const handleImageSelected = async (imageFile) => {
    setLoading(true);
    setError(null);

    try {
      // 定义任务需求
      const requirements = {
        document_type: 'auto',
        language: 'auto',
        accuracy_requirement: 'high',
        speed_requirement: 'medium',
        real_time: false,
        batch_processing: false,
      };

      const ocrResult = await ocrService.recognizeWithRequirements(imageFile, requirements);
      setResult(ocrResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>MaoOCR 智能识别</Text>
      
      <ImageCapture onImageSelected={handleImageSelected} />
      
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text>正在识别中...</Text>
        </View>
      )}
      
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      
      {result && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>识别结果:</Text>
          <Text style={styles.resultText}>{result.text}</Text>
          <Text style={styles.confidenceText}>
            置信度: {(result.confidence * 100).toFixed(2)}%
          </Text>
          <Text style={styles.timeText}>
            处理时间: {result.processing_time.toFixed(2)}秒
          </Text>
        </View>
      )}
    </ScrollView>
  );
};
```

### 3. Flutter 实现

#### 项目结构
```
maoocr_flutter/
├── lib/
│   ├── main.dart
│   ├── screens/
│   ├── widgets/
│   ├── services/
│   └── models/
├── android/
├── ios/
└── pubspec.yaml
```

#### 核心实现
```dart
// lib/services/ocr_service.dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class OCRService {
  final String baseURL;
  
  OCRService(this.baseURL);
  
  Future<OCRResult> recognizeImage(File imageFile, Map<String, dynamic> requirements) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseURL/api/ocr/recognize-with-requirements'),
      );
      
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );
      
      request.fields['requirements'] = jsonEncode(requirements);
      
      var response = await request.send();
      var responseData = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        return OCRResult.fromJson(jsonDecode(responseData));
      } else {
        throw Exception('OCR识别失败: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('网络请求失败: $e');
    }
  }
}

// lib/widgets/image_capture_widget.dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class ImageCaptureWidget extends StatefulWidget {
  final Function(File) onImageSelected;
  
  const ImageCaptureWidget({Key? key, required this.onImageSelected}) : super(key: key);
  
  @override
  _ImageCaptureWidgetState createState() => _ImageCaptureWidgetState();
}

class _ImageCaptureWidgetState extends State<ImageCaptureWidget> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  
  Future<void> _takePhoto() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera);
    if (photo != null) {
      setState(() {
        _selectedImage = File(photo.path);
      });
      widget.onImageSelected(_selectedImage!);
    }
  }
  
  Future<void> _selectFromGallery() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
      });
      widget.onImageSelected(_selectedImage!);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ElevatedButton.icon(
              onPressed: _takePhoto,
              icon: Icon(Icons.camera_alt),
              label: Text('拍照'),
            ),
            ElevatedButton.icon(
              onPressed: _selectFromGallery,
              icon: Icon(Icons.photo_library),
              label: Text('选择图片'),
            ),
          ],
        ),
        if (_selectedImage != null)
          Container(
            margin: EdgeInsets.all(16),
            child: Image.file(_selectedImage!, height: 200),
          ),
      ],
    );
  }
}
```

### 4. 离线模式支持

#### TensorFlow Lite 集成
```javascript
// src/services/OfflineOCRService.js
import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-react-native';

class OfflineOCRService {
  constructor() {
    this.model = null;
    this.isModelLoaded = false;
  }

  async loadModel() {
    try {
      // 加载TensorFlow Lite模型
      this.model = await tf.loadLayersModel('file://./assets/ocr_model.tflite');
      this.isModelLoaded = true;
    } catch (error) {
      console.error('模型加载失败:', error);
    }
  }

  async recognizeOffline(imageData) {
    if (!this.isModelLoaded) {
      throw new Error('模型未加载');
    }

    // 图像预处理
    const tensor = tf.tensor(imageData);
    const normalized = tensor.div(255.0);
    const batched = normalized.expandDims(0);

    // 模型推理
    const prediction = await this.model.predict(batched);
    const result = await prediction.array();

    // 后处理
    return this.postProcess(result[0]);
  }

  postProcess(prediction) {
    // 将模型输出转换为文本
    // 这里需要根据具体模型实现
    return {
      text: '离线识别结果',
      confidence: 0.8,
      processing_time: 0.1,
    };
  }
}
```

## 💻 PC软件部署

### 1. 桌面应用架构

#### 技术栈选择
- **框架**: Electron / PyQt / Tkinter
- **后端**: Python + FastAPI
- **前端**: HTML/CSS/JS 或 Qt Widgets
- **打包**: PyInstaller / cx_Freeze

#### 架构设计
```
桌面应用架构
├── 前端层 (Frontend)
│   ├── 主界面
│   ├── 图像预览
│   └── 结果展示
├── 后端层 (Backend)
│   ├── OCR引擎
│   ├── 模型管理
│   └── 文件处理
├── 通信层 (IPC)
│   ├── 进程间通信
│   └── 事件处理
└── 系统层 (System)
    ├── 文件系统
    ├── 系统API
    └── 硬件访问
```

### 2. Electron 实现

#### 项目结构
```
maoocr-desktop/
├── src/
│   ├── main/              # 主进程
│   ├── renderer/          # 渲染进程
│   └── shared/            # 共享代码
├── public/
├── package.json
└── electron-builder.json
```

#### 主进程实现
```javascript
// src/main/main.js
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

class MaoOCRDesktop {
  constructor() {
    this.mainWindow = null;
    this.pythonProcess = null;
  }

  createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
      },
    });

    this.mainWindow.loadFile('src/renderer/index.html');
    
    // 启动Python后端服务
    this.startPythonBackend();
  }

  startPythonBackend() {
    const pythonPath = path.join(__dirname, '../python/maoocr_server.py');
    this.pythonProcess = spawn('python', [pythonPath]);

    this.pythonProcess.stdout.on('data', (data) => {
      console.log('Python输出:', data.toString());
    });

    this.pythonProcess.stderr.on('data', (data) => {
      console.error('Python错误:', data.toString());
    });
  }

  setupIPC() {
    // 处理文件选择
    ipcMain.handle('select-file', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow, {
        properties: ['openFile'],
        filters: [
          { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'bmp'] },
          { name: 'PDFs', extensions: ['pdf'] },
        ],
      });
      return result.filePaths[0];
    });

    // 处理OCR识别
    ipcMain.handle('recognize-image', async (event, imagePath) => {
      try {
        const response = await fetch('http://localhost:8000/api/ocr/recognize', {
          method: 'POST',
          body: JSON.stringify({ image_path: imagePath }),
          headers: {
            'Content-Type': 'application/json',
          },
        });
        return await response.json();
      } catch (error) {
        throw new Error(`OCR识别失败: ${error.message}`);
      }
    });
  }
}

const maoOCR = new MaoOCRDesktop();

app.whenReady().then(() => {
  maoOCR.createWindow();
  maoOCR.setupIPC();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

#### 渲染进程实现
```html
<!-- src/renderer/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>MaoOCR 桌面版</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>MaoOCR 智能识别系统</h1>
        </header>
        
        <main>
            <div class="image-section">
                <button id="selectFile">选择文件</button>
                <div id="imagePreview"></div>
            </div>
            
            <div class="settings-section">
                <h3>识别设置</h3>
                <label>
                    文档类型:
                    <select id="documentType">
                        <option value="auto">自动检测</option>
                        <option value="simple_text">简单文本</option>
                        <option value="complex_layout">复杂布局</option>
                    </select>
                </label>
                
                <label>
                    语言:
                    <select id="language">
                        <option value="auto">自动检测</option>
                        <option value="chinese">中文</option>
                        <option value="english">英文</option>
                    </select>
                </label>
                
                <label>
                    准确率要求:
                    <select id="accuracy">
                        <option value="medium">中等</option>
                        <option value="high">高</option>
                    </select>
                </label>
            </div>
            
            <div class="action-section">
                <button id="recognize">开始识别</button>
                <button id="batchProcess">批量处理</button>
            </div>
            
            <div class="result-section">
                <h3>识别结果</h3>
                <div id="resultText"></div>
                <div id="resultInfo"></div>
            </div>
        </main>
    </div>
    
    <script src="renderer.js"></script>
</body>
</html>
```

```javascript
// src/renderer/renderer.js
const { ipcRenderer } = require('electron');

class MaoOCRRenderer {
  constructor() {
    this.selectedFile = null;
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('selectFile').addEventListener('click', () => {
      this.selectFile();
    });

    document.getElementById('recognize').addEventListener('click', () => {
      this.recognizeImage();
    });

    document.getElementById('batchProcess').addEventListener('click', () => {
      this.batchProcess();
    });
  }

  async selectFile() {
    try {
      const filePath = await ipcRenderer.invoke('select-file');
      if (filePath) {
        this.selectedFile = filePath;
        this.displayImagePreview(filePath);
      }
    } catch (error) {
      this.showError('文件选择失败: ' + error.message);
    }
  }

  displayImagePreview(filePath) {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = `<img src="file://${filePath}" alt="预览" style="max-width: 100%; max-height: 300px;">`;
  }

  async recognizeImage() {
    if (!this.selectedFile) {
      this.showError('请先选择文件');
      return;
    }

    try {
      this.showLoading('正在识别中...');
      
      const requirements = {
        document_type: document.getElementById('documentType').value,
        language: document.getElementById('language').value,
        accuracy_requirement: document.getElementById('accuracy').value,
        speed_requirement: 'medium',
        real_time: false,
        batch_processing: false,
      };

      const result = await ipcRenderer.invoke('recognize-image', this.selectedFile);
      this.displayResult(result);
    } catch (error) {
      this.showError('识别失败: ' + error.message);
    } finally {
      this.hideLoading();
    }
  }

  displayResult(result) {
    const resultText = document.getElementById('resultText');
    const resultInfo = document.getElementById('resultInfo');

    resultText.innerHTML = `<pre>${result.text}</pre>`;
    resultInfo.innerHTML = `
      <p>置信度: ${(result.confidence * 100).toFixed(2)}%</p>
      <p>处理时间: ${result.processing_time.toFixed(2)}秒</p>
      <p>使用模型: ${result.selected_models.join(', ')}</p>
    `;
  }

  showLoading(message) {
    // 显示加载状态
  }

  hideLoading() {
    // 隐藏加载状态
  }

  showError(message) {
    alert(message);
  }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
  new MaoOCRRenderer();
});
```

### 3. PyQt 实现

```python
# src/desktop/pyqt_app.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QComboBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np

from maoocr import MaoOCR

class OCRWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, image_path, requirements):
        super().__init__()
        self.image_path = image_path
        self.requirements = requirements

    def run(self):
        try:
            self.progress.emit(10)
            
            # 初始化MaoOCR
            ocr = MaoOCR(enable_dynamic_selection=True)
            self.progress.emit(30)
            
            # 执行识别
            result = ocr.recognize_with_requirements(self.image_path, self.requirements)
            self.progress.emit(90)
            
            self.finished.emit(result)
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(str(e))

class MaoOCRDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_image = None
        self.ocr_worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MaoOCR 桌面版')
        self.setGeometry(100, 100, 1000, 700)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 标题
        title = QLabel('MaoOCR 智能识别系统')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 24px; font-weight: bold; margin: 10px;')
        layout.addWidget(title)

        # 图像选择区域
        image_layout = QHBoxLayout()
        
        self.select_btn = QPushButton('选择图片')
        self.select_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_btn)
        
        self.image_label = QLabel('未选择图片')
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setStyleSheet('border: 2px dashed #ccc;')
        image_layout.addWidget(self.image_label)
        
        layout.addLayout(image_layout)

        # 设置区域
        settings_layout = QHBoxLayout()
        
        # 文档类型
        settings_layout.addWidget(QLabel('文档类型:'))
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems(['auto', 'simple_text', 'complex_layout'])
        settings_layout.addWidget(self.doc_type_combo)
        
        # 语言
        settings_layout.addWidget(QLabel('语言:'))
        self.language_combo = QComboBox()
        self.language_combo.addItems(['auto', 'chinese', 'english'])
        settings_layout.addWidget(self.language_combo)
        
        # 准确率
        settings_layout.addWidget(QLabel('准确率:'))
        self.accuracy_combo = QComboBox()
        self.accuracy_combo.addItems(['medium', 'high'])
        settings_layout.addWidget(self.accuracy_combo)
        
        layout.addLayout(settings_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.recognize_btn = QPushButton('开始识别')
        self.recognize_btn.clicked.connect(self.start_recognition)
        self.recognize_btn.setEnabled(False)
        button_layout.addWidget(self.recognize_btn)
        
        self.batch_btn = QPushButton('批量处理')
        self.batch_btn.clicked.connect(self.batch_process)
        button_layout.addWidget(self.batch_btn)
        
        layout.addLayout(button_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 结果显示
        result_label = QLabel('识别结果:')
        result_label.setStyleSheet('font-weight: bold; margin-top: 10px;')
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择图片', '', 
            'Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)'
        )
        
        if file_path:
            self.selected_image = file_path
            self.display_image(file_path)
            self.recognize_btn.setEnabled(True)

    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def start_recognition(self):
        if not self.selected_image:
            return

        # 构建需求
        requirements = {
            'document_type': self.doc_type_combo.currentText(),
            'language': self.language_combo.currentText(),
            'accuracy_requirement': self.accuracy_combo.currentText(),
            'speed_requirement': 'medium',
            'real_time': False,
            'batch_processing': False,
        }

        # 启动工作线程
        self.ocr_worker = OCRWorker(self.selected_image, requirements)
        self.ocr_worker.finished.connect(self.on_recognition_finished)
        self.ocr_worker.error.connect(self.on_recognition_error)
        self.ocr_worker.progress.connect(self.progress_bar.setValue)
        
        self.ocr_worker.start()
        
        # 更新UI状态
        self.recognize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

    def on_recognition_finished(self, result):
        # 显示结果
        self.result_text.setText(f"""
识别文本:
{result.text}

置信度: {result.confidence:.2%}
处理时间: {result.processing_time:.2f}秒
使用模型: {', '.join(result.selected_models)}
        """)
        
        # 恢复UI状态
        self.recognize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def on_recognition_error(self, error_msg):
        self.result_text.setText(f'识别失败: {error_msg}')
        self.recognize_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def batch_process(self):
        # 批量处理实现
        pass

def main():
    app = QApplication(sys.argv)
    window = MaoOCRDesktop()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

## 🐳 Docker部署

### 1. Docker架构设计

#### 容器化策略
- **微服务架构**: 将不同功能拆分为独立容器
- **数据持久化**: 使用Docker volumes存储模型和数据
- **负载均衡**: 使用Nginx进行负载均衡
- **监控**: 集成Prometheus和Grafana

#### 架构图
```
Docker部署架构
├── Nginx (负载均衡)
├── MaoOCR API (FastAPI)
├── vLLM服务 (模型推理)
├── Redis (缓存)
├── PostgreSQL (数据存储)
└── Prometheus + Grafana (监控)
```

### 2. Dockerfile 配置

#### 基础镜像
```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY configs/ ./configs/
COPY models/ ./models/

# 创建非root用户
RUN useradd -m -u 1000 maoocr && chown -R maoocr:maoocr /app
USER maoocr

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "src.maoocr.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 多阶段构建
```dockerfile
# Dockerfile.multi-stage
# 构建阶段
FROM python:3.9-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制应用代码
COPY --chown=1000:1000 src/ ./src/
COPY --chown=1000:1000 configs/ ./configs/
COPY --chown=1000:1000 models/ ./models/

# 创建用户
RUN useradd -m -u 1000 maoocr

USER maoocr

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.maoocr.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Docker Compose 配置

#### 完整服务配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # MaoOCR API服务
  maoocr-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://maoocr:password@postgres:5432/maoocr
      - MODEL_PATH=/app/models
    volumes:
      - model_data:/app/models
      - cache_data:/app/cache
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'

  # vLLM服务
  vllm-service:
    build:
      context: .
      dockerfile: Dockerfile.vllm
    ports:
      - "8001:8000"
    environment:
      - MODEL_PATH=/app/models
      - TENSOR_PARALLEL_SIZE=1
      - GPU_MEMORY_UTILIZATION=0.9
    volumes:
      - model_data:/app/models
    deploy:
      resources:
        limits:
          memory: 12G
          cpus: '6'
        reservations:
          memory: 8G
          cpus: '4'
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: maoocr
      POSTGRES_USER: maoocr
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Nginx负载均衡
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - maoocr-api
    restart: unless-stopped

  # Prometheus监控
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana可视化
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  model_data:
  cache_data:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

#### Nginx配置
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream maoocr_backend {
        server maoocr-api:8000;
        server vllm-service:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://maoocr_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            proxy_pass http://maoocr_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /v1/ {
            proxy_pass http://maoocr_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Kubernetes部署

#### 部署配置
```yaml
# k8s/maoocr-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maoocr-api
  labels:
    app: maoocr-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: maoocr-api
  template:
    metadata:
      labels:
        app: maoocr-api
    spec:
      containers:
      - name: maoocr-api
        image: maoocr/maoocr-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: DATABASE_URL
          value: "postgresql://maoocr:password@postgres-service:5432/maoocr"
        resources:
          limits:
            memory: "8Gi"
            cpu: "4"
          requests:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: model-storage
          mountPath: /app/models
        - name: cache-storage
          mountPath: /app/cache
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
      - name: cache-storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: maoocr-service
spec:
  selector:
    app: maoocr-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
```

### 5. 部署脚本

#### 自动化部署
```bash
#!/bin/bash
# deploy.sh

set -e

echo "开始部署MaoOCR..."

# 构建镜像
echo "构建Docker镜像..."
docker build -t maoocr/maoocr-api:latest .

# 启动服务
echo "启动Docker Compose服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 运行健康检查
echo "运行健康检查..."
curl -f http://localhost:8000/health || exit 1

echo "部署完成！"
echo "访问地址: http://localhost"
echo "API文档: http://localhost/docs"
echo "监控面板: http://localhost:3000"
```

## 📊 性能对比

### 平台性能对比

| 平台 | 启动时间 | 内存占用 | 响应速度 | 部署复杂度 | 维护成本 |
|------|----------|----------|----------|------------|----------|
| **移动端** | 快 | 低 | 中等 | 高 | 中等 |
| **桌面端** | 快 | 中等 | 快 | 中等 | 低 |
| **Docker** | 中等 | 高 | 快 | 低 | 低 |

### 资源使用对比

| 平台 | CPU使用 | 内存使用 | 存储空间 | 网络带宽 |
|------|---------|----------|----------|----------|
| **移动端** | 低 | 100-200MB | 50-100MB | 低 |
| **桌面端** | 中等 | 500MB-1GB | 200-500MB | 中等 |
| **Docker** | 高 | 2-8GB | 1-5GB | 高 |

## 🔮 未来规划

### 1. 移动端优化
- 支持离线识别
- 优化图像压缩
- 增加AR识别功能

### 2. 桌面端增强
- 支持插件系统
- 增加批处理功能
- 优化用户界面

### 3. 容器化改进
- 支持GPU容器
- 增加自动扩缩容
- 优化资源调度

## 📚 总结

多平台部署为MaoOCR提供了灵活的部署选择，用户可以根据自己的需求选择合适的平台。移动端适合个人使用，桌面端适合专业用户，Docker部署适合企业级应用。每种部署方式都有其优势和适用场景，关键是要根据实际需求进行选择。 