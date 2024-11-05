import cv2
import numpy as np
from config.config import FACE_QUALITY
from modules.utils.logger import Logger

class FaceQualityAssessor:
    def __init__(self):
        self.logger = Logger.get_logger("FaceQualityAssessor")
        
    def assess_quality(self, frame, face_location):
        """评估人脸图像质量"""
        x1, y1, x2, y2 = face_location
        face_img = frame[y1:y2, x1:x2]
        
        quality_scores = {}
        
        # 检查人脸大小
        face_size = min(x2-x1, y2-y1)
        quality_scores['size'] = face_size >= FACE_QUALITY['min_face_size']
        
        # 检查亮度
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        quality_scores['brightness'] = brightness >= FACE_QUALITY['min_brightness']
        
        # 检查清晰度
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(laplacian)
        quality_scores['sharpness'] = sharpness >= FACE_QUALITY['min_sharpness']
        
        # 计算总体质量分数
        overall_score = sum(quality_scores.values()) / len(quality_scores)
        
        return overall_score >= FACE_QUALITY['confidence_threshold'], quality_scores

class LivenessDetector:
    def __init__(self):
        self.logger = Logger.get_logger("LivenessDetector")
        self.last_check_time = 0
        self.blink_detector = None  # 使用dlib的眼睛关键点检测
        self.last_eye_state = None
        self.blink_count = 0
        
    def detect_liveness(self, frame, face_shape):
        """检测活体"""
        current_time = time.time()
        if current_time - self.last_check_time < LIVENESS_DETECTION['check_interval']:
            return True
            
        self.last_check_time = current_time
        
        # 检测眨眼
        eye_state = self._check_eye_state(face_shape)
        if eye_state != self.last_eye_state:
            if eye_state == 'closed':
                self.blink_count += 1
        self.last_eye_state = eye_state
        
        # 检测头部运动
        head_movement = self._check_head_movement(face_shape)
        
        # 综合判断
        is_live = (self.blink_count > 0 or head_movement)
        
        if is_live:
            self.logger.info("Liveness check passed")
        else:
            self.logger.warning("Possible spoofing attempt detected")
            
        return is_live
        
    def _check_eye_state(self, face_shape):
        """检查眼睛状态（开/闭）"""
        # 使用面部关键点计算眼睛纵横比(EAR)
        # 实际实现需要使用dlib的面部关键点
        pass
        
    def _check_head_movement(self, face_shape):
        """检测头部运动"""
        # 使用连续帧中的面部关键点计算头部姿态变化
        pass 