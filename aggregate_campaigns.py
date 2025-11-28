import pandas as pd

# 1. Load raw ad-group level data
df = pd.read_csv("data/processed/marketing/campaigns_v1.csv")

# 2. Clean column names (remove whitespace)
df.columns = df.columns.str.strip()

# 3. 피벗 집계 설정
# 숫자형 컬럼은 합계(sum), 나머지는 대표값(first) 사용
numeric_cols = [
    "budget", "actual_spend", "impressions", "clicks", "views",
    "sessions", "conversions", "revenue"
]

# 만약 숫자 컬럼 중 일부가 없을 수도 있으니 존재 여부로 필터링
numeric_cols = [c for c in numeric_cols if c in df.columns]

# 4. Pivot (groupby 대신 pivot_table 사용)
agg_dict = {col: "sum" for col in numeric_cols}
text_cols = ["campaign_name", "brand_name", "category", "country", "objective", "currency"]
for col in text_cols:
    if col in df.columns:
        agg_dict[col] = "first"

df_summary = df.pivot_table(
    index="campaign_id",
    values=list(agg_dict.keys()),
    aggfunc=agg_dict,
    fill_value=0
).reset_index()

# 5. Export summarized dataset
output_path = "data/processed/marketing/campaigns_summary.csv"
df_summary.to_csv(output_path, index=False)

print(f"[OK] Pivoted to {len(df_summary)} campaigns and saved as {output_path}")