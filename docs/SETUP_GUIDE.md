# HelixGraph Setup Guide

## 🎯 环境配置策略

### Git 仓库（共享）
- 所有代码、配置文件、文档都提交到 Git
- 三个人从同一个仓库拉取代码

### 本地环境（各自独立）
- 每个人在**本地**创建虚拟环境 (venv)
- 使用统一的 `requirements.txt` 安装依赖
- 不要提交 `venv/` 目录到 Git

### 敏感信息（本地保存）
- `.env` 文件包含真实密钥，**不提交**到 Git
- 使用 `.env.example` 作为模板

---

## 📋 首次设置步骤

### Step 1: 创建虚拟环境
```bash
cd /Users/ivan/FSFM/01_Courses/Coop/Helixgraph
python3 -m venv venv
```

### Step 2: 激活虚拟环境
```bash
source venv/bin/activate
```
**重要**: 每次开始工作时都要激活虚拟环境！

### Step 3: 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: 下载 spaCy 模型（HEL-21 需要）
```bash
python -m spacy download en_core_web_trf
```

### Step 5: 配置环境变量
```bash
cp .env.example .env
# 然后编辑 .env 文件，填入真实的密码和 API keys
```

---

## 🔄 日常工作流程

### 开始工作
```bash
cd Helixgraph
source venv/bin/activate      # 激活虚拟环境
git pull origin main          # 拉取最新代码
```

### 结束工作
```bash
git add .
git commit -m "完成 XXX 功能"
git push origin main
deactivate                    # 退出虚拟环境
```

---

## 🤝 团队协作规则

### 目录归属
- `nlp/` 和 `api/` → Ivan (HEL-21)
- `data_pipeline/` → Sun (HEL-22)
- `rag/` → Mert (HEL-23)
- `docs/` → 共享文档

### 依赖管理
如果你需要安装新的 Python 包：
```bash
pip install package-name
pip freeze > requirements.txt  # 更新依赖列表
git add requirements.txt
git commit -m "添加 package-name 依赖"
```

### 数据共享
- Ivan 需要 Sun 的数据：`campaigns.json`, `brands.json`, `products.csv`
- Ivan 需要 Mert 的数据：`suppliers.csv`, PO 编号, Contract IDs
- 数据文件应该放在 `data/raw/` 目录（可能需要创建）

---

## ⚠️ 常见问题

### Q: 虚拟环境激活后命令行没变化？
**A**: 正常现象，确认方法：
```bash
which python
# 应该显示: /Users/ivan/.../Helixgraph/venv/bin/python
```

### Q: pip install 很慢？
**A**: 可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 如何确认安装成功？
**A**: 运行测试脚本：
```bash
python -c "import spacy; print(spacy.__version__)"
python -c "import fastapi; print(fastapi.__version__)"
```

### Q: Git 冲突怎么办？
**A**: 
```bash
git pull origin main
# 如果有冲突，手动解决后：
git add .
git commit -m "解决合并冲突"
git push origin main
```

---

## 📞 需要帮助？

- Ivan (HEL-21): NER 和 API 问题
- Sun (HEL-22): 数据处理问题
- Mert (HEL-23): RAG 和 LLM 问题
