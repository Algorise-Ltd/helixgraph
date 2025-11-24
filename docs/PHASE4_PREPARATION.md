# Phase 4: FastAPI Integration & Entity Linking

> **🔔 重要更新**: Phase 4 在 **Colab** 中开发！  
> 查看快速开始指南: [PHASE4_QUICKSTART.md](PHASE4_QUICKSTART.md)

## 🌐 Colab工作流程

### 开发环境
- **训练&运行**: Google Colab (云端GPU/CPU)
- **代码编辑**: 本地IDE (舒适的开发环境)
- **文件同步**: Google Drive (自动同步)
- **Notebook**: `HEL21_Phase4_Development.ipynb`

### 工作流程
1. 在本地IDE编辑 `.py` 文件
2. Google Drive自动同步到Colab
3. 在Colab notebook中运行脚本
4. 查看结果和调试

---

## ✅ Phase 3 完成检查清单

- [x] 模型训练完成（F1-score > 85%）
- [x] 模型已同步到Google Drive `nlp/models/ner_model/model-best/`
- [ ] 在Colab中测试通过 `!python nlp/scripts/test_trained_model.py`
- [ ] 训练指标已记录

---

## 🎯 Phase 4 目标

### 1. Entity Linking (实体链接)
将识别的实体链接到知识图谱中的标准ID

**示例**：
```
检测到: "Acme Corp"
链接到: SUPPLIER_ID_123 (from suppliers.json)
```

### 2. FastAPI Endpoints (4个固定查询)
根据HEL-21任务要求创建API端点

### 3. Neo4j Integration
连接图数据库，存储和查询实体关系

### 4. RAG Helper (for HEL-23)
为Mert的RAG系统提供实体提取接口

---

## 📋 Phase 4 子任务

### Task 4.1: Entity Linking 实现

**文件**: `nlp/entity_linking.py`

**功能**：
- 模糊匹配实体到vocabulary
- 处理别名和变体
- 返回标准化ID

**技术栈**：
- `fuzzywuzzy` - 字符串相似度
- `entity_vocabulary.json` - 实体字典

**示例代码**：
```python
from nlp.entity_linking import link_entities

text = "Acme Corp submitted PO-2024-001"
entities = extract_ner(text)  # [(0, 9, 'SUPPLIER'), ...]
linked = link_entities(entities)
# → [{"text": "Acme Corp", "type": "SUPPLIER", "id": "SUP-001"}]
```

---

### Task 4.2: FastAPI Application

**文件**: `api/main.py`

**4个固定查询端点**：

1. **Query 1**: 供应商相关合同和订单
   ```
   GET /api/supplier/{supplier_id}/contracts
   ```

2. **Query 2**: 营销活动绩效
   ```
   GET /api/campaign/{campaign_id}/performance
   ```

3. **Query 3**: 员工技能匹配
   ```
   GET /api/skills/match?required=Python,SQL
   ```

4. **Query 4**: 跨域关系查询
   ```
   POST /api/relationships
   Body: {"entity_type": "SUPPLIER", "entity_id": "SUP-001"}
   ```

**额外端点**：
- `POST /api/extract-entities` - NER提取
- `GET /api/health` - 健康检查

---

### Task 4.3: Neo4j Integration

**文件**: `api/neo4j_client.py`

**功能**：
- 连接Neo4j数据库
- 执行Cypher查询
- 返回图数据结构

**示例查询**：
```cypher
MATCH (s:Supplier {id: $supplier_id})-[:HAS_CONTRACT]->(c:Contract)
RETURN s, c
```

---

### Task 4.4: RAG Helper Module

**文件**: `nlp/entity_extraction.py`

**为HEL-23提供的接口**：
```python
def extract_entities_for_rag(question: str) -> dict:
    """
    Extract entities from RAG questions
    
    Args:
        question: User question
        
    Returns:
        {"SUPPLIER": ["Acme Corp"], "CAMPAIGN": ["Spring Launch"]}
    """
```

---

## 🛠️ 开发顺序

### Week 1: Entity Linking
1. 创建 `nlp/entity_linking.py`
2. 实现模糊匹配逻辑
3. 加载实体词典
4. 单元测试

### Week 2: FastAPI Basics
1. 创建 `api/main.py`
2. 实现 `/extract-entities` 端点
3. 测试NER集成
4. 添加错误处理

### Week 3: Neo4j & 4 Queries
1. 设置Neo4j连接
2. 实现4个固定查询
3. 测试端到端流程
4. 性能优化

### Week 4: RAG Integration & Testing
1. 创建RAG helper
2. 与Mert集成测试
3. 文档编写
4. 最终验收

---

## 📁 新建文件结构

```
api/
├── __init__.py
├── main.py                  # FastAPI application
├── neo4j_client.py          # Neo4j connection
├── schemas.py               # Pydantic models
└── queries/
    ├── supplier_queries.py  # Query 1
    ├── campaign_queries.py  # Query 2
    ├── skills_queries.py    # Query 3
    └── relationship_queries.py  # Query 4

nlp/
├── entity_linking.py        # 实体链接
├── entity_extraction.py     # RAG helper
└── ner_pipeline.py          # NER wrapper

tests/
├── test_entity_linking.py
├── test_api.py
└── test_integration.py
```

---

## 🧪 测试策略

### Unit Tests
```bash
pytest tests/test_entity_linking.py
pytest tests/test_api.py
```

### Integration Tests
```bash
# Test NER + Entity Linking
python tests/test_ner_linking_integration.py

# Test API endpoints
pytest tests/test_api_integration.py
```

### End-to-End Test
```bash
# Test full pipeline: Text → NER → Linking → Neo4j → Response
python tests/test_e2e.py
```

---

## 📊 验收标准

### Entity Linking
- [ ] 模糊匹配准确率 > 90%
- [ ] 支持所有8种实体类型
- [ ] 处理常见变体和拼写错误

### API Performance
- [ ] 响应时间 < 500ms (NER)
- [ ] 响应时间 < 200ms (固定查询)
- [ ] 并发请求支持 (10+ users)

### Integration
- [ ] 与Neo4j成功连接
- [ ] 与HEL-23 RAG集成测试通过
- [ ] 所有4个查询正常工作

---

## 🚦 依赖检查

### 需要等待的外部依赖：

1. **Neo4j数据库** (Sun - HEL-22)
   - 状态：询问Sun进度
   - 需要：数据库连接信息

2. **RAG系统接口** (Mert - HEL-23)
   - 状态：询问Mert需求
   - 需要：接口规范

### 可以独立开始的：

✅ Entity Linking实现  
✅ FastAPI基础框架  
✅ NER集成  
✅ 本地测试

---

## 💡 立即可做的事

### 今天：
1. ✅ 测试训练好的模型
2. ✅ 记录模型性能指标
3. 📝 开始编写 `entity_linking.py`

### 本周：
1. 实现实体链接基础功能
2. 创建FastAPI骨架
3. 联系Sun和Mert确认接口

### 下周：
1. 集成Neo4j
2. 实现4个查询
3. 端到端测试

---

## 📞 需要协调的事项

### 与Sun (HEL-22) 沟通：
- [ ] Neo4j数据库何时就绪？
- [ ] 连接信息和凭证
- [ ] 数据schema确认

### 与Mert (HEL-23) 沟通：
- [ ] RAG系统需要什么格式的实体？
- [ ] 接口调用方式
- [ ] 测试数据准备

---

## 🎯 下一个里程碑

**Target**: 2周内完成Entity Linking + FastAPI基础

**Deliverables**:
1. 工作的实体链接模块
2. 可测试的API端点
3. 与队友的集成计划

---

**准备好开始Phase 4了吗？** 🚀

先运行 `python nlp/scripts/test_trained_model.py` 验证模型！
