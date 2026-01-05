import os
from dotenv import load_dotenv
import pathlib

print("Current working directory:", os.getcwd())
print("Current file location:", __file__)

# Try different methods to load .env
print("\n=== Method 1: Direct path ===")
env_path = pathlib.Path(__file__).parent / '.env'
print("Env file path:", env_path)
print("Env file exists:", env_path.exists())
if env_path.exists():
    load_dotenv(env_path)
    print("API Key loaded:", os.getenv("GEMINI_API_KEY")[:10] if os.getenv("GEMINI_API_KEY") else "None")

print("\n=== Method 2: Current directory ===")
load_dotenv()
print("API Key loaded:", os.getenv("GEMINI_API_KEY")[:10] if os.getenv("GEMINI_API_KEY") else "None")

print("\n=== Method 3: Absolute path ===")
abs_env_path = pathlib.Path.cwd() / '.env'
print("Absolute env path:", abs_env_path)
print("Absolute env exists:", abs_env_path.exists())
if abs_env_path.exists():
    load_dotenv(abs_env_path)
    print("API Key loaded:", os.getenv("GEMINI_API_KEY")[:10] if os.getenv("GEMINI_API_KEY") else "None")
