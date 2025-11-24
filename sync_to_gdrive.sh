#!/bin/bash
# 快速同步文件到Google Drive以便在Colab中使用

echo "=================================="
echo "🚀 同步文件到Google Drive"
echo "=================================="

# 定义路径
PROJECT_ROOT="/Users/ivan/FSFM/01_Courses/Coop/Helixgraph"
GDRIVE_ROOT="/Users/ivan/Library/CloudStorage/Google Drive-ivan.guoyixuan@gmail.com/My Drive/Helixgraph"

# 创建目录结构
echo ""
echo "📁 创建目录结构..."
mkdir -p "$GDRIVE_ROOT/nlp/configs"
mkdir -p "$GDRIVE_ROOT/nlp/training_data/spacy"
mkdir -p "$GDRIVE_ROOT/nlp/training_data/raw"
mkdir -p "$GDRIVE_ROOT/docs"

# 复制配置文件
echo ""
echo "📋 复制配置文件..."
cp "$PROJECT_ROOT/nlp/configs/config.cfg" "$GDRIVE_ROOT/nlp/configs/" && echo "  ✅ config.cfg"

# 复制训练数据
echo ""
echo "📊 复制训练数据..."
cp "$PROJECT_ROOT/nlp/training_data/spacy/train.spacy" "$GDRIVE_ROOT/nlp/training_data/spacy/" && echo "  ✅ train.spacy"
cp "$PROJECT_ROOT/nlp/training_data/spacy/dev.spacy" "$GDRIVE_ROOT/nlp/training_data/spacy/" && echo "  ✅ dev.spacy"

# 复制原始数据（可选，但有助于备份）
echo ""
echo "💾 复制原始数据..."
if [ -f "$PROJECT_ROOT/nlp/training_data/raw/entity_vocabulary.json" ]; then
    cp "$PROJECT_ROOT/nlp/training_data/raw/entity_vocabulary.json" "$GDRIVE_ROOT/nlp/training_data/raw/" && echo "  ✅ entity_vocabulary.json"
fi
if [ -f "$PROJECT_ROOT/nlp/training_data/raw/training_data.json" ]; then
    cp "$PROJECT_ROOT/nlp/training_data/raw/training_data.json" "$GDRIVE_ROOT/nlp/training_data/raw/" && echo "  ✅ training_data.json"
fi

# 复制Notebook
echo ""
echo "📓 复制Colab Notebook..."
cp "$PROJECT_ROOT/HEL21_NER_Training.ipynb" "$GDRIVE_ROOT/" && echo "  ✅ HEL21_NER_Training.ipynb"

# 复制文档
echo ""
echo "📚 复制文档..."
cp "$PROJECT_ROOT/docs/COLAB_MIGRATION_GUIDE.md" "$GDRIVE_ROOT/docs/" && echo "  ✅ COLAB_MIGRATION_GUIDE.md"

# 验证文件
echo ""
echo "=================================="
echo "🔍 验证已复制的文件"
echo "=================================="

echo ""
echo "📋 Config文件:"
ls -lh "$GDRIVE_ROOT/nlp/configs/"

echo ""
echo "📊 Training数据:"
ls -lh "$GDRIVE_ROOT/nlp/training_data/spacy/"

echo ""
echo "📓 Notebook:"
ls -lh "$GDRIVE_ROOT/"*.ipynb

echo ""
echo "=================================="
echo "✅ 同步完成！"
echo "=================================="

echo ""
echo "🎯 下一步："
echo "  1. 打开 https://colab.research.google.com/"
echo "  2. File → Open notebook → Google Drive"
echo "  3. 导航到: FSFM/01_Courses/Coop/Helixgraph/HEL21_NER_Training.ipynb"
echo "  4. Runtime → Change runtime type → GPU (T4)"
echo "  5. 运行所有cells开始训练！"
echo ""
echo "📖 详细指南: $GDRIVE_ROOT/docs/COLAB_MIGRATION_GUIDE.md"
