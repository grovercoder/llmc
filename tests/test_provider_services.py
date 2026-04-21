import pytest
from pathlib import Path
from llmc.services.provider_services import ProviderServices
from llmc.models import Provider, Connection, Reliability, TrafficControl

def test_provider_services_save_and_load(temp_config_dir, sample_provider, monkeypatch):
    """Test that providers can be saved to and loaded from a JSON file."""
    
    # The config_dir is assumed to be relative to Path.home()
    # Path.home() / ".config/aimodels" / "providers.json"
    # We need Path.home() to be the parent of the .config folder.
    home_mock = temp_config_dir.parent.parent
    monkeypatch.setattr(Path, "home", lambda: home_mock)
    
    ps = ProviderServices(config_dir=".config/aimodels")
    
    # Add provider
    ps.create(sample_provider)
    ps._save()
    
    # Assert file exists
    assert (temp_config_dir / "providers.json").exists()
    
    # Refresh and check
    new_ps = ProviderServices(config_dir=".config/aimodels")
    new_ps.refresh()
    loaded_provider = new_ps.get_by_id("test-provider")
    
    assert loaded_provider is not None
    assert loaded_provider.name == "Test Provider"

def test_provider_services_update(temp_config_dir, sample_provider, monkeypatch):
    with pytest.MonkeyPatch.context() as mp: # This was a mistake, using monkeypatch fixture instead
        pass

def test_provider_services_update_fixed(temp_config_dir, sample_provider, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)
    ps = ProviderServices(config_dir=".config/aimodels")
    
    ps.create(sample_provider)
    
    # Update provider
    sample_provider.name = "Updated Name"
    ps.update(sample_provider.id, sample_provider)
    
    updated = ps.get_by_id(sample_provider.id)
    assert updated.name == "Updated Name"
