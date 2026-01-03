import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="Accounting Agent", page_icon="📑")
st.title("📑 Accounting & Tax Agent")
st.caption("Direct access to Tunisian Tax Code and IFRS standards.")

# 2. Session State for UI messages only (not sent to backend)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history for the UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Chat Input
if prompt := st.chat_input("Ask your financial or legal question..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        backend_url = "http://localhost:8000/chat/" 
        payload = {"query": prompt} 
        
        with st.spinner("Thinking..."):
            response = requests.post(backend_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "No answer found.")
                category = data.get("category", "General")

                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.caption(f"📍 Classification: {category.upper()}")
                
                # Save to UI history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")