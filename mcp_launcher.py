import os
import subprocess
import json
from shutil import which
from dotenv import load_dotenv


if not os.path.exists(".env"):
    with open(".env", "w") as env_file:
        env_file.write("# Automatically created .env file\n")

if not os.path.exists(".env"):
    with open(".env", "w") as env_file:
        env_file.write("# Automatically created .env file\n")

load_dotenv()

def ensure_env_var(var_name, prompt_label):
    value = os.getenv(var_name)
    if not value:
        value = input(f"🔐 Enter value for {prompt_label} ({var_name}): ").strip()
        with open(".env", "a") as f:
            f.write(f"{var_name}={value}\n")
        os.environ[var_name] = value
    return value



CONFIG_PATH = os.path.expanduser("~/.kotlin_mcp_config.json")

models = {
    "openai": {
        "provider": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_API_BASE",
        "default_model": "gpt-4",
        "suggestions": ["gpt-4", "gpt-4o", "gpt-3.5-turbo"]
    },
    "openrouter": {
        "provider": "OpenRouter",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url_env": "OPENROUTER_BASE",
        "default_model": "openrouter/mistral-7b-openorca",
        "suggestions": ["mistral-7b-openorca", "meta-llama-3-8b-instruct", "command-r"]
    },
    "gemini": {
        "provider": "Gemini",
        "api_key_env": "GEMINI_API_KEY",
        "base_url_env": "GEMINI_BASE",
        "default_model": "gemini-pro",
        "suggestions": ["gemini-pro", "gemini-1.5-pro-latest"]
    }
}

def save_config(provider, model, path, cli_tool):
    config = {
        "last_provider": provider,
        "last_model": model,
        "last_path": path,
        "last_cli": cli_tool
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def check_cli_available(cli_name):
    return which(cli_name) is not None

def interactive_prompt():
    cfg = load_config()
    print("🔮 Available providers: openai, openrouter, gemini")
    provider = input(f"Select a provider [{cfg.get('last_provider', '')}]: ").strip().lower() or cfg.get("last_provider", "")
    if provider not in models:
        print("❌ Invalid provider.")
        exit(1)

    suggestions = models[provider]["suggestions"]
    default_model = models[provider]["default_model"]
    print(f"💡 Suggested models for {provider}: {', '.join(suggestions)}")
    model = input(f"Enter model name [{cfg.get('last_model', default_model)}]: ").strip() or cfg.get("last_model", default_model)

    project_path = input(f"Enter project path [{cfg.get('last_path', '')}]: ").strip() or cfg.get("last_path", "")

    print("🛠️ Available CLI options:")
    cli_options = []
    if check_cli_available("aider"):
        cli_options.append("aider")
    if check_cli_available("gemini"):
        cli_options.append("gemini")
    if not cli_options:
        print("❌ No supported CLI tools found (install 'aider' or 'gemini').")
        exit(1)

    print(f"   Available: {', '.join(cli_options)}")
    cli_tool = input(f"Select CLI tool [{cfg.get('last_cli', cli_options[0])}]: ").strip() or cfg.get("last_cli", cli_options[0])

    if cli_tool not in cli_options:
        print("❌ Invalid CLI tool selected.")
        exit(1)

    save_config(provider, model, project_path, cli_tool)
    return provider, model, project_path, cli_tool

def start_chat(provider_choice, model_name, project_path, cli_tool):
    if provider_choice not in models:
        print("Invalid provider. Choose from: openai, openrouter, gemini")
        return

    cfg = models[provider_choice]
    print(f"📦 Using model: {model_name} from {cfg['provider']}")
    print(f"📁 Project directory: {project_path}")
    print(f"🧠 CLI Tool: {cli_tool}")

    api_key = ensure_env_var(cfg["api_key_env"], f"{cfg['provider']} API Key")
    base_url = ensure_env_var(cfg["base_url_env"], f"{cfg['provider']} Base URL")

    if not api_key:
        print(f"❌ Missing environment variable: {cfg['api_key_env']}")
        exit(1)
    if not base_url:
        print(f"❌ Missing environment variable: {cfg['base_url_env']}")
        exit(1)

    os.environ["LLM_API_KEY"] = api_key
    os.environ["LLM_BASE_URL"] = base_url
    os.environ["LLM_MODEL"] = model_name

    if cli_tool == "aider":
        subprocess.run(["aider", "--model", model_name], cwd=project_path)
    elif cli_tool == "gemini":
        subprocess.run(["gemini"], cwd=project_path)
    else:
        print(f"❌ Unsupported CLI tool: {cli_tool}")

if __name__ == "__main__":
    import sys
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python mcp_launcher.py [provider] [model] [project_path] [cli_tool]")
        print("Example: python mcp_launcher.py openai gpt-4 /path/to/project aider")
        print("You can also run without arguments to use interactive mode with config memory.")
        exit(0)

    if len(sys.argv) == 5:
        provider, model, path, cli = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
        save_config(provider, model, path, cli)
    else:
        provider, model, path, cli = interactive_prompt()

    start_chat(provider, model, path, cli)
