import json
import os
import asyncio
from typing import Any, Dict

class Config:
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}

    async def load(self) -> None:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}

    async def save(self) -> None:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value