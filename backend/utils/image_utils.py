import cv2
import numpy as np
from PIL import Image

def decode_image(content: bytes) -> np.ndarray:
    image = np.frombuffer(content, np.uint8)
    return cv2.imdecode(image, cv2.IMREAD_COLOR)

def encode_image(image: np.ndarray) -> bytes:
    _, encoded_image = cv2.imencode(".png", image)
    return encoded_image.tobytes()

def preprocess_image(image: Image.Image) -> np.ndarray:
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return cv2.resize(image_cv, (640, 640))
