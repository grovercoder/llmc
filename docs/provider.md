# Provider Data Structure

The `Provider` model represents an AI service provider configuration in LLMC.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier for the provider (e.g., "ollama", "openai") |
| `name` | `str` | Human-readable name of the provider |
| `provider_type` | `str` | Type of provider (matches litellm provider types: "ollama", "openai", "anthropic", etc.) |
| `enabled` | `bool` | Whether the provider is enabled for use |
| `connection` | [`Connection`](#connection) | Connection details including base URL and API key configuration |
| `reliability` | [`Reliability`](#reliability) | Reliability settings for API calls |
| `traffic_control` | [`TrafficControl`](#trafficcontrol) | Rate limiting and traffic control settings |
| `headers` | `Dict[str, str]` | Additional HTTP headers to send with requests |
| `proxy` | [`Proxy`](#proxy) (optional) | Proxy configuration |

## Connection

| Field | Type | Description |
|-------|------|-------------|
| `base_url` | `str` | Base URL for the provider's API |
| `api_key` | `Optional[str]` | API key (may be None if stored in keyring) |
| `api_key_in_keyring` | `bool` | Whether the API key is stored in the system keyring |
| `organization_id` | `Optional[str]` | Organization ID for providers that support it |
| `api_version` | `Optional[str]` | API version to use |
| `region` | `Optional[str]` | Geographic region for regional providers |

## Reliability

| Field | Type | Description |
|-------|------|-------------|
| `timeout_seconds` | `int` | Request timeout in seconds |
| `max_retries` | `int` | Maximum number of retry attempts |
| `backoff_factor` | `float` | Backoff multiplier for retries |
| `retry_codes` | `List[int]` | HTTP status codes that trigger retries |

## TrafficControl

| Field | Type | Description |
|-------|------|-------------|
| `priority` | `int` | Priority level for traffic shaping |
| `weight` | `int` | Weight for load balancing |
| `rpm_limit` | `Optional[int]` | Requests per minute limit |
| `tpc_limit` | `Optional[int]` | Tokens per call limit |
| `max_concurrency` | `Optional[int]` | Maximum concurrent requests |

## Proxy

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | `bool` | Whether proxy is enabled |
| `url` | `Optional[str]` | Proxy URL |

## Example Provider Configuration

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "provider_type": "openrouter",
  "enabled": true,
  "connection": {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key_in_keyring": true,
    "api_key": null
  },
  "reliability": {
    "timeout_seconds": 60,
    "max_retries": 3,
    "backoff_factor": 2.0,
    "retry_codes": [429, 500, 502, 503, 504]
  },
  "traffic_control": {
    "priority": 1,
    "weight": 1,
    "rpm_limit": 60,
    "tpc_limit": 4096,
    "max_concurrency": 10
  },
  "headers": {},
  "proxy": null
}
```