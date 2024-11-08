from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Response, BackgroundTasks
import io
from backend.core.logger import logger
import os

def remove_file(file_path):
    os.remove(file_path)


router = APIRouter()

@router.post("/detect_video")
async def detect_video(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    supported_formats = {"video/mp4": "mp4", "video/avi": "avi"}
    
    if file.content_type not in supported_formats:
        logger.error(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid video type. Only MP4 and AVI are supported.")
    
    try:
        contents = await file.read()
        
        file_extension = supported_formats[file.content_type]
        input_video_path = f"temp_input_video.{file_extension}"
        output_video_path = f"temp_output_video.{file_extension}"
        
        with open(input_video_path, "wb") as f:
            f.write(contents)
        
        model = request.app.state.model
        predictions = model.predict_video(input_video_path, conf=0.65)
        predictions.save(output_path=output_video_path, show_confidence=True)
        
        with open(output_video_path, "rb") as f:
            video_bytes = f.read()
        
        # background_tasks.add_task(remove_file, input_video_path)
        # background_tasks.add_task(remove_file, output_video_path)
        
        return Response(content=video_bytes, media_type=file.content_type, background=background_tasks)
    
    except Exception as e:
        logger.exception("Error during video detection")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect_video_fullsize")
async def detect_video_fullsize(request: Request, file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    supported_formats = {"video/mp4": "mp4", "video/avi": "avi"}
    
    if file.content_type not in supported_formats:
        logger.error(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid video type. Only MP4 and AVI are supported.")
    
    try:
        contents = await file.read()
        
        file_extension = supported_formats[file.content_type]
        input_video_path = f"temp_input_video.{file_extension}"
        output_video_path = f"temp_output_video.{file_extension}"
        
        with open(input_video_path, "wb") as f:
            f.write(contents)
        
        model = request.app.state.model
        predictions = model.predict_video(input_video_path, skip_image_resizing=True, conf=0.65)
        predictions.save(output_path=output_video_path, show_confidence=True)
        
        with open(output_video_path, "rb") as f:
            video_bytes = f.read()
        
        os.remove(input_video_path)
        os.remove(output_video_path)
        
        return Response(content=video_bytes, media_type=file.content_type)
    
    except Exception as e:
        logger.exception("Error during video detection")
        raise HTTPException(status_code=500, detail=str(e))
