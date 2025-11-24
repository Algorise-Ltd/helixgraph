# HelixGraph 🔷

Multi‑domain enterprise knowledge graph that will touch bases with all of your experiences – Marketing/eCommerce + Procurement/Logistics + HR – that powers cross‑domain queries and an LLM‑assisted demo for contextual answers.

## 🚀 Quick Start

### 1. Clone & Setup Virtual Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Helixgraph

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model (for NER)
python -m spacy download en_core_web_trf
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

### 4. Verify Setup

```bash
# Run tests (once implemented)
pytest

# Start API server (HEL-21)
uvicorn api.main:app --reload

# Access API docs at: http://localhost:8000/docs
```

## 📂 Project Structure

```
Helixgraph/
├── nlp/              # Named Entity Recognition (HEL-21)
├── api/              # REST API endpoints (HEL-21)
├── data_pipeline/    # Data ingestion (HEL-22)
├── rag/              # RAG system (HEL-23)
└── docs/             # Documentation
```

## 👥 Team & Tasks

- **Ivan (HEL-21)**: NER Model + Entity Linking + FastAPI
- **Sun (HEL-22)**: Data Pipeline + Neo4j Integration
- **Mert (HEL-23)**: RAG System + LLM Integration

## 🔧 Development Workflow

1. Pull latest changes: `git pull origin main`
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m "descriptive message"`
4. Push and create PR: `git push origin feature/your-feature`

## 📝 Notes

- Always activate virtual environment before working
- Never commit `.env` or `venv/` directories
- Update `requirements.txt` if adding new dependencies
- Document major changes in commit messages
