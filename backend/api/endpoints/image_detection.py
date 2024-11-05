from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Response
from typing import List
import io
from PIL import Image
from backend.core.logger import logger
from backend.utils.prediction_utils import Predictions, Visualizer
from backend.utils.image_utils import decode_image, encode_image

visualizer = Visualizer()

router = APIRouter()

@router.post("/detect")
async def detect_image(request: Request, file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        logger.error(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG and PNG are supported.")
    
    try:
        contents = await file.read()
        image = decode_image(contents)
        
        model = request.app.state.model
        results = model.predict(image)
        
        # abcd_model = request.app.state.abcd 
        # abcd_features = abcd_model.extract_features(image)
        # abcd_results = abcd_model.predict(image)
        # как обрабатывать результаты?
        
        annotated_image = visualizer.plot_predictions(image, results)
        bytes_image = encode_image(annotated_image)
        
        logger.info(f"Detection results: {results}")
        return Response(content=bytes_image, media_type="image/png")
    except Exception as e:
        logger.exception("Error during detection")
        raise HTTPException(status_code=500, detail=str(e))
