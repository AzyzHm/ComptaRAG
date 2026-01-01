import streamlit as st
import requests

st.title("Accounting Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask me anything..."):
    # 1. Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Call FastAPI backend
    try:
        backend_url = "http://localhost:8000/chat"
        payload = {"message": prompt, "history": []}
        
        with st.spinner("Thinking..."):
            response = requests.post(backend_url, json=payload)
            response.raise_for_status()
            data = response.json()
            answer = data["response"]

        # 3. Display assistant response
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")