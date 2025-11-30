from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    ESTRATTO_CONTO = "estratto conto"
    MODULO_CESSIONE_QUINTO = "modulo cessione quinto"
    CEDOLINO = "cedolino"
    CARTA_IDENTITA = "carta d'identità"
    PATENTE = "patente"
    DOCUMENTI_FISCALI = "documenti fiscali"
    ALTRO = "altro"

class LoanDetail(BaseModel):
    bank_name: Optional[str] = Field(None, description="Name of the Bank or Financial Institution")
    start_date: Optional[str] = Field(None, description="Start date of the loan (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Expiry date of the loan (YYYY-MM-DD)")
    amount_installment: Optional[str] = Field(None, description="Installment amount (Importo rata)")
    duration_total: Optional[str] = Field(None, description="Total duration (Durata totale)")
    duration_residual: Optional[str] = Field(None, description="Residual duration (Durata residua)")

class PersonalInfo(BaseModel):
    name: Optional[str] = Field(None, description="First name")
    surname: Optional[str] = Field(None, description="Last name")
    fiscal_code: Optional[str] = Field(None, description="Italian Fiscal Code (Codice Fiscale)")

class AnalysisResult(BaseModel):
    document_type: DocumentType = Field(..., description="The type of the document")
    personal_info: PersonalInfo = Field(..., description="Extracted personal information")
    loans: List[LoanDetail] = Field(default_factory=list, description="List of extracted loan/cession details (only for financial docs)")

class ProcessingState(BaseModel):
    processed_files: List[str] = Field(default_factory=list, description="List of file paths that have been processed")
    last_run_timestamp: str = Field(..., description="Timestamp of the last run")
