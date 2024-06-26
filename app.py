import streamlit as st
import ollama

st.title("Java Tutor 🤖🚀")

# Initial prompt for the assistant to act as a software tester
role_prompt = {
    "role": "system",
    "content": ("You are an expert Java programming tutor.\n "
                "You're training the user for placement drive,so act like a real tutor and provide if \n"
                "- some tips in coding"
                "- Easy tricks in coding"
                "- Explain as a Tutor"
                "When a user provides Question of java code\n "
                "1) Analyze the Question\n"
                "2) Always Identify the Easiest solution code in java programming language\n"
                "3) Offer detailed explanation as points to resolve that question with code.\n "
                "4) More importantly explanation should be as points."
                "Provide clear, concise, and easiest solution in the following format:\n"
                "code:\n"
                "explanation as points:"
                "Sample output:")
}

if "messages" not in st.session_state:
    st.session_state["messages"] = [role_prompt, {"role": "assistant", "content": "How can I assist you?"}]
    st.session_state["model"] = "llama3"  # Default model

# Sidebar for model selection using a dropdown
model_choice = st.sidebar.selectbox("Choose a model", ("llama3", "codellama"))

if model_choice and model_choice != st.session_state["model"]:
    st.session_state["model"] = model_choice
    st.success(f"Switched to {model_choice} model")

# Write Message History
for msg in st.session_state.messages:
    if msg['role'] != 'system':  # Skip displaying the role prompt
        if msg['role'] == 'user':
            st.chat_message(msg['role'], avatar="🧑‍💻").write(msg['content'])
        else:
            st.chat_message(msg['role'], avatar='🤖').write(msg['content'])

# Generator for streamlit token
def generate_response():
    response = ollama.chat(model=st.session_state["model"], stream=True, messages=st.session_state.messages)
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token

if prompt := st.chat_input():
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["full_message"] = ""
    st.chat_message('assistant', avatar="🤖").write_stream(generate_response)
    st.session_state.messages.append({'role': 'assistant', 'content': st.session_state["full_message"]})
