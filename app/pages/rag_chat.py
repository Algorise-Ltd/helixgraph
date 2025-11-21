import streamlit as st
import time

# -----------------------------
# RAG Chat Page (UI Only)
# -----------------------------
def rag_chat_page():

    st.title("💬 RAG Chat Interface")
    st.caption("Conversational interface for exploring graph insights. (UI Only)")

    st.markdown("---")

    # -----------------------------
    # Chat Session State
    # -----------------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []   # list of dicts: {role: "user"/"assistant", content: "..."}

    # -----------------------------
    # Example Questions (Inline Box)
    # -----------------------------
    with st.container():
        st.markdown(
            """
            <div class='box'>
            <h4>💡 Example Questions</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        cols = st.columns(2)
        examples = [
            "Which campaigns had the highest ROI?",
            "Show  campaign → order → product relationships.",
            "Which channels performed best in June?",
            "Summarize Dyson campaigns in Germany.",
        ]

        for i, q in enumerate(examples):
            if cols[i % 2].button(q):
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "(placeholder) This is where the RAG answer will appear."
                })

    st.markdown("---")

    # -----------------------------
    # Chat Message Rendering
    # -----------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class='box' style='border-color:#333; margin-bottom:10px;'>
                    <b>🧑 You:</b><br>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class='box' style='border-color:#555; background-color:#0F0F0F; margin-bottom:10px;'>
                    <b>🤖 Assistant:</b><br>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------
    # User Input Bar (Aligned)
    # -----------------------------
    st.markdown("---")

    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input("Ask a question:", key="rag_user_input")

    with col2:
        if st.button("Send"):
            if user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                with st.spinner("Thinking..."):
                    time.sleep(0.4)
                    response = "(placeholder) RAG model response will go here."

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

    # -----------------------------
    # Metadata Box
    # -----------------------------
    st.markdown("---")

    st.markdown(
        """
        <div class='box'>
            <h4>📘 Retrieval Metadata (Placeholder)</h4>
            <p>Displays retrieved nodes, relationships, similarity scores, etc.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.json({
        "retrieved_nodes": ["Campaign_A", "Product_4422", "Order_9912"],
        "similarity_scores": [0.88, 0.79, 0.76],
        "top_chunks": ["chunk_01", "chunk_05"],
        "note": "Mock metadata — real metadata comes from backend RAG API."
    })
