# Agents Data Structure

The `Agent` model represents a coding agent configuration that LLMC can synchronize with.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier for the agent (e.g., "aider", "claude") |
| `name` | `str` | Human-readable name of the agent |
| `description` | `str` | Description of what the agent does |
| `config_path` | `str` | Path to the agent's configuration file (supports `~` expansion) |
| `model_field` | `str` | The field in the config file where the model is specified |
| `supports_multiple` | `bool` | Whether the agent can be configured with multiple models |
| `model_format` | `str` | Identifier for the adapter used to format models for this agent |
| `exists` | `bool` (computed) | Whether the config file exists on the filesystem |

## Supported Agents

LLMC includes built-in support for the following agents:

### OpenCode
- ID: `opencode`
- Config Path: `~/.config/opencode/opencode.json`
- Model Field: `provider`
- Supports Multiple: Yes
- Format: OpenCode-specific JSON structure

### Aider
- ID: `aider`
- Config Path: `~/.aider.conf.yml`
- Model Field: `model`
- Supports Multiple: No (single model)
- Format: String in format `provider/model`

### Claude
- ID: `claude`
- Config Path: `~/.claude/settings.json`
- Model Field: `model`
- Supports Multiple: No
- Format: Model ID string

### Hermes
- ID: `hermes`
- Config Path: `~/.hermes/config.yaml`
- Model Field: `models`
- Supports Multiple: Yes
- Format: List of model objects with `id` and `name`

### PI
- ID: `pi`
- Config Path: `~/.pi/config.json`
- Model Field: `default_model`
- Supports Multiple: No (but manages preferred models list)
- Format: Complex structure with `preferred_models` array and `default_model`

## Agent Configuration Discovery

LLMC discovers agents by checking for the existence of their configuration files at the specified paths. When an agent is discovered, its configuration is saved to `~/.config/aimodels/agents.json` for future reference.

## Custom Agents

To add support for additional agents, you would need to:
1. Add the agent definition to the known agents list in `agents_discover()` function
2. Create an adapter class that implements the `AgentAdapter` interface
3. Register the adapter in the `ADAPTERS` dictionary

See `sync_service.py` for examples of adapter implementations.