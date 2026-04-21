# LLMC (LLM Model Controller)

LLMC (LLM Model Controller) is a powerful, lightweight, and extensible orchestration tool for Large Language Model (LLM) configuration management. It enables developers to decouple AI model preferences from individual tools, storing them in a standardized, vendor-agnostic format. By maintaining a single source of truth for your preferred models, LLMC allows you to seamlessly synchronize configurations across a wide range of AI coding agents and providers—such as Aider, Claude Code, and PI—streamlining your AI-driven development workflow.

## 🚀 Features

- **Unified Provider Management**: Manage multiple AI providers (Ollama, OpenRouter, OpenAI-compatible, etc.) in one place.
- **Model Discovery**: Easily discover and add models from your enabled providers.
- **Agent Synchronization**: Automatically sync your selected models to the configuration files of various coding agents (Aider, Claude, PI, OpenCode, etc.).
- **Secure API Key Storage**: Securely store API keys in your system's keyring.
- **Extensible Architecture**: Easily add new providers and supported agents.
- **CLI-First Experience**: A robust Command Line Interface (CLI) built with `typer` and `rich` for a beautiful terminal experience.

## 🛠️ Installation

Ensure you have `uv` or `pip` installed.

### Using `uv` (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd llmc

# Set up the environment
uv sync

# Run the CLI
uv run llmc --help

# (Optional) Add llmc to your PATH by creating a symlink
sudo ln -s $(pwd)/llmc /usr/local/bin/llmc
```

### Using `pip`

```bash
pip install .
```

## 📂 Configuration

LLMC stores its configuration in `~/.config/aimodels`. The following files are managed by the tool:

- `providers.json`: Contains your configured AI providers and their settings.
- `models.json`: Contains your selected models and their preferred configurations.
- `agents.json`: Contains information about the discovered coding agents on your system.

### 1. Manage Providers

List your configured providers:
```bash
llmc providers list
```

Add an API key for a provider (stored securely in your keyring):
```bash
llmc providers apikey openrouter -k your_api_key_here
```

### 2. Manage Models

List all available models across your enabled providers:
```bash
llmc models list
```

Discover and add new models from your providers:
```bash
llmc models add
```

### 3. Sync Agents

Discover supported coding agents on your system:
```bash
llmc agents discover
```

Sync your selected models to the discovered agents:
```bash
llmc agents sync
```

## 🖥️ CLI Commands

### `providers`
- `list`: List all providers.
- `get <id>`: Get detailed information about a provider.
- `enable/disable <id>`: Enable or disable a provider.
- `apikey <id> [-k <key>] [--remove]`: Manage API keys for a provider.

### `models`
- `list`: List all configured models.
- `add`: Interactively add models from providers.
- `get <id>`: Get details of a specific model.

### `agents`
- `list`: List configured agents.
- `discover`: Scan your system for supported coding agents (Aider, Claude, etc.).
- `sync`: Sync your `models.json` configuration to the identified agents.

### `candidates`
- `candidates [-p <provider_id>] [filter_text]`: List all models available from enabled providers.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
