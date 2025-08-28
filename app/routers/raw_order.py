from fastapi import APIRouter, UploadFile, File, HTTPException
import json

# services 
from app.services.order_normalizer import NormalizeCsvOrder 
# from app.services.order_normalizer import NormalizePDFOrder 
# common output structure 
from app.schemas.normalized_order import NormalizedOrder
# detection schema
from app.schemas.detection import DetectionConfig

router = APIRouter(
    prefix="/raw_order",
    tags=["raw_order"]
)

@router.get("/")
async def list_orders():
    return {"message": "Raw order endpoint. Use /csv or /pdf to upload files."}

@router.post("/normalize_csv", response_model=NormalizedOrder)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file to process"),
    detection: UploadFile = File(..., description="Detection JSON configuration file")
):
    """
    Upload a CSV file and detection JSON configuration.
    The detection JSON should contain column mapping information.
    """
    # Read and parse detection JSON file
    try:
        detection_contents = await detection.read()
        detection_json = detection_contents.decode('utf-8')
        detection_dict = json.loads(detection_json)
        detection_config = DetectionConfig(**detection_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid detection JSON file: {str(e)}")
    
    # Read CSV file and process
    
    try:
        # contents = await file.read()
        # normalizer = NormalizeCsvOrder(contents)
        # converted_data = normalizer.convert_to_component_list()
        # return converted_data 
            # app/routers/raw_order.py (inside /normalize_csv)
        contents = await file.read()
        normalizer = NormalizeCsvOrder(contents, detection_config)  # pass detection_config
        converted_data = normalizer.convert_to_component_list()
        return converted_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@router.post("/normalize_pdf", response_model=NormalizedOrder) 
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to process"),
    detection: UploadFile = File(..., description="Detection JSON configuration file")
):
    """
    Upload a PDF file and detection JSON configuration.
    The detection JSON should contain column mapping information.
    """
    # Read and parse detection JSON file
    try:
        detection_contents = await detection.read()
        detection_json = detection_contents.decode('utf-8')
        detection_dict = json.loads(detection_json)
        detection_config = DetectionConfig(**detection_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid detection JSON file: {str(e)}")
    
    # Read PDF file and process
    try:
        contents = await file.read() 
        normalizer = NormalizePDFOrder(contents)
        normalized_data = normalizer.convert_to_component_list()
        return normalized_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")