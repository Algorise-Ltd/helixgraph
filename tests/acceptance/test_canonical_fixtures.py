import yaml
from pathlib import Path
from docs import pydantic_schemas as S

SCHEMA_MAP = {
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

FIXTURE_DIR = Path("tests/fixtures")

def test_each_fixture_validates_against_schema():
    for path in sorted(FIXTURE_DIR.glob("q*.yaml")):
        data = yaml.safe_load(path.read_text())
        (qid, payload), = data.items()
        schema = SCHEMA_MAP[qid]

        for row in payload["expected"]["rows"]:
            schema(**row)
