import pytest
from llmc.services.sync_service import (
    AiderAdapter, ClaudeAdapter, OpenCodeAdapter, PIAdapter, HermesAdapter
)
from llmc.models import AIModel, AIModelMetadata, AIModelParameters, CostPer1mTokens

@pytest.fixture
def sample_model():
    return AIModel(
        id="gpt-4o",
        model_name="GPT-4o",
        provider_id="openai-prod",
        enabled=True,
        metadata=AIModelMetadata(context_window=128000),
        parameters=AIModelParameters(temperature=0.7),
        cost_per_1m_tokens=CostPer1mTokens(input=2.5, output=10.0),
    )

def test_aider_adapter(sample_model):
    adapter = AiderAdapter()
    val = adapter.get_model_value(sample_model)
    # Expects "provider/model" where provider is the first part of provider_id
    assert val == "openai/gpt-4o"

def test_claude_adapter(sample_model):
    adapter = ClaudeAdapter()
    val = adapter.get_model_value(sample_model)
    assert val == "gpt-4o"

def test_opencode_adapter(sample_model):
    adapter = OpenCodeAdapter()
    val = adapter.get_model_value(sample_model)
    assert val["id"] == "gpt-4o"
    assert val["options"]["temperature"] == 0.7

def test_hermes_adapter(sample_model):
    adapter = HermesAdapter()
    val = adapter.get_model_value(sample_model)
    assert val == {"id": "gpt-4o", "name": "GPT-4o"}

def test_pi_adapter(sample_model):
    adapter = PIAdapter()
    val = adapter.get_model_value(sample_model)
    assert val["name"] == "gpt-4o"
    assert val["provider"] == "openai"
