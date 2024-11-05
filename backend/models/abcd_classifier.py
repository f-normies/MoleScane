from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np
from typing import List

from backend.core.config import settings
from backend.core.logger import logger
from backend.utils.extract_abcd import process_image

class ABCDClassifier:
    def __init__(self):
        self.model = self.load_model()
        self.scaler = StandartScaler()
        logger.info("All set!")

    def load_model(self):
        logger.info(f"Loading ABCDClassifier...")
        try:
            model = joblib.load(settings.model_path)
            logger.info("ABCDClassifier loaded successfully")
            return model
        except Exception as e:
            logger.exception("Failed to load ABCDClassifier")
            raise e

    def extract_features(self, image: np.ndarray):
        return process_image(image)[1:]
    
    def predict(self, image: np.ndarray) -> str:
        logger.debug("Predicting ABCD features...")
        features = extract_features(image)
        features = np.array(features).reshape(1, -1)
        features = self.scaler.transform(features)
        prediction = self.model.predict(features)
        logger.debug("Prediction completed")
        return setting.classes[prediction]