from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from pathlib import Path

# Force correct path
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.3-8b-instant",
    "mixtral-8x7b-32768"
]

def get_llm():
    for model in MODELS:
        try:
            llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name=model
            )
            # test call
            llm.invoke("hi")
            print(f"✅ Using model: {model}")
            return llm
        except Exception as e:
            print(f"❌ Model failed: {model}", e)

    raise Exception("No working model found")