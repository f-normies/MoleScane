import torch
from super_gradients.training import models
from backend.core.config import settings
from backend.core.logger import logger
import numpy as np
import supervision as sv
from typing import List

from backend.utils.prediction_utils import Predictions

class YOLONAS:
    def __init__(self):
        self.model = self.load_model()
        logger.info("All set!")

    def load_model(self):
        logger.info(f"Loading YOLO-NAS model from {settings.checkpoint_path}...")
        try:
            device = (
                torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
            )
            model = models.get(
                model_name=settings.model,
                num_classes=settings.num_classes,
                checkpoint_path=settings.checkpoint_path,
            ).to(device)
            logger.info("YOLO-NAS model loaded successfully")
            return model
        except Exception as e:
            logger.exception("Failed to load YOLO-NAS model")
            raise e

    def predict(self, image: np.ndarray, skip_image_resizing: bool = False, conf: float = 0.5) -> Predictions:
        logger.debug("Performing inference...")
        predictions = self.model.predict(image, 
                                         skip_image_resizing=skip_image_resizing, 
                                         conf=conf, 
                                         iou=0.5
                                         )
        logger.debug("Inference completed")
        detections = sv.Detections.from_yolo_nas(predictions)
        labels = [settings.classes[i] for i in predictions.prediction.labels]
        return Predictions(detections=detections, labels=labels)
    
    def predict_batch(self, images: List[str], skip_image_resizing: bool = False, conf: float = 0.5):
        logger.debug("Performing batch inference...")
        predictions = self.model.predict(images, 
                                         skip_image_resizing=skip_image_resizing, 
                                         conf=conf, 
                                         iou=0.5
                                         )
        logger.debug("Inference completed")
        return predictions

    def predict_video(self, video: str, skip_image_resizing: bool = False, conf: float = 0.5) -> Predictions:
        logger.debug("Performing inference...")
        predictions = self.model.predict(video, 
                                         skip_image_resizing=skip_image_resizing, 
                                         conf=conf, 
                                         iou=0.5
                                         )
        logger.debug("Inference completed")
        return predictions