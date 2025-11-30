import json
import os
from datetime import datetime
from typing import List
from src.models.schemas import ProcessingState

class StateManager:
    def __init__(self, state_file: str = "state.json"):
        self.state_file = state_file

    def load_state(self) -> ProcessingState:
        if not os.path.exists(self.state_file):
            return ProcessingState(processed_files=[], last_run_timestamp=datetime.now().isoformat())

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            return ProcessingState(**data)
        except json.JSONDecodeError:
            # Corrupt file, start fresh
            return ProcessingState(processed_files=[], last_run_timestamp=datetime.now().isoformat())

    def save_state(self, state: ProcessingState):
        with open(self.state_file, "w") as f:
            f.write(state.model_dump_json(indent=2))

    def get_unprocessed_files(self, all_files: List[str], limit: int = 50) -> List[str]:
        state = self.load_state()
        processed_set = set(state.processed_files)

        unprocessed = []
        for file_path in all_files:
            if file_path not in processed_set:
                unprocessed.append(file_path)
                if len(unprocessed) >= limit:
                    break
        return unprocessed

    def mark_files_as_processed(self, file_paths: List[str]):
        state = self.load_state()
        # Use set for uniqueness but keep list for storage
        current_processed = set(state.processed_files)
        current_processed.update(file_paths)

        state.processed_files = list(current_processed)
        state.last_run_timestamp = datetime.now().isoformat()
        self.save_state(state)
