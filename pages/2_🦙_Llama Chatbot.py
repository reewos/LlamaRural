import os
import io
import json
import streamlit as st 
import pandas as pd
from llama_index.llms.openllm import OpenLLM
from llama_index.core.llms import ChatMessage

from dotenv import load_dotenv
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="LlamaRural - Análisis de Cobertura",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role":'system', "content":'You are a helpfull assistant'}]

# Model configuration
llama_32_3B = OpenLLM(model="meta-llama/Llama-3.2-3B-Instruct-Turbo", api_key=os.environ['AIML_API_KEY'], api_base="https://api.aimlapi.com")
llama_31_405 = OpenLLM(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", api_key=os.environ['AIML_API_KEY'], api_base="https://api.aimlapi.com")

def analyze_chat_history(messages):
    # Basic analysis to determine which model to use

    messages_temp = messages[1:]
    messages_temp.append(
        ChatMessage(
            role="system",
            content="Based on the user's last message, determine whether to use 'meta-llama/Llama-3.2-3B-Instruct-Turbo' for general responses or 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo' for complex reasoning tasks. Please respond with only 'meta-llama/Llama-3.2-3B-Instruct-Turbo' or 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'."
        )
    )

    response = llama_32_3B.chat(messages_temp)
    # print(f"{response}")
    print(response)
    if "405B" in str(response).lower():
        return "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"

    return "meta-llama/Llama-3.2-3B-Instruct-Turbo"


def main():
    st.title("🌟 LlamaRural")
    st.subheader("🤖🦙 LLama Chatbot")

    file_path = 'resources/nearby.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("JSON loaded successfully:", data)
    else:
        print("File does not exist.")

            
    for message in st.session_state.chat_messages:
        if message["role"] != 'system':
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    print(st.session_state.chat_messages)

    if prompt := st.chat_input("What is up?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare the full history to send to the model
        full_history = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in st.session_state.chat_messages]

        # Analyze the chat history and select the appropriate model
        model_choice = analyze_chat_history(full_history)
        print(full_history)
        print(model_choice)

        # Send the full history to the appropriate model
        if model_choice == "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo":
            response = llama_31_405.chat(full_history)
            # print(response)
        else:
            response = llama_32_3B.chat(full_history)
            # print(response)

        response_text = str(response).replace('assistant: ', '', 1)
        # print(response['content'])

        if response_text == '':
            response_text = "Error: There are not enough tokens to complete it"

        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(f"{str(response_text).replace('assistant: ', '', 1)}\n\n**Model Used:** {model_choice}")

if __name__ == "__main__":
    main()