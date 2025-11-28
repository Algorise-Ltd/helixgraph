import pandas as pd

# CSV paths
camp = "data/processed/marketing/campaigns_summary.csv"
prod = "data/processed/marketing/products_v1.csv"
ordr = "data/processed/marketing/orders_v1.csv"

# Load
dfc = pd.read_csv(camp)
dfp = pd.read_csv(prod)
dfo = pd.read_csv(ordr)

# 1) Basic count checks
assert len(dfc) == 30, f"Expected 30 campaigns, got {len(dfc)}"
assert len(dfp) == 200, f"Expected 200 products, got {len(dfp)}"
assert len(dfo) == 500, f"Expected 500 orders, got {len(dfo)}"

# 2) Referential integrity
camp_ids = set(dfc["campaign_id"])
prod_ids = set(dfp["product_id"])
bad_c = dfo.loc[~dfo["campaign_id"].isin(camp_ids)]
bad_p = dfo.loc[~dfo["product_id"].isin(prod_ids)]
assert bad_c.empty, f"{len(bad_c)} orders reference missing campaign_id"
assert bad_p.empty, f"{len(bad_p)} orders reference missing product_id"

# 3) Date range validation
dfc["start_date"] = pd.to_datetime(dfc["start_date"])
dfc["end_date"] = pd.to_datetime(dfc["end_date"])
dfo["order_date"] = pd.to_datetime(dfo["order_date"])

merged = dfo.merge(
    dfc[["campaign_id", "start_date", "end_date"]],
    on="campaign_id",
    how="left"
)
viol = merged[
    (merged["order_date"] < merged["start_date"]) |
    (merged["order_date"] > merged["end_date"])
]
assert viol.empty, f"{len(viol)} orders fall outside campaign period"

print("[OK] CSV validation passed for counts, keys, and date ranges.")
