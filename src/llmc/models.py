from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Connection(BaseModel):
    base_url: str
    api_key: Optional[str] = None
    api_key_in_keyring: bool = False
    organization_id: Optional[str] = None
    api_version: Optional[str] = None
    region: Optional[str] = None


class Reliability(BaseModel):
    timeout_seconds: int
    max_retries: int
    backoff_factor: float
    retry_codes: List[int] = Field(default_factory=list)


class TrafficControl(BaseModel):
    priority: int
    weight: int
    rpm_limit: Optional[int] = None
    tpc_limit: Optional[int] = None  # Note: original JSON had tpm_limit, I'll use tpm_limit to be accurate
    max_concurrency: Optional[int] = None

    # Re-checking the JSON: it used 'tpm_limit'
    tpm_limit: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class Proxy(BaseModel):
    enabled: bool
    url: Optional[str] = None


class Provider(BaseModel):
    id: str
    name: str
    provider_type: str
    enabled: bool
    connection: Connection
    reliability: Reliability
    traffic_control: TrafficControl
    headers: Dict[str, str] = Field(default_factory=dict)
    proxy: Optional[Proxy] = None


class Providers(BaseModel):
    providers: List[Provider]


class AIModelMetadata(BaseModel):
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    modalities: List[str] = Field(default_factory=list)
    supports_tool_calling: Optional[bool] = None
    supports_json_mode: Optional[bool] = None
    training_cutoff: Optional[str] = None


class AIModelParameters(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: List[str] = Field(default_factory=list)
    reasoning_effort: Optional[str] = None
    thinking_level: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class CostPer1mTokens(BaseModel):
    input: float
    output: float
    cached_input: Optional[float] = None


class AIModel(BaseModel):
    id: str
    model_name: str
    provider_id: str
    enabled: bool
    metadata: AIModelMetadata
    parameters: AIModelParameters
    cost_per_1m_tokens: CostPer1mTokens


class AIModels(BaseModel):
    models: List[AIModel]
