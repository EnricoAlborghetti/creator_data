import os
import json
import base64
from openai import OpenAI
from src.models.schemas import AnalysisResult, DocumentType

class AIAnalyzer:
    def __init__(self, api_key: str = None):
        # Fallback to env var if not passed
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
             # Just a warning, main loop might handle it or user provides it later
             print("Warning: OPENAI_API_KEY not found.")
        self.client = OpenAI(api_key=self.api_key)

    def analyze_document(self, images_b64: list[str], potential_cf: str = None) -> AnalysisResult:
        """
        Analyzes document images using OpenAI Vision.
        """
        if not images_b64:
             # Return a default 'Altro' if no images could be processed (e.g. PDF failure)
             # but try to populate CF if found in path
            from src.models.schemas import PersonalInfo
            return AnalysisResult(
                document_type=DocumentType.ALTRO,
                personal_info=PersonalInfo(fiscal_code=potential_cf)
            )

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": """You are an expert document analyzer for Italian administrative and financial documents.
Your goal is to extract structured data from the provided images.

1. **Classify the document** into one of these types:
   - "estratto conto"
   - "modulo cessione quinto"
   - "cedolino" (Pay slip / Pension slip)
   - "carta d'identità"
   - "patente"
   - "documenti fiscali"
   - "altro"

2. **Extract Personal Information**:
   - Name
   - Surname
   - Fiscal Code (Codice Fiscale)

3. **Extract Loan/Financial Details**:
   - IF and ONLY IF the document is a "cedolino", "estratto conto", or "modulo cessione quinto", look for "Cessione del Quinto" or "Delega" entries.
   - Look for keywords: "cqs", "cess", "dlg", "del", "tratt", "quinto", "V°".
   - For each entry found, extract:
     - Bank Name (Banca/Finanziaria)
     - Start Date (Data inizio)
     - End/Expiry Date (Data scadenza)
     - Installment Amount (Importo rata)
     - Total Duration (Durata totale)
     - Residual Duration (Durata residua)
"""
            },
            {
                "role": "user",
                "content": []
            }
        ]

        # Add hint about CF from folder path if available
        user_text = "Analyze the following document images."
        if potential_cf:
            user_text += f" Note: The file path suggests a potential Fiscal Code: {potential_cf}. Verify if this matches the document content."

        messages[1]["content"].append({"type": "text", "text": user_text})

        # Add images (limit to first 3 pages to save tokens if it's a long PDF converted to images)
        for img_b64 in images_b64[:3]:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}",
                     "detail": "high"
                }
            })

        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=AnalysisResult,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            print(f"AI Analysis failed: {e}")
            # Return empty/error structure
            from src.models.schemas import PersonalInfo
            return AnalysisResult(
                document_type=DocumentType.ALTRO,
                personal_info=PersonalInfo(fiscal_code=potential_cf)
            )
