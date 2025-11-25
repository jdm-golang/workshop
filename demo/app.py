import streamlit as st
import requests

st.title("Octanksson Turbines - Manufacturing Operations Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if query := st.chat_input("Ask a question:"):
    # Display user message in chat message container
    st.chat_message("user").markdown(query)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})

    try:
        response = requests.post("http://127.0.0.1:5001/ask", json={"query": query})
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        agent_response = data.get("response")

        # Display agent response in chat message container
        with st.chat_message("assistant"):
            st.markdown(agent_response)
        # Add agent response to chat history
        st.session_state.messages.append({"role": "assistant", "content": agent_response})

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the agent: {e}")
