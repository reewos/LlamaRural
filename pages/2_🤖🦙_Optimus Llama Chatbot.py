import os
import io
import json
import streamlit as st 
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="LlamaRural - Análisis de Cobertura",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ['AIML_API_KEY'],
    base_url="https://api.aimlapi.com"
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": 'system', "content": 'You are a helpful assistant'}]

def analyze_chat_history(messages):
    # Basic analysis to determine which model to use
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
        messages=[
            *messages,
            {
                "role": "system",
                "content": "Based on the user's last message, determine whether to use 'Llama-3.2-3B' for general responses or 'Meta-Llama-3.1-405B' for complex tasks. Please respond with only 'Llama-3.2-3B' or 'Meta-Llama-3.1-405B'."
            }
        ]
    )
    
    model_choice = response.choices[0].message.content

    if "405b" in model_choice.lower():
        return "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
    return "meta-llama/Llama-3.2-3B-Instruct-Turbo"


def need_location_data(messages):
    # Basic analysis to determine which model to use
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
        messages=[
            *messages,
            {
                "role": "system",
                "content": "Analyzes the messages and determines if it requires location data. The question is considered connectivity-relevant if it mentions connection issues or if the user is looking for assistance finding a nearby location. Answer 'Yes' if the question requires location data and 'No' if it does not."
            }
        ]
    )
    
    choice = response.choices[0].message.content

    if "yes" in choice.lower():
        return True
    return False

def get_chat_response(messages, model):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting response: {e}")
        return "Error: There are not enough tokens to complete it"

def main():
    st.title("🌟 LlamaRural")
    st.subheader("🤖🦙 Optimus LLama Chatbot")

    data_location = None

    file_path = 'resources/nearby.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data_location = json.load(file)
            # print("JSON loaded successfully:", data)
    else:
        print("File does not exist.")
            
    # Display chat history
    for message in st.session_state.chat_messages:
        if message["role"] != 'system':
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Select appropriate model
        model_choice = analyze_chat_history(st.session_state.chat_messages)  # Exclude the last message
        print(f"Selected model: {model_choice}")

        needed = need_location_data(st.session_state.chat_messages) 
        print(f"Need Location: {needed}")
        if needed and data_location is not None:
            # Add assistant response to chat
            st.session_state.chat_messages.append({"role": "system", "content": f"Location data: \n {data_location}"})

        # Get response from the model
        response_text = get_chat_response(st.session_state.chat_messages, model_choice)

        # Add assistant response to chat
        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(f"{response_text}\n\n**Model Used:** {model_choice}")

if __name__ == "__main__":
    main()