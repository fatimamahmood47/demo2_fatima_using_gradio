# schemas/normalized_order.py (MODIFIED)
from pydantic import BaseModel
from typing import List

class ConstructionComponent(BaseModel):
    external_product_name: str      # e.g., "ケーブル IV1.25sq 黄"
    external_product_code: str      # e.g., "abc4123"
    quantities: int                 # e.g., 2

class NormalizedOrder(BaseModel):
    components: List[ConstructionComponent]

# schemas/converted_order.py (MODIFIED)
from pydantic import BaseModel
from typing import List
from pydantic import Field

class Candidate(BaseModel):
    master_id: int
    product_name: str = Field(alias="product-name")  # Handle hyphen in JSON
    product_code: str = Field(alias="product-code")
    score: float

    class Config:
        populate_by_name = True  # Allow both field names and aliases

class PreConvert(BaseModel):
    id: int
    mixed: str
    quantity: float   # ✅ now supports decimal quantities


# class Converted(BaseModel):
#     candidates: List[Candidate]
#     quantity: int
class Converted(BaseModel):
    candidates: List[Candidate]
    quantity: float   # ✅

class ConvertedProduct(BaseModel):
    pre_convert: PreConvert = Field(alias="pre-convert")  # Handle hyphen in JSON
    converted: Converted

    class Config:
        populate_by_name = True  # Allow both field names and aliases

class ConvertOrder(BaseModel):
    records: List[ConvertedProduct]