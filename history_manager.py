"""
History Manager Module
Handles saving, loading, appending, and clearing calculation history in JSON format.
"""

import json
import os
import time
from typing import List, Dict, Any


class HistoryManager:
    """
    Manages calculation history persistence and in-memory operations.
    """

    def __init__(self, filename: str = "calc_history.json"):
        self.filename = filename
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
        else:
            self.history = []
        return self.history

    def save_history(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_entry(self, expression: str, result: str, mode: str = "Standard") -> Dict[str, Any]:
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "expression": str(expression),
            "result": str(result),
            "mode": mode
        }
        self.history.insert(0, entry)  # newest first
        # Limit history to 100 entries
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save_history()
        return entry

    def clear_history(self) -> None:
        self.history = []
        self.save_history()

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
