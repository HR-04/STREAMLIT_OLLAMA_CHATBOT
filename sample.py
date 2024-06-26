import streamlit as st
import ollama
import time
import random


st.title("Java Tutor🤖🚀")
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
    st.session_state["last_tip_update"] = time.time()
    st.session_state["update_interval"] = 25  # 30 seconds

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

# Timer display using streamlit.empty()
tip_placeholder = st.sidebar.empty()
timer_placeholder = st.sidebar.empty()

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

# Main loop to update tips every 30 seconds and display countdown timer
while True:
    current_time = time.time()
    
    # Update tips every 30 seconds
    if current_time - st.session_state["last_tip_update"] > st.session_state["update_interval"]:
        update_tips()
        st.session_state["last_tip_update"] = current_time

    # Calculate time remaining for the next update
    time_remaining = int(st.session_state["update_interval"] - (current_time - st.session_state["last_tip_update"]))
    
    # Display the countdown timer and tips
    timer_placeholder.markdown(f"""
    <div style="font-size: 20px; font-weight: bold; margin: 20px 0;">
        Next update in: {time_remaining} seconds
    </div>
    """, unsafe_allow_html=True)
    
    tip_placeholder.markdown(f"""
    <div style="background-color: black; color: white; padding: 20px; border-radius: 10px;">
        {st.session_state["current_tip"]}
    </div>
    """, unsafe_allow_html=True)

    # Sleep for a short period to prevent CPU overuse
    time.sleep(1)
