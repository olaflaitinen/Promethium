# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Type, Dict, Any, Optional
from promethium_seismic.ml.models.base import PromethiumModel
from promethium_seismic.core.logging import get_logger

logger = get_logger(__name__)

class ModelRegistry:
    _registry: Dict[str, Type[PromethiumModel]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(model_cls: Type[PromethiumModel]):
            if name in cls._registry:
                logger.warning(f"Model {name} already registered. Overwriting.")
            cls._registry[name] = model_cls
            return model_cls
        return decorator

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> PromethiumModel:
        if name not in cls._registry:
            raise ValueError(f"Model {name} not found in registry. Available: {list(cls._registry.keys())}")
        
        logger.info(f"Creating model: {name} | Config: {config}")
        return cls._registry[name](config)
