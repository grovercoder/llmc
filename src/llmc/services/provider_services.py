from typing import List, Optional
from llmc.models import Provider, Providers
from pathlib import Path
import json

from llmc.services.keyring_service import KeyringService

class ProviderServices:
    def __init__(self, config_dir: str = ".config/aimodels"):
        self.config_path = Path.home() / config_dir / "providers.json"
        self._providers: List[Provider] = []

    def _resolve_api_key(self, provider: Provider) -> Provider:
        """Resolve API key from keyring if needed."""
        if provider.connection.api_key_in_keyring:
            key = KeyringService.get_key(provider.id)
            if key:
                provider.connection.api_key = key
        return provider

    def _save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.get_providers_wrapper().model_dump(mode='json'), f, indent=2)

    def refresh(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
                providers_data = Providers(**data)
                self._providers = providers_data.providers

    def get_all(self, resolve_keys: bool = True) -> List[Provider]:
        if resolve_keys:
            return [self._resolve_api_key(p) for p in self._providers]
        return self._providers

    def get_by_id(self, provider_id: str, resolve_key: bool = True) -> Optional[Provider]:
        provider = next((p for p in self._providers if p.id == provider_id), None)
        if provider and resolve_key:
            return self._resolve_api_key(provider)
        return provider

    def create(self, provider: Provider) -> Provider:
        if self.get_by_id(provider.id) is not None:
            raise ValueError(f"Provider with id {provider.id} already exists")
        self._providers.append(provider)
        return provider

    def update(self, provider_id: str, provider_data: Provider) -> Provider:
        idx = next((i for i, p in enumerate(self._providers) if p.id == provider_id), None)
        if idx is None:
            raise ValueError(f"Provider with id {provider_id} not found")
        self._providers[idx] = provider_data
        return provider_data

    def delete(self, provider_id: str) -> bool:
        idx = next((i for i, p in enumerate(self._providers) if p.id == provider_id), None)
        if idx is not None:
            self._providers.pop(idx)
            return True
        return False

    def set_api_key(self, provider_id: str, api_key: str) -> Provider:
        """Store API key in keyring and update provider config."""
        provider = self.get_by_id(provider_id, resolve_key=False)
        if provider is None:
            raise ValueError(f"Provider '{provider_id}' not found")

        if not KeyringService.is_available():
            raise RuntimeError("Keyring is not available on this system")

        if not KeyringService.set_key(provider_id, api_key):
            raise RuntimeError("Failed to store API key in keyring")

        provider.connection.api_key = None
        provider.connection.api_key_in_keyring = True
        provider.enabled = True
        self.update(provider_id, provider)
        self._save()
        return provider

    def remove_api_key(self, provider_id: str) -> bool:
        """Remove API key from keyring and update provider config."""
        provider = self.get_by_id(provider_id, resolve_key=False)
        if provider is None:
            raise ValueError(f"Provider '{provider_id}' not found")

        KeyringService.remove_key(provider_id)

        provider.connection.api_key = None
        provider.connection.api_key_in_keyring = False
        self.update(provider_id, provider)
        self._save()
        return True

    def get_providers_wrapper(self) -> Providers:
        return Providers(providers=self._providers)
