import streamlit as st
import ollama
import time
from datetime import datetime
import random
from threading import Timer

# Initialize session state for messages and model
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "system",
        "content": ("You are an expert Java programming tutor.\n"
                    "You're training the user for placement drive, so act like a real tutor and provide:\n"
                    "- Some tips in coding\n"
                    "- Easy tricks in coding\n"
                    "- Explain as a Tutor\n"
                    "When a user provides a question on Java code:\n"
                    "1) Analyze the question\n"
                    "2) Identify the easiest solution in Java programming language\n"
                    "3) Offer a detailed explanation as points\n"
                    "4) Provide clear, concise, and easiest solutions in the following format:\n"
                    "code:\n"
                    "explanation as points:\n"
                    "Sample output:")
    }, {"role": "assistant", "content": "How can I assist you?"}]
    st.session_state["model"] = "llama3"  # Default model
    st.session_state["current_tip"] = "💡 Tip: Use meaningful variable names to make your code more readable."

# Sidebar for model selection using a dropdown
model_choice = st.sidebar.selectbox("Choose a model", ("llama3", "codellama"))

if model_choice and model_choice != st.session_state["model"]:
    st.session_state["model"] = model_choice
    st.success(f"Switched to {model_choice} model")

# Function to update the tips and tricks
def update_tips():
    tips_list = [
        "💡 Tip: Use meaningful variable names to make your code more readable.",
        "💡 Tip: Always close resources like files and network connections in a finally block or use try-with-resources.",
        "🚀 Trick: Use StringBuilder for concatenating strings in loops for better performance.",
        "🤖 Info: Did you know? Java was originally called Oak, after an oak tree that stood outside James Gosling's office.",
        "😂 Joke: Why do Java developers wear glasses? Because they don't C#.",
        "💡 Tip: Prefer composition over inheritance for better flexibility.",
        "🚀 Trick: Use lambda expressions to simplify your code and make it more readable.",
        "🤖 Info: The Java mascot, Duke, was created by Joe Palrang, an artist who worked on Shrek.",
        "😂 Joke: Why did the Java developer quit his job? Because he didn't get arrays (a raise).",
        "💡 Tip: Always use proper indentation to make your code more readable and maintainable."
    ]
    st.session_state["current_tip"] = random.choice(tips_list)
    st.rerun()

# Display tips and tricks in the sidebar
st.sidebar.subheader("Java Tips, Tricks, and Jokes")
st.sidebar.write(st.session_state["current_tip"])

# Function to display current time
def display_time():
    return datetime.now().strftime('%H:%M:%S')

# Placeholder for time display
time_placeholder = st.empty()

# Loop to update time every second
while True:
    time_placeholder.text(display_time())
    time.sleep(1)

# Function to generate tips dynamically using the model
def generate_tip():
    prompt = {
        "role": "user",
        "content": "Provide a Java coding tip, trick, or joke."
    }
    response = ollama.chat(model=st.session_state["model"], messages=[prompt])
    st.session_state["current_tip"] = response['choices'][0]['message']['content']
    st.rerun()

# Write Message History
for msg in st.session_state.messages:
    if msg['role'] != 'system':  # Skip displaying the role prompt
        if msg['role'] == 'user':
            st.chat_message(msg['role'], avatar="🧑‍💻").write(msg['content'])
        else:
            st.chat_message(msg['role'], avatar='🤖').write(msg['content'])

# Generator for Streamlit token
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

# Display the current time in the sidebar
with st.sidebar:
    st.markdown(display_timer(), unsafe_allow_html=True)

# Set a timer to update the tips every 2 minutes
if "timer" not in st.session_state:
    st.session_state["timer"] = Timer(120.0, generate_tip)
    st.session_state["timer"].start()

# Update tips immediately if running for the first time
if st.session_state["current_tip"] == "":
    generate_tip()
