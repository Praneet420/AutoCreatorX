# prompt_memory_bank.py

import json
import os
from datetime import datetime

class PromptMemoryBank:
    def __init__(self, memory_file="logs/prompt_memory.json"):
        self.memory_file = memory_file
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def save_prompt(self, context_id, prompt):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if context_id not in self.memory:
            self.memory[context_id] = []
        self.memory[context_id].append({"timestamp": timestamp, "prompt": prompt})
        self._write_memory()

    def get_prompts(self, context_id):
        return self.memory.get(context_id, [])

    def _write_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
