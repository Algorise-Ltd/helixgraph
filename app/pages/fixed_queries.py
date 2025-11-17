import streamlit as st
import pandas as pd
import json
import os

# -----------------------------
# Corrected Data Folder Path
# -----------------------------
# Streamlit app is inside: helixgraph/app/
# Data folder is:          helixgraph/data/processed/marketing/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # helixgraph/
DATA_DIR = os.path.join(BASE_DIR, "data", "processed", "marketing")

def load_campaigns():
    path = os.path.join(DATA_DIR, "campaigns_v1.csv")
    return pd.read_csv(path)

def load_products():
    path = os.path.join(DATA_DIR, "products_v1.csv")
    return pd.read_csv(path)

def load_channels():
    path = os.path.join(DATA_DIR, "channels.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Fixed Query UI Page
# -----------------------------
def fixed_query_page():

    st.title("📌 Fixed Query Explorer (UI Only)")
    st.write("Explore marketing data using predefined UI-only queries (no Cypher yet).")

    # Load Data
    try:
        campaigns = load_campaigns()
        products = load_products()
        channels = load_channels()
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return

    st.markdown("---")
    st.subheader("Choose a Query Type")

    query_options = [
        "Find Campaigns by Category",
        "Find Campaigns by Channel",
        "Find Campaigns by Brand",
        "Find Products by Brand",
        "List Channels and Subcategories",
    ]

    query_choice = st.selectbox("Select a Query", query_options)
    st.markdown("---")

    # ====================================================
    # 1) Find Campaigns by Category
    # ====================================================
    if query_choice == "Find Campaigns by Category":
        st.subheader("📂 Filter Campaigns by Category")

        categories = sorted(campaigns["category"].dropna().unique())
        selected = st.selectbox("Select Category", categories)

        if st.button("Run Query"):
            result = campaigns[campaigns["category"] == selected]
            st.dataframe(result, use_container_width=True)

    # ====================================================
    # 2) Find Campaigns by Channel
    # ====================================================
    elif query_choice == "Find Campaigns by Channel":
        st.subheader("📡 Filter by Channel")

        channel_names = [c["name"] for c in channels]
        selected = st.selectbox("Select Channel", channel_names)

        if st.button("Run Query"):
            result = campaigns[campaigns["channel"] == selected]
            st.dataframe(result, use_container_width=True)

    # ====================================================
    # 3) Find Campaigns by Brand
    # ====================================================
    elif query_choice == "Find Campaigns by Brand":
        st.subheader("🏷️ Filter Campaigns by Brand")

        brands = sorted(campaigns["brand_name"].dropna().unique())
        selected = st.selectbox("Select Brand", brands)

        if st.button("Run Query"):
            result = campaigns[campaigns["brand_name"] == selected]
            st.dataframe(result, use_container_width=True)

    # ====================================================
    # 4) Find Products by Brand
    # ====================================================
    elif query_choice == "Find Products by Brand":
        st.subheader("🛒 Filter Products by Brand")

        product_brands = sorted(products["brand"].dropna().unique())
        selected = st.selectbox("Select Brand", product_brands)

        if st.button("Run Query"):
            result = products[products["brand"] == selected]
            st.dataframe(result, use_container_width=True)

    # ====================================================
    # 5) Display channels.json full structure
    # ====================================================
    elif query_choice == "List Channels and Subcategories":
        st.subheader("📡 Channels Overview")

        for ch in channels:
            st.markdown(f"### **{ch['name']}** ({ch['type']})")
            st.write("Subcategories:")
            st.write(", ".join(ch["subcategories"]))
            st.markdown("---")
