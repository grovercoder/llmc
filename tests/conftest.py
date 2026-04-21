import pytest
import os
import shutil
from pathlib import Path
from llmc.models import Provider, Connection, Reliability, TrafficControl, AIModel, AIModelMetadata, AIModelParameters, CostPer1mTokens

@pytest.fixture
def temp_config_dir(tmp_path):
    """Provides a temporary directory for configuration files."""
    config_dir = tmp_path / ".config/aimodels"
    config_dir.mkdir(parents=True)
    return config_dir

@pytest.fixture
def sample_provider():
    return Provider(
        id="test-provider",
        name="Test Provider",
        provider_type="openai",
        enabled=True,
        connection=Connection(base_url="https://test.example.com/v1"),
        reliability=Reliability(timeout_seconds=30, max_retries=3, backoff_factor=2.0),
        traffic_control=TrafficControl(priority=1, weight=1),
    )

@pytest.fixture
def sample_model():
    return AIModel(
        id="gpt-4o",
        model_name="GPT-4o",
        provider_id="test-provider",
        enabled=True,
        metadata=AIModelMetadata(context_window=128000),
        parameters=AIModelParameters(temperature=0.7),
        cost_per_1m_tokens=CostPer1mTokens(input=2.5, output=10.0),
    )
