# HelixGraph Testing Guide

Complete guide for running tests in the HelixGraph project.

## Test Files

### 1. Schema Validation Tests
**File:** `tests/test_hr_schema.py`

Tests Pydantic data validation for HR schemas:
- Employee model validation (5 tests)
- Skill model validation (4 tests)
- EmployeeSkill model validation (5 tests)
- Data integrity checks (3 tests)

**Run:**
```bash
python tests/test_hr_schema.py
```

**Expected Output:**
- 17 tests, 100% pass rate
- Execution time: <1 second

---

### 2. ETL End-to-End Tests
**File:** `tests/test_etl_end_to_end.py`

Tests complete ETL pipeline with Neo4j:
- Connection tests
- Data loading and validation
- Full load cycle with timing
- Data integrity verification

**Run:**
```bash
python tests/test_etl_end_to_end.py
```

**Expected Output:**
- All tests pass
- Load time: ~1-2 seconds
- Verifies 262 nodes, 2,065 relationships

---

### 3. Complete Test Suite
**File:** `scripts/run_all_tests.py`

Runs all tests with comprehensive reporting:
- Environment validation
- Schema validation tests
- ETL end-to-end tests
- Performance metrics

**Run:**
```bash
python scripts/run_all_tests.py
```

**Expected Output:**
- 2/2 test suites passed
- Total time: ~2-3 seconds

---

## Prerequisites

### Environment Setup
1. Create `.env` file with Neo4j credentials:
```bash
cp .env.example .env
# Edit .env with your Neo4j credentials
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate test data:
```bash
python scripts/generate_hr_data.py
```

### Verify Environment
```bash
python scripts/test_env_config.py
```

---

## Test Results

### Schema Validation
```
Total Tests:  17
Passed:       17 ✓
Failed:       0 ✗
Success Rate: 100.0%
```

### ETL End-to-End
```
Performance Metrics:
  Clear time:    0.06s
  Load time:     0.75s
  Verify time:   0.07s
  Total time:    1.18s

Dataset:
  Employees:     200
  Skills:        50
  Departments:   6
  Locations:     6
  Relationships: 2,065
```

---

## Utility Scripts

### Check Database Statistics
View current Neo4j database state:
```bash
python scripts/check_neo4j_stats.py
```

### Clear Database
Clear all data from Neo4j:
```bash
python scripts/clear_neo4j.py
```

### Reload Database
Clear and reload all HR data:
```bash
python scripts/reload_with_clear.py
```

---

## Test Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| Employee Schema | 5/5 tests | ✅ Complete |
| Skill Schema | 4/4 tests | ✅ Complete |
| EmployeeSkill Schema | 5/5 tests | ✅ Complete |
| Data Integrity | 3/3 tests | ✅ Complete |
| ETL Connection | All tests | ✅ Complete |
| ETL Loading | All tests | ✅ Complete |
| ETL Performance | <60s target | ✅ Complete (1.18s) |

---

## Continuous Integration

For CI/CD pipelines, use:
```bash
python scripts/run_all_tests.py
```

Exit codes:
- `0`: All tests passed
- `1`: One or more tests failed

---

## Troubleshooting

### Connection Errors
1. Verify `.env` file exists
2. Check Neo4j credentials
3. Test connection:
```bash
python scripts/test_env_config.py
```

### Data Validation Errors
1. Regenerate data:
```bash
python scripts/generate_hr_data.py
```

2. Verify data files:
```bash
python scripts/validate_data.py
```

### Performance Issues
- Expected load time: 1-2 seconds
- If slower, check:
  - Neo4j instance performance
  - Network connection
  - Batch size settings

---

## Performance Benchmarks

| Operation | Expected Time | Actual |
|-----------|---------------|--------|
| Schema Tests | <1s | ~0.5s |
| Clear Database | <1s | ~0.06s |
| Load Data | <5s | ~0.75s |
| Verify Data | <1s | ~0.07s |
| Full Test Suite | <10s | ~2.38s |

---

**Last Updated:** 2025-10-12  
**Status:** All tests passing ✅

