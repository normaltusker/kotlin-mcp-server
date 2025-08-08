# Android MCP Assistant

This project enables a Local Model Context Protocol (MCP)-based assistant to interact with your Kotlin Android project using any LLM of your choice — OpenAI, Gemini, or OpenRouter — at runtime.

---

## ✅ Features

- 🔄 **Runtime Model Switching** – Easily switch between GPT-4, Gemini Pro, and Mistral via CLI.
- 📂 **Full Project Context** – The LLM sees your Kotlin Android app structure (activities, layouts, Gradle, etc.).
- ✍️ **File Editing by LLM** – Add/modify Kotlin code directly using the selected language model.
- 🧠 **Grounded Conversations** – Ask for changes or new screens, and the AI responds in the context of your app.

---

## ⚠️ What You Can Add

These optional components enhance functionality and are supported:

| Capability                       | How to Add |
|----------------------------------|------------|
| 🧠 Kotlin syntax intelligence     | Add [`kotlin-language-server`](https://github.com/fwcd/kotlin-language-server) and `mcp-lsp` |
| ⚙️ Gradle build/test integration | Add `mcp-process` and configure commands like `./gradlew assembleDebug` |
| 💬 GUI Assistant Chat            | Connect to [OpenWebUI](https://github.com/open-webui/open-webui) or use [`aider`](https://github.com/paul-gauthier/aider) |
| 🧪 AI-based Code Suggestions     | Combine LSP + MCP for full developer co-pilot capabilities |

---

## 🚀 Usage

```bash
python3 mcp_launcher.py openai /absolute/path/to/your/project
python3 mcp_launcher.py gemini /Users/me/dev/MyAndroidApp
```

Or define your project path in `.env`:

```env
PROJECT_PATH=/Users/me/dev/MyAndroidApp
```

Then run:

```bash
python3 mcp_launcher.py openrouter
```

---

## 📁 Directory Layout

```
.
├── .env                  # API keys and project path
├── mcp_launcher.py       # Main launcher script
├── android-project/      # Optional placeholder project directory
├── servers/
│   ├── mcp-filesystem/   # For reading/writing project files
│   ├── mcp-process/      # (Optional) For running shell commands like Gradle
│   └── kotlin-language-server/  # (Optional) LSP for Kotlin syntax + types
```

---

## 🧑‍💻 Requirements

- Python 3.8+
- Aider, LiteLLM, or OpenWebUI for chat
- IntelliJ with Kotlin plugin for editing

---

## 🧪 Recommended Tools

- [`aider`](https://github.com/paul-gauthier/aider)
- [`mcp-filesystem`](https://github.com/modelcontext/mcp-filesystem)
- [`mcp-process`](https://github.com/modelcontext/mcp-process)
- [`kotlin-language-server`](https://github.com/fwcd/kotlin-language-server)
- [`mcp-lsp`](https://github.com/modelcontext/mcp-lsp)

---

## 📦 License

MIT


---

## 🛠️ Gradle Build Support via `mcp-process`

To allow the assistant to run commands like `./gradlew build`, do the following:

1. Clone the MCP process server:
```bash
git clone https://github.com/modelcontext/mcp-process servers/mcp-process
```

2. Use the included wrapper script:
```bash
chmod +x servers/mcp-process/mcp-gradle-wrapper.sh
./servers/mcp-process/mcp-gradle-wrapper.sh /path/to/project "./gradlew assembleDebug"
```

You can then allow your assistant to run build/test commands using subprocess or integrate it in your aider prompt.

---

## 🧠 Kotlin Syntax Intelligence with LSP

Enable Kotlin code understanding by wiring in a Language Server:

1. Clone Kotlin LSP:
```bash
git clone https://github.com/fwcd/kotlin-language-server servers/kotlin-language-server
cd servers/kotlin-language-server
./gradlew installDist
```

2. Run the language server:
```bash
./build/install/kotlin-language-server/bin/kotlin-language-server
```

3. Integrate it with [mcp-lsp](https://github.com/modelcontext/mcp-lsp) (optional but recommended):
```bash
git clone https://github.com/modelcontext/mcp-lsp servers/mcp-lsp
cd servers/mcp-lsp
npm install
npm run start
```

Configure it to point to the above Kotlin language server binary.

---

## 🤖 Aider Integration

Aider automatically detects the current working directory and Git context. You’re already wired to use Aider from the launcher.

To invoke:

```bash
python3 mcp_launcher.py openai /path/to/your/project
```

Then, in the chat:

> 💬 "Run a Gradle build and check for lint issues"

You can respond:
```bash
./servers/mcp-process/mcp-gradle-wrapper.sh /path/to/project "./gradlew lint"
```

Or automate subprocess calling in `mcp_launcher.py` using `mcp-process`.

---



---

## 🐳 Docker Support (Optional)

You can build and run the entire MCP assistant setup in a portable Docker container.

### 1. Build the image
```bash
docker-compose build
```

### 2. Start the container
```bash
docker-compose run mcp-assistant
```

This gives you an environment with:
- Python 3.11
- Aider preinstalled
- Node.js & npm
- OpenJDK 17
- Git + curl + bash

Perfect for experimenting, testing or sharing with others.

---
