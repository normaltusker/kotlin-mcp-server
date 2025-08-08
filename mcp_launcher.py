import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

models = {
    "openai": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4"
    },
    "openrouter": {
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "mistral/mistral-7b-instruct"
    },
    "gemini": {
        "provider": "gemini",
        "api_key": os.getenv("GEMINI_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "model": "gemini-pro"
    }
}

def start_chat(model_choice, project_path):
    if model_choice not in models:
        print("Invalid model choice. Options: openai, openrouter, gemini")
        return

    cfg = models[model_choice]
    print(f"Using model: {cfg['model']} from {cfg['provider']}")
    print(f"Project directory: {project_path}")

    os.environ["LLM_API_KEY"] = cfg["api_key"]
    os.environ["LLM_BASE_URL"] = cfg["base_url"]
    os.environ["LLM_MODEL"] = cfg["model"]

    subprocess.run(["aider", "--model", cfg["model"], "--cwd", project_path])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_launcher.py [openai|openrouter|gemini] [optional: /path/to/your/project]")
    else:
        project_path = sys.argv[2] if len(sys.argv) > 2 else os.getenv("PROJECT_PATH", "android-project")
        start_chat(sys.argv[1], project_path)
