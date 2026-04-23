# LLMC Overview

LLMC (LLM Chooser) is a CLI tool designed to manage AI model configurations centrally and synchronize them with various coding agents. It decouples model preferences from individual tools, providing a single source of truth for AI model settings.

## Core Concepts

LLMC organizes configuration into three primary components:

- **Providers**: AI service providers (Ollama, OpenAI, Anthropic, etc.) that host models
- **Models**: Specific AI models selected from enabled providers for use
- **Agents**: Coding tools and IDE integrations that LLMC can synchronize with

## Standard Workflow

The typical LLMC workflow follows these steps:

1. **List and Enable Providers**
   ```bash
   llmc providers list              # View available providers
   llmc providers enable <id>       # Enable desired providers
   ```

2. **Configure API Keys**
   ```bash
   llmc providers apikey <id>       # Securely store API key in system keyring
   ```

3. **Discover Available Models**
   ```bash
   llmc candidates                  # List models from enabled providers
   # Auth column indicators:
   #   ✗ - No authentication required
   #   ✓ - Authentication required and key provided
   #   ? - Authentication required but key missing
   ```

4. **Select Preferred Models**
   ```bash
   llmc models list                 # View currently selected models
   llmc models add -p <id> -m <id>  # Add model to preferred list
   ```

5. **Synchronize with Coding Agents**
   ```bash
   llmc agents discover             # Detect installed coding agents
   llmc agents sync                 # Sync models to selected agent configurations
   ```

## Configuration Storage

LLMC stores all configuration in `~/.config/aimodels/` as three JSON files:

### providers.json
- Contains configured AI providers and their connection settings
- Initially populated from `seeds/providers.json` on first run
- Only enabled providers are queried for available models
- Refer to [provider.md](provider.md) for detailed structure

### agents.json
- Defines known coding agents that LLMC can synchronize with
- Initially populated from `seeds/agents.json` on first run
- Updated when running `llmc agents discover`
- Refer to [agents.md](agents.md) for detailed structure

### models.json
- Contains the user's selected AI models with their configurations
- Each entry follows the structure defined in [aimodel.md](aimodel.md)
- Should only include models intended for use with coding agents

## Extensibility

LLMC's architecture supports extension through:
- Additional provider types in the seeds file
- New agent adapters in `sync_service.py`
- Custom model metadata and parameters

See the individual data structure documents for implementation details.