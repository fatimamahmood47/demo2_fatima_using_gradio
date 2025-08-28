# schemas/normalized_order.py (MODIFIED)
from pydantic import BaseModel
from typing import List

class ConstructionComponent(BaseModel):
    external_product_name: str
    external_product_code: str
    quantities: float   # ✅ now accepts 13.166, 71.8, 1.325, etc.


class NormalizedOrder(BaseModel):
    components: List[ConstructionComponent]

# schemas/converted_order.py (MODIFIED)
from pydantic import BaseModel
from typing import List

class Candidate(BaseModel):
    master_id: int
    product_name: str  # Note: using hyphen as shown in target JSON
    product_code: str
    score: float

class PreConvert(BaseModel):
    id: int
    mixed: str
    quantity: int

class Converted(BaseModel):
    candidates: List[Candidate]
    quantity: int

class ConvertedProduct(BaseModel):
    pre_convert: PreConvert  # Note: using underscore as shown in target JSON
    converted: Converted

class ConvertOrder(BaseModel):
    records: List[ConvertedProduct]  # This will be a list directly