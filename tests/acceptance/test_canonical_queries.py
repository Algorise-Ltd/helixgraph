import os
import yaml
from pydantic import ValidationError
from docs.pydantic_schemas import (
    Q1Schema, Q2Schema, Q3Schema, Q4Schema, Q5Schema,
    Q6Schema, Q7Schema, Q8Schema, Q9Schema, Q10Schema,
    Q11Schema, Q12Schema
)

SCHEMA_MAP = {
    "Q001": Q1Schema, "Q002": Q2Schema, "Q003": Q3Schema, "Q004": Q4Schema,
    "Q005": Q5Schema, "Q006": Q6Schema, "Q007": Q7Schema, "Q008": Q8Schema,
    "Q009": Q9Schema, "Q010": Q10Schema, "Q011": Q11Schema, "Q012": Q12Schema,
}

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def test_fixtures_schema_compliance():
    """Validate each YAML fixture against its corresponding Pydantic schema."""
    for file in sorted(os.listdir(FIXTURE_DIR)):
        if not file.endswith(".yaml"):
            continue
        path = os.path.join(FIXTURE_DIR, file)
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        question_id = list(data.keys())[0]
        schema_cls = SCHEMA_MAP[question_id]
        rows = data[question_id]["expected"]["rows"]
        for row in rows:
            try:
                schema_cls(**row)
            except ValidationError as e:
                raise AssertionError(f"{file}: Schema validation failed\n{e}")
