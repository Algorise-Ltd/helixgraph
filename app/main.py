from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, Dict, Any
import os, yaml
from pathlib import Path

# --- config & auth (env-based) ---
API_KEY = os.getenv("API_KEY", "dev-key")  # will be overridden by .env in real deploy

def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

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
def run_question(qid: str, params: Dict[str, Any] | None = None):
    qs = load_questions()
    if qid not in qs:
        raise HTTPException(404, f"{qid} not found")
    # minimal stub response – replace with real logic in later steps
    return {"id": qid, "status": "not_implemented_yet"}
