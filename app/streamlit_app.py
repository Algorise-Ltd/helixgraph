import streamlit as st
from PIL import Image
import os
import base64

# ----------------------------------------------------------
# MUST be the first Streamlit command
# ----------------------------------------------------------
st.set_page_config(
    page_title="Algorise Graph App",
    page_icon="📊",
    layout="wide",
)

# ----------------------------------------------------------
# Dark Mode (Algorise Style)
# ----------------------------------------------------------
algorise_style = """
<style>

    /* Use Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Background */
    body, .stApp {
        background-color: #000000 !important;   /* Pure black */
        color: #FFFFFF !important;              /* Pure white font */
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        color: white !important;
    }

    /* Titles */
    h1, h2, h3, h4, h5 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: white !important;
    }

    /* Regular Text */
    p, li, div, span {
        font-family: 'Inter', sans-serif !important;
        color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1A1A1A !important;
        color: white !important;
        border-radius: 8px;
        border: 1px solid #333;
        padding: 10px 18px;
        font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        background-color: #333 !important;
        border-color: #666 !important;
    }

    /* Tables */
    .dataframe {
        color: white !important;
    }

    /* Streamlit Card / Box */
    .box {
        background-color: #0D0D0D !important;
        border: 1px solid #222 !important;
        border-radius: 10px;
        padding: 18px;
    }

</style>
"""

# Inject CSS
st.markdown(algorise_style, unsafe_allow_html=True)

# ----------------------------------------------------------
# Sidebar Logo
# ----------------------------------------------------------
logo_path = os.path.join("asset", "Algorise Logo.jpg")

if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.sidebar.image(logo, width=140)
else:
    st.sidebar.markdown("### **Algorise Graph App**")

st.sidebar.markdown("---")

# ----------------------------------------------------------
# Navigation
# ----------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Fixed Queries", "RAG Chat", "Bloom Guides"]
)

# ----------------------------------------------------------
# Home Page (with Logo + Title)
# ----------------------------------------------------------
if page == "Home":

    # Load Base64 logo
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        logo_base64 = base64.b64encode(open(logo_path, "rb").read()).decode()
    else:
        logo_base64 = None

    # Title section with logo
    if logo_base64:
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:15px; margin-top:10px;'>
                <img src="data:image/png;base64,{logo_base64}" width="70" />
                <h1 style='margin:0px; font-weight:600;'>Algorise Graph Intelligence</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.title("Algorise Graph Intelligence")

    st.write("Welcome to the Algorise Streamlit Application.")
    st.write("Use the sidebar to explore queries, RAG chat, and Bloom views.")

# ----------------------------------------------------------
# Other Pages
# ----------------------------------------------------------
elif page == "Fixed Queries":
    from pages.fixed_queries import fixed_query_page
    fixed_query_page()

elif page == "RAG Chat":
    from pages.rag_chat import rag_chat_page
    rag_chat_page()

elif page == "Bloom Guides":
    st.title("🌐 Neo4j Bloom Guide")
    st.write("This section explains how to create Bloom Perspectives.")
