from fastapi import APIRouter, WebSocket, HTTPException
from backend.core.logger import logger
import os
import cv2
import numpy as np
from backend.utils.prediction_utils import Predictions, Visualizer

def remove_file(file_path):
    os.remove(file_path)

visualizer = Visualizer()

router = APIRouter()

@router.websocket("/ws/video_real_time")
async def detect_video(websocket: WebSocket):
    logger.info(f"Started predicting real-time...")
    await websocket.accept()
    try:
        while True:
            model = websocket.app.state.model
            
            frame_data = await websocket.receive_bytes()
            np_frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

            results = model.predict(frame, conf=0.65)
            annotated_frame = visualizer.plot_predictions(frame, results)

            _, buffer = cv2.imencode(".png", annotated_frame)
            await websocket.send_bytes(buffer.tobytes())
    except Exception as e:
        logger.exception("Error during real-time detection")
    finally:
        logger.info("Stopping predicting real-time...")
        await websocket.close()