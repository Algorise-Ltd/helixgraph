# Google Colab 迁移指南

## 🎯 为什么用Colab？

- ✅ **免费GPU**: Tesla T4 GPU，训练速度快30-40倍
- ✅ **稳定环境**: 预配置的Python环境，无依赖冲突
- ✅ **更大内存**: 12GB+ RAM，避免本地OOM问题
- ✅ **云端运行**: 不占用本地资源，可关闭电脑

---

## 📁 Step 1: 同步文件到Google Drive

### 方法A: 手动复制（推荐）

1. 打开Finder，导航到：
   ```
   /Users/ivan/Library/CloudStorage/GoogleDrive-ivan.guoyixuan@gmail.com/
   ```

2. 创建项目文件夹结构：
   ```
   GoogleDrive-ivan.guoyixuan@gmail.com/
   └── FSFM/
       └── 01_Courses/
           └── Coop/
               └── Helixgraph/
                   └── nlp/
                       ├── configs/
                       │   └── config.cfg
                       └── training_data/
                           └── spacy/
                               ├── train.spacy
                               └── dev.spacy
   ```

3. 复制以下文件到对应位置：
   - `nlp/configs/config.cfg`
   - `nlp/training_data/spacy/train.spacy`
   - `nlp/training_data/spacy/dev.spacy`

### 方法B: 命令行复制

```bash
# 定义目标路径
GDRIVE_PATH="/Users/ivan/Library/CloudStorage/GoogleDrive-ivan.guoyixuan@gmail.com/FSFM/01_Courses/Coop/Helixgraph"

# 创建目录结构
mkdir -p "$GDRIVE_PATH/nlp/configs"
mkdir -p "$GDRIVE_PATH/nlp/training_data/spacy"

# 复制文件
cp nlp/configs/config.cfg "$GDRIVE_PATH/nlp/configs/"
cp nlp/training_data/spacy/train.spacy "$GDRIVE_PATH/nlp/training_data/spacy/"
cp nlp/training_data/spacy/dev.spacy "$GDRIVE_PATH/nlp/training_data/spacy/"

# 验证
ls -lh "$GDRIVE_PATH/nlp/configs/"
ls -lh "$GDRIVE_PATH/nlp/training_data/spacy/"
```

---

## 🚀 Step 2: 上传Notebook到Colab

### 选项A: 直接上传

1. 打开 [Google Colab](https://colab.research.google.com/)
2. 点击 `File` → `Upload notebook`
3. 选择: `/Users/ivan/FSFM/01_Courses/Coop/Helixgraph/HEL21_NER_Training.ipynb`

### 选项B: 从Google Drive打开

1. 将notebook复制到Google Drive：
   ```bash
   cp HEL21_NER_Training.ipynb "/Users/ivan/Library/CloudStorage/GoogleDrive-ivan.guoyixuan@gmail.com/"
   ```

2. 在Google Drive中右键点击notebook
3. 选择 `Open with` → `Google Colaboratory`

---

## ⚙️ Step 3: 配置Colab运行环境

### 1. 启用GPU（重要！）

在Colab中：
- 点击 `Runtime` → `Change runtime type`
- 选择 `Hardware accelerator: GPU`
- 选择 `GPU type: T4` (免费版)
- 点击 `Save`

### 2. 设置高RAM（如果可用）

- `Runtime` → `Change runtime type`
- 选择 `Runtime shape: High-RAM`
- 点击 `Save`

---

## 🎬 Step 4: 执行训练

### 快速开始

1. **Mount Google Drive** (Cell 1)
   - 运行第一个cell
   - 点击授权链接，登录Google账号
   - 复制授权码

2. **安装依赖** (Cell 2)
   - 自动安装spaCy和transformers
   - 大约需要2-3分钟

3. **检查GPU** (Cell 3)
   - 确认GPU已启用
   - 看到 "✅ GPU Available: Tesla T4" 即成功

4. **复制文件** (Cell 4b - 使用Option B)
   - 从Google Drive复制训练数据
   - 确认路径正确

5. **开始训练** (Cell 7)
   - 点击运行
   - **预计时间**: 30-45分钟（GPU）
   - 观察训练指标

### 训练过程监控

训练时会显示：
```
E    #       LOSS TRANS...  LOSS NER  ENTS_F  ENTS_P  ENTS_R  SCORE 
---  ------  -------------  --------  ------  ------  ------  ------
  0       0           0.00    127.45    0.00    0.00    0.00    0.00
  0     200          53.22     45.78   65.23   68.45   62.34   0.65
  1     400          32.15     28.92   78.45   80.12   76.89   0.78
  2     600          18.34     16.23   84.56   86.23   82.98   0.85
...
✔ Saved pipeline to output directory
nlp/models/ner_model/model-best
```

**关键指标：**
- `ENTS_F`: F1-score（目标: >85%）
- `ENTS_P`: Precision（准确率）
- `ENTS_R`: Recall（召回率）
- `LOSS NER`: 损失（应逐渐下降）

---

## 📊 Step 5: 评估和测试

### 评估模型 (Cell 8)

```python
!python -m spacy evaluate \
    nlp/models/ner_model/model-best \
    nlp/training_data/spacy/dev.spacy \
    --gpu-id 0
```

### 测试样例 (Cell 9)

运行测试cell查看模型识别效果：

```
🧪 Testing model with sample sentences:

1. The Marketing Coordinator managed the Nike Summer Sale campaign successfully.
   Entities found: 3
     - [ROLE] 'Marketing Coordinator'
     - [PRODUCT] 'Nike'
     - [CAMPAIGN] 'Nike Summer Sale'
```

---

## 💾 Step 6: 下载训练好的模型

### 方法A: 直接下载（Cell 12）

运行最后一个cell，模型会自动下载为zip文件。

### 方法B: 从Google Drive下载

模型已保存在：
```
/content/drive/MyDrive/Helixgraph/nlp/models/ner_model/model-best/
```

在Google Drive网页端右键下载整个文件夹。

---

## ⚠️ 常见问题

### 1. GPU不可用

**症状**: "No GPU available, will use CPU"

**解决**:
- Runtime → Change runtime type → GPU → T4
- 重启runtime: Runtime → Restart runtime

### 2. Google Drive挂载失败

**症状**: "Drive mount failed"

**解决**:
```python
# 重新挂载
from google.colab import drive
drive.flush_and_unmount()
drive.mount('/content/drive', force_remount=True)
```

### 3. 内存不足

**症状**: "CUDA out of memory"

**解决**:
```python
# 在config.cfg中减小batch size
# 或使用Runtime → Restart runtime释放内存
```

### 4. 找不到文件

**症状**: "No such file or directory"

**解决**:
```python
# 检查路径
!ls -la /content/drive/MyDrive/Helixgraph/nlp/training_data/spacy/

# 如果路径不对，修改PROJECT_PATH变量
PROJECT_PATH = "/content/drive/MyDrive/你的正确路径"
```

### 5. 训练中断

**症状**: Colab断开连接

**解决**:
- Colab免费版有12小时限制
- 训练应该在45分钟内完成
- 如果中断，模型会自动保存checkpoint
- 重新运行训练cell，会从checkpoint继续

---

## 🎯 训练完成后

### 下载到本地

1. 下载zip文件（Cell 12）
2. 解压到本地项目：
   ```bash
   cd /Users/ivan/FSFM/01_Courses/Coop/Helixgraph
   unzip ~/Downloads/ner_model_trained.zip
   ```

3. 验证模型：
   ```bash
   python -m spacy evaluate \
       nlp/models/ner_model/model-best \
       nlp/training_data/spacy/dev.spacy
   ```

### 集成到项目（Phase 4）

模型现在可以用于：
- FastAPI endpoint开发
- Entity linking实现
- Neo4j图数据库集成

---

## 📝 文件清单

确保以下文件已复制到Google Drive：

```
✅ nlp/configs/config.cfg (14KB)
✅ nlp/training_data/spacy/train.spacy (100KB)
✅ nlp/training_data/spacy/dev.spacy (29KB)
✅ HEL21_NER_Training.ipynb (notebook文件)
```

---

## 🚀 快速命令参考

```bash
# 1. 复制文件到Google Drive
GDRIVE="/Users/ivan/Library/CloudStorage/GoogleDrive-ivan.guoyixuan@gmail.com/FSFM/01_Courses/Coop/Helixgraph"
mkdir -p "$GDRIVE/nlp/configs" "$GDRIVE/nlp/training_data/spacy"
cp nlp/configs/config.cfg "$GDRIVE/nlp/configs/"
cp nlp/training_data/spacy/*.spacy "$GDRIVE/nlp/training_data/spacy/"
cp HEL21_NER_Training.ipynb "$GDRIVE/"

# 2. 验证文件
ls -lh "$GDRIVE/nlp/configs/"
ls -lh "$GDRIVE/nlp/training_data/spacy/"
```

---

## 💡 提示

- **保持连接**: 训练时不要关闭Colab标签页
- **监控进度**: 观察loss下降和F1-score上升
- **早停**: 如果F1-score达到>90%，可以提前停止
- **保存检查点**: 每200步自动保存
- **GPU时间**: 免费版Colab每天有GPU时间限制，合理使用

---

## ✅ 成功指标

训练成功的标志：

```
✅ Final F1-score: > 85%
✅ Training loss: < 5.0
✅ No errors during evaluation
✅ Model saved to: model-best/
✅ Test sentences correctly labeled
```

---

**准备好了吗？** 

1. ✅ 文件已复制到Google Drive
2. ✅ Notebook已上传到Colab
3. ✅ GPU已启用
4. 🚀 开始训练！

祝训练顺利！ 🎉
