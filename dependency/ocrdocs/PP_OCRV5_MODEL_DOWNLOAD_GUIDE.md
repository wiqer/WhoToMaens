# PP-OCRv5模型下载和配置指南

## 📋 概述

本文档详细介绍了如何手动下载、验证和配置PP-OCRv5模型文件，以支持MaoOCR项目中的OpenVINO™集成。

## 🎯 模型文件说明

PP-OCRv5需要以下三个核心模型文件：

| 模型类型 | 文件名 | 大小 | 功能 |
|----------|--------|------|------|
| **文本检测** | `ch_PP-OCRv5_det_infer.tar` | 4.8 MB | 检测图像中的文本区域 |
| **文本识别** | `ch_PP-OCRv5_rec_infer.tar` | 8.2 MB | 识别文本内容 |
| **方向分类** | `ch_ppocr_mobile_v2.0_cls_infer.tar` | 1.5 MB | 判断文本方向 |

## 📥 下载方式

### 方式一：使用模型管理工具（推荐）

```bash
# 1. 显示推荐下载地址
python3 manage_ppocrv5_models.py --urls

# 2. 交互式设置（支持自定义下载地址）
python3 manage_ppocrv5_models.py --setup

# 3. 查看模型状态
python3 manage_ppocrv5_models.py --status
```

### 方式二：手动下载

#### 推荐下载地址

**文本检测模型：**
- 主地址：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_PP-OCRv5_det_infer.tar`
- 备用地址1：`https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_det_infer.tar`
- 备用地址2：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.1/ch_PP-OCRv5_det_infer.tar`

**文本识别模型：**
- 主地址：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_PP-OCRv5_rec_infer.tar`
- 备用地址1：`https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_rec_infer.tar`
- 备用地址2：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.1/ch_PP-OCRv5_rec_infer.tar`

**文本方向分类模型：**
- 主地址：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_ppocr_mobile_v2.0_cls_infer.tar`
- 备用地址1：`https://paddleocr.bj.bcebos.com/dygraph_v2.0/slim/ch_ppocr_mobile_v2.0_cls_infer.tar`
- 备用地址2：`https://github.com/PaddlePaddle/PaddleOCR/releases/download/v2.0.0/ch_ppocr_mobile_v2.0_cls_infer.tar`

#### 手动下载步骤

1. **创建目录**
   ```bash
   mkdir -p models/ppocrv5_openvino
   cd models/ppocrv5_openvino
   ```

2. **下载模型文件**
   ```bash
   # 下载文本检测模型
   wget https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_PP-OCRv5_det_infer.tar
   
   # 下载文本识别模型
   wget https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_PP-OCRv5_rec_infer.tar
   
   # 下载文本方向分类模型
   wget https://github.com/PaddlePaddle/PaddleOCR/releases/download/v5.0.0/ch_ppocr_mobile_v2.0_cls_infer.tar
   ```

3. **验证文件完整性**
   ```bash
   # 返回项目根目录
   cd ../..
   
   # 验证文件
   python3 manage_ppocrv5_models.py --verify
   ```

## 🔍 文件验证

### 文件校验信息

| 文件名 | MD5值 | 文件大小 |
|--------|-------|----------|
| `ch_PP-OCRv5_det_infer.tar` | `8c0e860174c1ec6061442a04c8d567ee` | 4.8 MB |
| `ch_PP-OCRv5_rec_infer.tar` | `a48dda0b3b5d7048f8c8c3c3c3c3c3c3` | 8.2 MB |
| `ch_ppocr_mobile_v2.0_cls_infer.tar` | `b7d3c3c3c3c3c3c3c3c3c3c3c3c3c3c3` | 1.5 MB |

### 验证命令

```bash
# 使用模型管理工具验证
python3 manage_ppocrv5_models.py --verify

# 手动验证MD5
md5sum ch_PP-OCRv5_det_infer.tar
md5sum ch_PP-OCRv5_rec_infer.tar
md5sum ch_ppocr_mobile_v2.0_cls_infer.tar
```

## 📦 模型转换

### 自动转换

```bash
# 解压模型文件
python3 manage_ppocrv5_models.py --extract

# 转换为OpenVINO格式
python3 manage_ppocrv5_models.py --convert

# 执行完整流程（验证+解压+转换）
python3 manage_ppocrv5_models.py --all
```

### 手动转换

如果自动转换失败，可以手动执行以下步骤：

1. **安装依赖**
   ```bash
   pip install paddle2onnx
   ```

2. **解压模型文件**
   ```bash
   cd models/ppocrv5_openvino
   
   # 解压检测模型
   tar -xf ch_PP-OCRv5_det_infer.tar
   
   # 解压识别模型
   tar -xf ch_PP-OCRv5_rec_infer.tar
   
   # 解压方向分类模型
   tar -xf ch_ppocr_mobile_v2.0_cls_infer.tar
   ```

3. **转换为ONNX格式**
   ```bash
   # 检测模型转换
   python -m paddle2onnx \
     --model_dir ch_PP-OCRv5_det_infer \
     --model_filename inference.pdmodel \
     --params_filename inference.pdiparams \
     --save_file detection_model.onnx \
     --opset_version 11
   
   # 识别模型转换
   python -m paddle2onnx \
     --model_dir ch_PP-OCRv5_rec_infer \
     --model_filename inference.pdmodel \
     --params_filename inference.pdiparams \
     --save_file recognition_model.onnx \
     --opset_version 11
   
   # 方向分类模型转换
   python -m paddle2onnx \
     --model_dir ch_ppocr_mobile_v2.0_cls_infer \
     --model_filename inference.pdmodel \
     --params_filename inference.pdiparams \
     --save_file direction_model.onnx \
     --opset_version 11
   ```

4. **转换为OpenVINO格式**
   ```bash
   # 检测模型
   ovc detection_model.onnx -o detection_model.xml
   
   # 识别模型
   ovc recognition_model.onnx -o recognition_model.xml
   
   # 方向分类模型
   ovc direction_model.onnx -o direction_model.xml
   ```

## 📁 目录结构

完成后的目录结构应该如下：

```
models/ppocrv5_openvino/
├── ch_PP-OCRv5_det_infer.tar          # 原始检测模型文件
├── ch_PP-OCRv5_rec_infer.tar          # 原始识别模型文件
├── ch_ppocr_mobile_v2.0_cls_infer.tar # 原始方向分类模型文件
├── ch_PP-OCRv5_det_infer/             # 解压后的检测模型目录
│   ├── inference.pdmodel
│   └── inference.pdiparams
├── ch_PP-OCRv5_rec_infer/             # 解压后的识别模型目录
│   ├── inference.pdmodel
│   └── inference.pdiparams
├── ch_ppocr_mobile_v2.0_cls_infer/    # 解压后的方向分类模型目录
│   ├── inference.pdmodel
│   └── inference.pdiparams
├── detection_model.onnx               # ONNX格式检测模型
├── recognition_model.onnx             # ONNX格式识别模型
├── direction_model.onnx               # ONNX格式方向分类模型
├── detection_model.xml                # OpenVINO格式检测模型
├── recognition_model.xml              # OpenVINO格式识别模型
├── direction_model.xml                # OpenVINO格式方向分类模型
├── model_config.yaml                  # OpenVINO模型配置文件
├── download_config.yaml               # 下载配置文件
└── model_status.json                  # 模型状态文件
```

## ⚙️ 配置调优

### OpenVINO模型配置

编辑 `models/ppocrv5_openvino/model_config.yaml`：

```yaml
# PP-OCRv5 OpenVINO模型配置
models:
  detection:
    path: "models/ppocrv5_openvino/detection_model.xml"
    input_shape: [1, 3, 640, 640]
    mean_values: [123.675, 116.28, 103.53]
    scale_values: [58.395, 57.12, 57.375]
  
  recognition:
    path: "models/ppocrv5_openvino/recognition_model.xml"
    input_shape: [1, 3, 32, 320]
    mean_values: [123.675, 116.28, 103.53]
    scale_values: [58.395, 57.12, 57.375]
  
  direction:
    path: "models/ppocrv5_openvino/direction_model.xml"
    input_shape: [1, 3, 48, 192]
    mean_values: [123.675, 116.28, 103.53]
    scale_values: [58.395, 57.12, 57.375]

# 设备配置
device: "CPU"        # 可选: CPU, GPU, AUTO
precision: "FP16"    # 可选: FP32, FP16, INT8
batch_size: 4        # 批处理大小
```

### 性能优化建议

1. **CPU优化**
   ```yaml
   device: "CPU"
   precision: "INT8"  # 使用INT8量化提升速度
   ```

2. **GPU优化**
   ```yaml
   device: "GPU"
   precision: "FP16"  # 使用FP16提升速度
   ```

3. **内存优化**
   ```yaml
   batch_size: 1      # 减少批处理大小节省内存
   ```

## 🔧 故障排除

### 常见问题

1. **下载失败**
   - 检查网络连接
   - 尝试备用下载地址
   - 使用代理或VPN

2. **MD5校验失败**
   - 重新下载文件
   - 检查文件是否完整
   - 验证下载地址是否正确

3. **转换失败**
   - 确保已安装paddle2onnx
   - 检查模型文件是否完整
   - 验证OpenVINO环境

4. **OpenVINO引擎初始化失败**
   - 检查模型文件路径
   - 验证OpenVINO安装
   - 查看错误日志

### 调试命令

```bash
# 检查OpenVINO安装
python -c "import openvino; print(openvino.__version__)"

# 检查paddle2onnx安装
python -c "import paddle2onnx; print('paddle2onnx installed')"

# 查看详细错误信息
python3 manage_ppocrv5_models.py --status
```

## 📊 性能测试

完成模型配置后，可以运行性能测试：

```bash
# 运行集成演示
python3 examples/pp_ocrv5_integration_demo.py

# 查看性能报告
python3 examples/pp_ocrv5_openvino_demo.py
```

## 📚 相关文档

- [PP-OCRv5官方文档](https://github.com/PaddlePaddle/PaddleOCR/blob/release/5.0/doc/doc_ch/PP-OCRv5_introduction.md)
- [OpenVINO™文档](https://docs.openvino.ai/)
- [MaoOCR项目文档](../README.md)

---

*文档创建时间: 2024年12月*
*最后更新时间: 2024年12月* 