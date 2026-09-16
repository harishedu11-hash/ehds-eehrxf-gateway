from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class LegacyCondition(BaseModel):
    code: str = Field(description="Diagnosis code, e.g. ICD-10")
    display: str = Field(description="Clinical description")
    onset_date: Optional[date] = None

class LegacyMedication(BaseModel):
    name: str = Field(description="Brand or generic medication name")
    dose: str = Field(description="Dosing instructions, e.g. 500mg daily")
    atc_code: Optional[str] = Field(None, description="Anatomical Therapeutic Chemical code")

class LegacyPatientRecord(BaseModel):
    national_id: str = Field(description="National citizen or health identifier")
    country_code: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code, e.g. 'FR', 'DE'")
    given_name: str
    family_name: str
    birth_date: date
    gender: str = Field(description="administrative gender: male, female, other, unknown")
    conditions: List[LegacyCondition] = []
    medications: List[LegacyMedication] = []
