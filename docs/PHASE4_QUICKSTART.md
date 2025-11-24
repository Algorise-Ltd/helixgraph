# Phase 4 快速开始指南 - Colab版

## 📋 概述

Phase 4在Colab中开发，主要代码在`.py`文件中，notebook仅用于运行脚本。

## 🚀 使用Colab开发

### 1. 打开开发notebook

在Colab中打开：
```
HEL21_Phase4_Development.ipynb
```

### 2. 运行notebook

按照notebook中的步骤执行：
- ✅ 挂载Google Drive
- ✅ 安装依赖
- ✅ 测试模型
- ✅ 运行脚本

### 3. 编辑代码

**推荐工作流**：
1. 在本地IDE编辑`.py`文件
2. Google Drive自动同步到Colab
3. 在Colab中运行和测试

## 📁 Phase 4文件结构

```
Helixgraph/
├── HEL21_Phase4_Development.ipynb  # Colab开发notebook
│
├── nlp/
│   ├── entity_linking.py           # ✅ Entity linking实现
│   ├── entity_extraction.py        # ✅ RAG helper (for HEL-23)
│   └── scripts/
│       ├── test_trained_model.py   # Phase 3模型测试
│       └── test_entity_linking.py  # ✅ Entity linking测试
│
├── api/
│   ├── __init__.py
│   ├── config.py                   # ✅ 配置管理
│   └── main.py                     # ✅ FastAPI应用
│
└── tests/
    ├── __init__.py
    └── test_api.py                 # ✅ API测试
```

## 🧪 测试命令

### 在Colab中运行：

```python
# 测试Phase 3模型
!python nlp/scripts/test_trained_model.py

# 测试Entity Linking
!python nlp/scripts/test_entity_linking.py

# 测试Entity Extraction (RAG helper)
!python nlp/entity_extraction.py

# 启动FastAPI
!uvicorn api.main:app --host 0.0.0.0 --port 8000

# 运行pytest测试
!pytest tests/test_api.py -v
```

## 🔧 本地编辑流程

1. **在本地编辑代码**
   ```bash
   cd "/Users/ivan/Library/CloudStorage/GoogleDrive-.../Helixgraph"
   code nlp/entity_linking.py
   ```

2. **自动同步到Colab**
   - Google Drive会自动同步
   - 稍等几秒让同步完成

3. **在Colab中测试**
   ```python
   # 重新加载模块
   import importlib
   import nlp.entity_linking
   importlib.reload(nlp.entity_linking)
   
   # 运行测试
   !python nlp/scripts/test_entity_linking.py
   ```

## 📊 Phase 4任务清单

### Week 1: Entity Linking ✅
- [x] 创建 `nlp/entity_linking.py`
- [x] 创建 `nlp/scripts/test_entity_linking.py`
- [ ] 确保entity_vocabulary.json存在
- [ ] 运行测试并调优threshold

### Week 2: FastAPI基础 ✅
- [x] 创建 `api/main.py`
- [x] 创建 `api/config.py`
- [x] 实现 `/health` endpoint
- [x] 实现 `/api/extract-entities` endpoint
- [x] 实现 `/api/link-entities` endpoint
- [ ] 在Colab中测试API

### Week 3: RAG集成 ✅
- [x] 创建 `nlp/entity_extraction.py`
- [ ] 与Mert测试集成

### Week 4: Neo4j & 固定查询
- [ ] 等待Sun的Neo4j数据库 (HEL-22)
- [ ] 实现4个固定查询endpoints
- [ ] 端到端测试

## 🌐 访问Colab API

### 方式1: 使用ngrok (推荐)

在Colab中：
```python
from pyngrok import ngrok
public_url = ngrok.connect(8000)
print(f"API URL: {public_url}")
```

然后在本地terminal测试：
```bash
curl https://xxxx.ngrok.io/health
curl https://xxxx.ngrok.io/api/extract-entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Acme Corp submitted PO-2024-001"}'
```

### 方式2: Colab内部测试

在Colab中：
```python
import requests
response = requests.post(
    "http://localhost:8000/api/extract-entities",
    json={"text": "Tech Solutions Ltd submitted PO-2024-001"}
)
print(response.json())
```

## 🐛 常见问题

### Q: 模型加载失败
```python
# 检查模型路径
!ls -la nlp/models/ner_model/model-best/

# 确保Google Drive已挂载
from google.colab import drive
drive.mount('/content/drive', force_remount=True)
```

### Q: 模块导入错误
```python
# 确保在项目目录
%cd /content/drive/MyDrive/Helixgraph

# 添加到Python path
import sys
sys.path.insert(0, '/content/drive/MyDrive/Helixgraph')
```

### Q: FastAPI无法启动
```python
# 检查端口
!lsof -ti:8000

# 杀死占用的进程
!kill -9 $(lsof -ti:8000)

# 重新启动
!uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 📞 团队协作

### 与Sun (HEL-22) 协调：
- Neo4j数据库连接信息
- 数据schema确认
- 固定查询需求

### 与Mert (HEL-23) 协调：
- RAG接口测试
- `nlp/entity_extraction.py` 使用方法
- 集成测试数据

## 🎯 下一步

1. ✅ 确认所有文件已创建
2. 📝 在Colab中打开 `HEL21_Phase4_Development.ipynb`
3. ▶️ 运行所有cell，验证环境
4. 🧪 运行测试，确保通过
5. 📊 记录结果，准备进入Week 2

---

**准备好了吗？** 打开Colab notebook开始吧！ 🚀
