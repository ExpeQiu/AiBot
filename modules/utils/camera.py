import cv2
from config.config import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    
    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release() 