import streamlit as st
import requests

st.set_page_config(
    page_title="Accounting Agent",
    page_icon="📊",
    layout="centered"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            max-width: 900px;
        }
        .stChatMessage {
            border-radius: 12px;
        }
        .stChatInput textarea {
            font-size: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("## 📊 Accounting & Tax Agent")
    st.markdown(
        """
        **Scope**
        - 🇹🇳 Tunisian Tax Code  
        - 🌍 IFRS Standards  

        **Mode**
        - Retrieval-augmented  
        - No hallucinations  
        """
    )
    st.divider()
    st.markdown("🟢 Backend: Connected")

st.markdown("## 📑 Accounting & Tax Agent")
st.caption("Direct access to Tunisian tax law and IFRS standards. Ask precisely.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask a tax or accounting question…")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    try:
        with st.spinner("Thinking…"):
            response = requests.post(
                "http://localhost:8000/chat/",
                json={"query": prompt},
                timeout=30
            )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "No answer returned.")
            category = data.get("category", "general").upper()

            with st.chat_message("assistant"):
                st.markdown(answer)
                st.caption(f"📍 Classification: {category}")

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        else:
            st.error(f"Backend error {response.status_code}")

    except Exception:
        st.error("Backend unreachable. Connection error!")
