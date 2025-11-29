from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, Dict, Any
import os, yaml
from pathlib import Path
from pydantic import BaseModel

from docs import pydantic_schemas as S  # NEW

SCHEMA_MAP = {  # NEW — 按你的 Q001…Q012 命名
    "Q001": S.Q1Schema,
    "Q002": S.Q2Schema,
    "Q003": S.Q3Schema,
    "Q004": S.Q4Schema,
    "Q005": S.Q5Schema,
    "Q006": S.Q6Schema,
    "Q007": S.Q7Schema,
    "Q008": S.Q8Schema,
    "Q009": S.Q9Schema,
    "Q010": S.Q10Schema,
    "Q011": S.Q11Schema,
    "Q012": S.Q12Schema,
}

# --- config & auth (env-based) ---
API_KEY = os.getenv("API_KEY", "dev-key")  # will be overridden by .env in real deploy

def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

class RunParams(BaseModel):
    top_n: int | None = None

# --- data sources ---
YAML_PATH = Path("docs/canonical_questions.yaml")

app = FastAPI(
    title="HelixGraph API",
    description="Product & API Foundation – canonical questions",
    version="0.1.0",
)

def load_questions() -> Dict[str, Any]:
    data = yaml.safe_load(YAML_PATH.read_text())
    return {q["id"]: q for q in data["questions"]}

# --- endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/schema/{qid}", dependencies=[Depends(require_api_key)])
def get_schema(qid: str):
    schema_cls = SCHEMA_MAP.get(qid)
    if not schema_cls:
        raise HTTPException(status_code=404, detail=f"No schema defined for {qid}")
    return schema_cls.schema()

@app.get("/questions", dependencies=[Depends(require_api_key)])
def list_questions():
    qs = load_questions()
    # return id + text only for now
    return [{"id": k, "text": v["text"], "priority": v.get("priority")} for k, v in qs.items()]

@app.get("/questions/{qid}", dependencies=[Depends(require_api_key)])
def get_question(qid: str):
    qs = load_questions()
    if qid not in qs:
        raise HTTPException(404, f"{qid} not found")
    return qs[qid]

# stub: will later return computed results validated by Pydantic schemas
@app.post("/run/{qid}", dependencies=[Depends(require_api_key)])
def run_question(qid: str, params: RunParams | None = None):
    """
    Stub: return example rows that conform to the Pydantic model.
    Replace this with real logic later.
    """
    schema_cls = SCHEMA_MAP.get(qid)
    if not schema_cls:
        raise HTTPException(status_code=404, detail=f"No schema defined for {qid}")

    # build one example row using field types
    example = {}
    for name, field in schema_cls.__fields__.items():
        t = field.type_
        example[name] = 0 if t in (int, float) else "" if t is str else None

    return [schema_cls(**example).dict()]
