import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    model: str = "yolo-nas-l"
    checkpoint_path: str = "models/yolonas-l.pth"
    classes: List = ['AKIEC', 'BCC', 'BKL', 'DF', 'MEL', 'NV', 'VASC']
    num_classes: int = 7
    abcd_model: str = "models/rf_abcd_classifier.joblib"

    class Config:
        env_file = ".env"

settings = Settings()
