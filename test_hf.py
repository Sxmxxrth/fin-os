import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv("HF_TOKEN")

models_to_test = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Meta-Llama-3-8B-Instruct"
]

for model in models_to_test:
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": "Write a python hello world"}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"[{model}] Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS!")
            break
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"[{model}] Failed: {e}")
