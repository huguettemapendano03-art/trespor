"""
Settings Manager Module
Handles user preferences, themes, colors, precision, and default angle units.
"""

import json
import os
from typing import Dict, Any


class SettingsManager:
    """
    Manages user preferences and persistent configuration.
    """

    DEFAULT_SETTINGS = {
        "appearance_mode": "dark",      # "dark", "light", or "system"
        "color_theme": "blue",          # "blue", "green", "dark-blue"
        "angle_unit": "DEG",            # "DEG", "RAD", "GRAD"
        "precision": 10,                # Number of decimal places
        "sound_effects": False,         # Audio feedback setting placeholder
        "always_on_top": False,
        "default_mode": "Standard"      # "Standard", "Scientific", "Logic"
    }

    def __init__(self, filename: str = "calc_settings.json"):
        self.filename = filename
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.DEFAULT_SETTINGS.copy()
        else:
            self.save_settings()
        return self.settings

    def save_settings(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save_settings()

    def reset_defaults(self) -> None:
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
