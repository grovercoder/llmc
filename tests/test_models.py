import pytest
from llmc.models import (
    Provider, Connection, Reliability, TrafficControl,
    AIModel, AIModelMetadata, AIModelParameters, CostPer1mTokens
)
from pydantic import ValidationError

def test_provider_valid_creation():
    """Test that a valid provider configuration is accepted."""
    provider = Provider(
        id="test-provider",
        name="Test Provider",
        provider_type="openai",
        enabled=True,
        connection=Connection(base_url="https://api.test.com/v1"),
        reliability=Reliability(timeout_seconds=60, max_retries=3, backoff_factor=2.0),
        traffic_control=TrafficControl(priority=1, weight=1),
    )
    assert provider.id == "test-provider"

def test_provider_invalid_connection():
    """Test that invalid connection data raises a ValidationError."""
    with pytest.raises(ValidationError):
        Provider(
            id="test",
            name="Test",
            provider_type="openai",
            enabled=True,
            connection="not-a-connection-object", # Should be Connection model
            reliability=Reliability(timeout_seconds=60, max_retries=3, backoff_factor=2.0),
            traffic_control=TrafficControl(priority=1, weight=1),
        )

def test_aimodel_valid_creation():
    """Test that a valid AIModel configuration is accepted."""
    model = AIModel(
        id="test-model",
        model_name="Test Model",
        provider_id="test-provider",
        enabled=True,
        metadata=AIModelMetadata(context_window=8192),
        parameters=AIModelParameters(temperature=0.7),
        cost_per_1m_tokens=CostPer1mTokens(input=0.1, output=0.2),
    )
    assert model.id == "test-model"

def test_aimodel_invalid_cost():
    """Test that invalid cost data raises a ValidationError."""
    with pytest.raises(ValidationError):
        AIModel(
            id="test",
            model_name="Test",
            provider_id="test-provider",
            enabled=True,
            metadata=AIModelMetadata(),
            parameters=AIModelParameters(),
            cost_per_1m_tokens="not-cost-object", # Should be CostPer1mTokens
        )
