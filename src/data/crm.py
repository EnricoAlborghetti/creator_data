import json
import os
from typing import List, Dict, Any
from src.models.schemas import AnalysisResult

class CRMMock:
    def __init__(self, output_file: str = "crm_output.json"):
        self.output_file = output_file

    def save_data(self, file_path: str, result: AnalysisResult):
        """
        Appends the analysis result to the JSON file.
        Reads existing, appends, writes back.
        """
        data = []
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

        # Convert Pydantic model to dict and add source file info
        record = result.model_dump()
        record["source_file"] = file_path

        data.append(record)

        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
