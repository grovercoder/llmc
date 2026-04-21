from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import os
from llmc.models import AIModel

AGENTS_CONFIG = Path.home() / ".config/aimodels/agents.json"


class Agent:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        config_path: str,
        model_field: str,
        supports_multiple: bool,
        model_format: str,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.config_path = config_path
        self.model_field = model_field
        self.supports_multiple = supports_multiple
        self.model_format = model_format

    @property
    def resolved_path(self) -> Path:
        return Path(os.path.expanduser(self.config_path))

    def exists(self) -> bool:
        return self.resolved_path.exists()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "config_path": self.config_path,
            "model_field": self.model_field,
            "supports_multiple": self.supports_multiple,
            "model_format": self.model_format,
            "exists": self.exists(),
        }


class Agents:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    @classmethod
    def load(cls) -> "Agents":
        if not AGENTS_CONFIG.exists():
            return cls([])
        with open(AGENTS_CONFIG) as f:
            data = json.load(f)
        agents = [
            Agent(
                id=a["id"],
                name=a["name"],
                description=a["description"],
                config_path=a["config_path"],
                model_field=a["model_field"],
                supports_multiple=a["supports_multiple"],
                model_format=a["model_format"],
            )
            for a in data.get("agents", [])
        ]
        return cls(agents)

    def save(self):
        data = {"agents": [a.to_dict() for a in self.agents]}
        AGENTS_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(AGENTS_CONFIG, "w") as f:
            json.dump(data, f, indent=2)

    def get_by_id(self, agent_id: str) -> Optional[Agent]:
        return next((a for a in self.agents if a.id == agent_id), None)

    def list_all(self) -> List[Agent]:
        return self.agents


class AgentAdapter:
    def get_model_value(self, model: AIModel) -> Any:
        raise NotImplementedError

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        raise NotImplementedError


class OpenCodeAdapter(AgentAdapter):
    def get_model_value(self, model: AIModel) -> Dict[str, Any]:
        provider_id = model.provider_id.split("-")[0]
        temp = model.parameters.temperature if model.parameters and model.parameters.temperature is not None else 0.1
        return {
            "id": model.id,
            "name": model.model_name,
            "_launch": True,
            "maxTokens": 16384,
            "options": {
                "temperature": temp,
            },
        }

    def _get_provider(self, model: AIModel) -> str:
        return model.provider_id.split("-")[0]

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        config = config or {}
        if "provider" not in config:
            config["provider"] = {}

        existing_providers = config.get("provider", {})

        for model in models:
            provider_id = self._get_provider(model)
            if provider_id not in existing_providers:
                existing_providers[provider_id] = {
                    "name": provider_id.capitalize(),
                    "npm": "@ai-sdk/openai-compatible",
                    "options": {},
                    "models": {},
                }
            if "models" not in existing_providers[provider_id]:
                existing_providers[provider_id]["models"] = {}

            model_entry = self.get_model_value(model)
            existing_providers[provider_id]["models"][model.id] = model_entry

        config["provider"] = existing_providers
        return config


class AiderAdapter(AgentAdapter):
    def get_model_value(self, model: AIModel) -> str:
        provider = model.provider_id.split("-")[0]
        return f"{provider}/{model.id}"

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        if not models:
            return config
        model = models[0]
        config["model"] = self.get_model_value(model)
        return config


class ClaudeAdapter(AgentAdapter):
    def get_model_value(self, model: AIModel) -> str:
        return model.id

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        if not models:
            return config
        model = models[0]
        config["model"] = self.get_model_value(model)
        return config


class HermesAdapter(AgentAdapter):
    def get_model_value(self, model: AIModel) -> Dict[str, Any]:
        return {"id": model.id, "name": model.model_name}

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        config = config or {}
        existing_models = config.get("models", [])
        model_ids = [m["id"] for m in existing_models]

        for model in models:
            if model.id not in model_ids:
                existing_models.append(self.get_model_value(model))

        config["models"] = existing_models
        return config


class PIAdapter(AgentAdapter):
    def get_model_value(self, model: AIModel) -> Dict[str, Any]:
        provider = model.provider_id.split("-")[0]
        return {
            "name": model.id,
            "provider": provider,
            "priority": 0,
        }

    def set_models(self, config: Dict, models: List[AIModel]) -> Dict:
        if not models:
            return config

        config = config or {}
        existing_preferred = config.get("preferred_models", [])

        added_names = {m["name"] for m in existing_preferred}

        for i, model in enumerate(models):
            if model.id not in added_names:
                entry = {
                    "name": model.id,
                    "provider": model.provider_id.split("-")[0],
                    "priority": len(existing_preferred) + i,
                }
                existing_preferred.append(entry)

        config["preferred_models"] = existing_preferred
        config["default_model"] = models[0].id
        return config

    def set_agent_models(self, config: Dict, models: List[AIModel]) -> Dict:
        if not models:
            return config

        config = config or {"providers": {}}

        existing_providers = config.get("providers", {})

        provider_base_urls = {
            "openrouter": "https://openrouter.ai/api/v1",
        }

        from llmc.services.provider_services import ProviderServices
        from llmc.services.keyring_service import KeyringService
        ps = ProviderServices()
        ps.refresh()

        for model in models:
            provider_raw = model.provider_id.split("-")[0]
            provider_name = f"llmc-{provider_raw}"

            if provider_name not in existing_providers:
                # Resolve API Key
                provider = ps.get_by_id(model.provider_id)
                api_key = "ollama" if provider_raw == "ollama" else ""
                
                if provider:
                    if provider.connection.api_key_in_keyring:
                        key = KeyringService.get_key(provider.id)
                        if key:
                            api_key = key
                    elif provider.connection.api_key:
                        api_key = provider.connection.api_key

                existing_providers[provider_name] = {
                    "baseUrl": provider_base_urls.get(provider_raw, "http://localhost:11434/v1"),
                    "api": "openai-completions",
                    "apiKey": api_key,
                    "models": [],
                }

            model_ids = [m["id"] for m in existing_providers[provider_name].get("models", [])]
            if model.id not in model_ids:
                existing_providers[provider_name]["models"].append({"id": model.id})

        config["providers"] = existing_providers
        return config


ADAPTERS = {
    "opencode": OpenCodeAdapter(),
    "aider": AiderAdapter(),
    "claude": ClaudeAdapter(),
    "hermes": HermesAdapter(),
    "pi": PIAdapter(),
}


class SyncService:
    def __init__(self):
        self.agents = Agents.load()

    def discover(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "config_path": a.config_path,
                "exists": a.exists(),
                "supports_multiple": a.supports_multiple,
            }
            for a in self.agents.list_all()
        ]

    def get_models_for_agent(self, agent_id: str, available_models: List[AIModel]) -> List[AIModel]:
        agent = self.agents.get_by_id(agent_id)
        if not agent:
            return available_models
        if agent.supports_multiple:
            return available_models
        return available_models[:1] if available_models else []

    def apply_sync(
        self, agent_id: str, models: List[AIModel], dry_run: bool = False
    ) -> Dict[str, Any]:
        agent = self.agents.get_by_id(agent_id)
        if not agent:
            return {"error": f"Unknown agent: {agent_id}"}

        if not agent.exists():
            return {"error": f"Config file not found: {agent.config_path}"}

        adapter = ADAPTERS.get(agent.model_format)
        if not adapter:
            return {"error": f"No adapter for format: {agent.model_format}"}

        try:
            with open(agent.resolved_path) as f:
                if agent.resolved_path.suffix == ".json":
                    current_config = json.load(f)
                elif agent.resolved_path.suffix in [".yaml", ".yml"]:
                    import yaml
                    current_config = yaml.safe_load(f) or {}
                else:
                    current_config = {}
        except Exception as e:
            current_config = {}

        new_config = adapter.set_models(current_config, models)

        if agent_id == "pi":
            agent_models_path = Path.home() / ".pi" / "agent" / "models.json"
            try:
                if agent_models_path.exists():
                    with open(agent_models_path) as f:
                        current_agent_models = json.load(f)
                else:
                    current_agent_models = {"providers": {}}
            except Exception:
                current_agent_models = {"providers": {}}

            new_agent_models = adapter.set_agent_models(current_agent_models, models)

            if not dry_run:
                backup_path = agent_models_path.with_suffix(
                    agent_models_path.suffix + ".backup"
                )
                import shutil

                shutil.copy(agent_models_path, backup_path)
                with open(agent_models_path, "w") as f:
                    json.dump(new_agent_models, f, indent=2)

        if dry_run:
            return {
                "agent": agent_id,
                "dry_run": True,
                "current_config": current_config,
                "new_config": new_config,
            }

        backup_path = agent.resolved_path.with_suffix(
            agent.resolved_path.suffix + ".backup"
        )
        import shutil

        shutil.copy(agent.resolved_path, backup_path)

        if agent.resolved_path.suffix == ".json":
            with open(agent.resolved_path, "w") as f:
                json.dump(new_config, f, indent=2)
        elif agent.resolved_path.suffix in [".yaml", ".yml"]:
            import yaml

            with open(agent.resolved_path, "w") as f:
                yaml.dump(new_config, f, default_flow_style=False)
        else:
            return {"error": "Unsupported config format"}

        return {
            "agent": agent_id,
            "success": True,
            "backup": str(backup_path),
            "models_synced": [m.id for m in models],
        }
