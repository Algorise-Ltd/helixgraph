import pandas as pd
import numpy as np

path = r"G:\내 드라이브\0. Algorise\helixgraph\data\processed\marketing\campaigns_summary.csv"

print(f"\n[INFO] Checking CSV integrity: {path}\n")

# 파일 로드
try:
    df = pd.read_csv(path)
except Exception as e:
    print(f"[FAIL] Unable to load CSV: {e}")
    raise SystemExit(1)

# 기본 정보 출력
print("[INFO] Basic Info")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print("Columns:", list(df.columns))
print()

# 결측치 검사
nulls = df.isnull().sum()
if nulls.sum() == 0:
    print("[OK] No missing values detected.")
else:
    print("[WARN] Missing values found:")
    print(nulls[nulls > 0])
print()

# 숫자형 컬럼 유효성 검사
numeric_cols = ["budget", "actual_spend", "impressions", "clicks", "views", "sessions", "conversions", "revenue"]
numeric_cols = [c for c in numeric_cols if c in df.columns]

if numeric_cols:
    for col in numeric_cols:
        invalid = df[df[col] < 0]
        if len(invalid) > 0:
            print(f"[WARN] {col}: {len(invalid)} negative values found")
    print("[OK] Numeric columns checked for negative values.\n")
else:
    print("[WARN] No numeric columns found to validate.\n")

# 중복 campaign_id 확인
if df["campaign_id"].duplicated().any():
    print("[WARN] Duplicate campaign_id detected:")
    print(df[df["campaign_id"].duplicated()]["campaign_id"].values)
else:
    print("[OK] All campaign_id values are unique.\n")

# 통계 요약
print("[INFO] Quick numeric summary:")
print(df.describe(include=[np.number]))

print("\n[FINISHED] CSV integrity check complete.")
