from typing import List, Optional
from llmc.models import AIModel, AIModels
from pathlib import Path
import json

class AIModelServices:
    def __init__(self, config_dir: str = ".config/aimodels"):
        self.config_path = Path.home() / config_dir / "models.json"
        self._models: List[AIModel] = []

    def get_all(self) -> List[AIModel]:
        return self._models

    def get_by_id(self, model_id: str) -> Optional[AIModel]:
        return next((m for m in self._models if m.id == model_id), None)

    def create(self, model: AIModel) -> AIModel:
        if self.get_by_id(model.id) is not None:
            raise ValueError(f"AIModel with id {model.id} already exists")
        self._models.append(model)
        return model

    def update(self, model_id: str, model_data: AIModel) -> AIModel:
        idx = next((i for i, m in enumerate(self._models) if m.id == model_id), None)
        if idx is None:
            raise ValueError(f"AIModel with id {model_id} not found")
        self._models[idx] = model_data
        return model_data

    def delete(self, model_id: str) -> bool:
        idx = next((i for i, m in enumerate(self._models) if m.id == model_id), None)
        if idx is not None:
            self._models.pop(idx)
            return True
        return False

    def _save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.get_models_wrapper().model_dump(mode='json'), f, indent=2)

    def refresh(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
                models_data = AIModels(**data)
                self._models = models_data.models

    def get_models_wrapper(self) -> AIModels:
        return AIModels(models=self._models)
