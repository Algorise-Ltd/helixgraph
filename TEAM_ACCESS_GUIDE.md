# HelixGraph Team Access Guide 👥

**项目：** HelixGraph Knowledge Graph & NER System  
**更新日期：** 2024年11月23日

---

## 🗄️ Neo4j数据库访问

### 数据库信息
- **平台：** Neo4j Aura Free
- **实例名称：** Helixgraph
- **数据库：** neo4j

### 如何访问

#### 方法1：通过Neo4j控制台（推荐）
1. 访问 https://console.neo4j.io
2. 使用你的邮箱登录（需要Ivan邀请你）
3. 应该能看到 "Helixgraph" 实例
4. 点击 **"Query"** 打开Neo4j Browser
5. 开始查询和管理数据！

#### 方法2：直接连接凭证（已被邀请的成员）
```
Connection URI: neo4j+s://351353ad.databases.neo4j.io
Database: neo4j
```
使用你自己的账号密码登录。

---

## 👥 团队成员角色

### Ivan（你）- NER & FastAPI开发
**负责：**
- ✅ NER模型训练和维护
- ✅ FastAPI endpoints开发
- ✅ Entity Linking功能
- ✅ 系统集成

**访问权限：**
- Neo4j: Admin
- FastAPI: 全部控制

---

### Sun - Marketing数据管理
**负责：**
- Campaigns数据
- Brands/Products数据
- Marketing analytics支持

**需要访问：**
1. **Neo4j数据库（Editor权限）**
   - 添加/修改campaigns
   - 管理brands数据
   - 验证数据质量

2. **（可选）FastAPI查询endpoints**
   - 测试marketing相关查询
   - 验证campaign数据API

**数据位置：**
```
Neo4j节点类型：
- Product (brands)
- Campaign

JSON源文件：
- data/source/marketing/brands.json
- data/source/marketing/campaigns.json
```

---

### Mert - RAG系统集成
**负责：**
- Procurement数据
- RAG系统开发
- Entity Extraction集成

**需要访问：**
1. **FastAPI - Entity Extraction Helper** ⭐重要
   ```python
   from nlp.entity_extraction import extract_entities_for_rag
   
   # Mert在RAG系统中使用
   question = "Tell me about Acme Corp's performance"
   entities = extract_entities_for_rag(question)
   # Returns: {'Supplier': 'Acme Corp'}
   ```

2. **FastAPI endpoints文档**
   - `/docs` - 查看所有可用API
   - `/api/extract-entities` - NER提取
   - `/api/link-entities` - Entity Linking
   - `/api/v1/*` - Fixed query endpoints

3. **（可选）Neo4j只读访问**
   - 了解数据结构
   - 设计RAG查询逻辑

**数据位置：**
```
Neo4j节点类型：
- Supplier
- Contract
- PurchaseOrder

JSON源文件：
- data/source/procurement_mert/suppliers.json
- data/source/procurement_mert/contracts.json
```

---

## 🚀 FastAPI访问

### 当前状态
- **环境：** 本地开发（Ivan的机器）
- **地址：** http://localhost:8000
- **状态：** ✅ 运行中（仅本地可访问）

### 访问方式

#### 选项1：等待云端部署（推荐）
- Ivan会将API部署到云端
- 届时会提供公共URL
- 所有团队成员可访问

#### 选项2：本地运行（适合开发）
如果你需要本地测试：

```bash
# 1. Clone项目（从Google Drive或Git）
cd "/path/to/Helixgraph"

# 2. 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建.env文件（向Ivan要Neo4j凭证）
echo "NEO4J_URI=..." > .env
echo "NEO4J_USERNAME=..." >> .env
echo "NEO4J_PASSWORD=..." >> .env

# 5. 启动API
uvicorn api.main:app --reload --port 8000

# 6. 访问文档
open http://localhost:8000/docs
```

#### 选项3：临时公共URL（测试用）
- Ivan可以用ngrok创建临时公共URL
- 适合短期测试和演示
- URL会在24小时后失效

---

## 📚 API文档

### 主要Endpoints

#### 1. NER & Entity Linking
```
POST /api/extract-entities
- 从文本中提取实体
- 输入: {"text": "Invoice INV-123 from Acme Corp"}
- 输出: 识别的entities列表

POST /api/link-entities  
- 提取并链接到标准形式
- 输入: {"text": "Nike campaign"}
- 输出: 链接到知识图谱的entities
```

#### 2. Fixed Query Endpoints
```
GET /api/v1/suppliers/top-roi
- 按ROI排序供应商
- 参数: min_roi, limit, sort

GET /api/v1/campaigns/{id}/team-gaps
- 分析campaign团队技能缺口

GET /api/v1/products/high-conversion
- 高转化率产品
- 参数: min_conversion, category

GET /api/v1/suppliers/{id}/risk
- 供应商风险评估
```

### 完整文档
当API运行时，访问：
- **交互式文档：** http://api-url/docs
- **ReDoc格式：** http://api-url/redoc

---

## 🔧 Entity Extraction Helper（给Mert）

### 在RAG系统中使用

```python
# 文件: nlp/entity_extraction.py

from nlp.entity_extraction import extract_entities_for_rag

# 示例1：基础使用
question = "What campaigns is Acme Corp funding?"
entities = extract_entities_for_rag(question)
print(entities)
# 输出: {'Supplier': 'Acme Corp'}

# 示例2：多个实体
question = "Show me Nike campaign performance"  
entities = extract_entities_for_rag(question)
print(entities)
# 输出: {'Product': 'Nike', 'type': 'Campaign'}

# 示例3：在RAG pipeline中
def enhance_rag_with_entities(user_question):
    # 1. 提取实体
    entities = extract_entities_for_rag(user_question)
    
    # 2. 根据实体类型构建Neo4j查询
    if 'Supplier' in entities:
        context = query_supplier_info(entities['Supplier'])
    elif 'Campaign' in entities:
        context = query_campaign_info(entities['Campaign'])
    
    # 3. 将context和问题发给LLM
    answer = llm_generate(question, context)
    return answer
```

### Entity类型映射
```python
NER标签 → 图谱节点类型：
- SUPPLIER → Supplier
- PRODUCT → Product  
- CAMPAIGN → Campaign
- CONTRACT → Contract
- PO → PurchaseOrder
- INVOICE → Invoice
- ROLE → Employee
- SKILL → Skill
```

---

## 🛠️ 数据管理

### 添加新数据

#### 通过Neo4j Browser（推荐）
```cypher
// 添加新Campaign
CREATE (:Campaign {
  id: "NEW_CAMP_001",
  name: "New Campaign Name",
  brand: "Brand Name",
  budget: 100000.0,
  status: "active"
});

// 添加新Supplier
CREATE (:Supplier {
  id: "SUP-999",
  name: "New Supplier Inc",
  category: "Technology"
});
```

#### 通过JSON文件（批量）
1. 更新对应的JSON文件
2. 通知Ivan重新导入
3. 或使用Python导入脚本

---

## 📞 需要帮助？

### 联系方式
- **Ivan** - NER/API问题
- **Sun** - Marketing数据问题  
- **Mert** - RAG集成问题

### 常见问题

**Q: Neo4j连接失败？**
A: 检查网络，可能需要VPN或不同网络环境。使用Neo4j Browser（网页版）通常可以绕过。

**Q: API访问不了？**
A: 确认API已部署到云端，或联系Ivan获取临时访问URL。

**Q: 数据导入问题？**
A: 参考 `NEO4J_MANUAL_IMPORT_GUIDE.md` 或联系Ivan。

**Q: Entity Extraction不准确？**
A: 提供具体例子给Ivan，可能需要重新训练模型。

---

## 📊 项目状态

### 已完成 ✅
- NER模型训练（F1 = 0.9979）
- Entity Linking实现
- FastAPI基础架构
- 4个Fixed Query endpoints
- Neo4j Aura实例创建
- Mock数据系统

### 进行中 🔄  
- Neo4j连接问题解决（网络限制）
- 完整数据导入
- API云端部署

### 待完成 ⏳
- API集成测试
- RAG系统集成（与Mert协调）
- 生产环境部署

---

**最后更新：** 2024年11月23日 23:39  
**维护者：** Ivan

有问题随时在团队群里问！🚀
