# AI Model Data Structure

The `AIModel` model represents a configured AI model that a user has selected from a provider and wants to use with coding agents.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier for the model (typically the model name from the provider) |
| `model_name` | `str` | Human-readable name of the model |
| `provider_id` | `str` | ID of the provider that offers this model |
| `enabled` | `bool` | Whether this model is enabled for use |
| `metadata` | [`AIModelMetadata`](#aimodelmetadata) | Information about the model's capabilities and specifications |
| `parameters` | [`AIModelParameters`](#aimodelparameters) | Default parameters to use when invoking the model |
| `cost_per_1m_tokens` | [`CostPer1mTokens`](#costper1mtokens) | Cost per 1 million tokens for input and output |

## AIModelMetadata

| Field | Type | Description |
|-------|------|-------------|
| `context_window` | `Optional[int]` | Maximum context window size in tokens |
| `max_output_tokens` | `Optional[int]` | Maximum number of tokens the model can generate in a single call |
| `modalities` | `List[str]` | Supported modalities (e.g., ["text"], ["text", "image"]) |
| `supports_tool_calling` | `Optional[bool]` | Whether the model supports tool/function calling |
| `supports_json_mode` | `Optional[bool]` | Whether the model supports JSON mode output |
| `training_cutoff` | `Optional[str]` | Knowledge cutoff date (e.g., "2024-01") |

## AIModelParameters

| Field | Type | Description |
|-------|------|-------------|
| `temperature` | `Optional[float]` | Sampling temperature (0.0 to 2.0) |
| `top_p` | `Optional[float]` | Nucleus sampling parameter |
| `top_k` | `Optional[int]` | Top-k sampling parameter |
| `frequency_penalty` | `Optional[float]` | Frequency penalty (-2.0 to 2.0) |
| `presence_penalty` | `Optional[float]` | Presence penalty (-2.0 to 2.0) |
| `stop` | `List[str]` | Stop sequences |
| `reasoning_effort` | `Optional[str]` | Reasoning effort level (for models that support it) |
| `thinking_level` | `Optional[str]` | Thinking level (for models that support it) |

## CostPer1mTokens

| Field | Type | Description |
|-------|------|-------------|
| `input` | `float` | Cost per 1 million input tokens (in USD) |
| `output` | `float` | Cost per 1 million output tokens (in USD) |
| `cached_input` | `Optional[float]` | Cost per 1 million cached input tokens (if applicable) |

## Example AI Model Configuration

```json
{
  "id": "gpt-4o",
  "model_name": "GPT-4o",
  "provider_id": "openai",
  "enabled": true,
  "metadata": {
    "context_window": 128000,
    "max_output_tokens": 16384,
    "modalities": ["text", "image"],
    "supports_tool_calling": true,
    "supports_json_mode": true,
    "training_cutoff": "2024-01"
  },
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": null
  },
  "cost_per_1m_tokens": {
    "input": 2.5,
    "output": 10.0,
    "cached_input": 1.25
  }
}
```

## Model Identification

Models are uniquely identified by their `id` field within the LLMC configuration. This ID is typically the same as the model identifier used by the provider, but may be normalized in some cases.

When synchronizing with coding agents, LLMC uses adapters to convert the AIModel structure into the format expected by each specific agent.