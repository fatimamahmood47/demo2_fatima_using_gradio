# routers/normalized_order.py (MODIFIED)
from fastapi import APIRouter
from typing import List

# programmer defined schema 
from app.schemas.normalized_order import NormalizedOrder 
from app.schemas.converted_order import ConvertedProduct

# routers 
from app.services.order_converter import ConvertProduct

router = APIRouter(
    prefix="/normalized_order",
    tags=["normalized_order"]
)

@router.get("/")
async def list_orders():
    return {"message": "This endpoint receive normalize order and convert external product names to internal ones. along with internal product id"}

@router.post("/convert_internal", response_model=List[ConvertedProduct])  # Changed response model
async def upload_csv(normalized_order: NormalizedOrder): 
    converter = ConvertProduct(normalized_order)
    return converter.convert_single_order()  # This now returns a list directly