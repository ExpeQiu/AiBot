import cv2
import numpy as np
import dlib
from scipy.spatial import distance as dist
from config.config import LIVENESS_DETECTION
from modules.utils.logger import Logger

class LivenessDetector:
    def __init__(self):
        self.logger = Logger.get_logger("LivenessDetector")
        self.last_check_time = 0
        self.last_eye_state = None
        self.blink_count = 0
        self.last_landmarks = None
        self.movement_history = []
        self.expression_history = []
        
    def detect_liveness(self, frame, face_shape):
        """增强的活体检测"""
        current_time = time.time()
        if current_time - self.last_check_time < LIVENESS_DETECTION['check_interval']:
            return True
            
        self.last_check_time = current_time
        
        # 转换关键点为numpy数组
        landmarks = np.array([[p.x, p.y] for p in face_shape.parts()])
        
        # 1. 眨眼检测
        eye_aspect_ratio = self._get_eye_aspect_ratio(landmarks)
        blink_detected = self._check_blink(eye_aspect_ratio)
        
        # 2. 头部姿态估计
        head_movement = self._detect_head_movement(landmarks)
        
        # 3. 表情变化检测
        expression_change = self._detect_expression_change(landmarks)
        
        # 4. 纹理分析（检测打印照片）
        texture_score = self._analyze_texture(frame, landmarks)
        
        # 5. 红外反射检测（如果有红外摄像头）
        # ir_score = self._check_ir_reflection(frame)
        
        # 综合评分
        liveness_score = self._compute_liveness_score(
            blink_detected,
            head_movement,
            expression_change,
            texture_score
        )
        
        is_live = liveness_score >= LIVENESS_DETECTION['threshold']
        
        if is_live:
            self.logger.info(f"Liveness check passed (score: {liveness_score:.2f})")
        else:
            self.logger.warning(f"Possible spoofing attempt (score: {liveness_score:.2f})")
            
        return is_live
    
    def _get_eye_aspect_ratio(self, landmarks):
        """计算眼睛纵横比"""
        # 假设使用dlib的68点标记，眼睛点的索引
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        
        # 计算眼睛的纵横比
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        
        return (left_ear + right_ear) / 2.0
    
    def _eye_aspect_ratio(self, eye):
        """计算单眼纵横比"""
        # 计算垂直方向的两组点之间的距离
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        # 计算水平方向的距离
        C = dist.euclidean(eye[0], eye[3])
        # 计算纵横比
        ear = (A + B) / (2.0 * C)
        return ear
    
    def _check_blink(self, eye_aspect_ratio):
        """检测眨眼"""
        if eye_aspect_ratio < LIVENESS_DETECTION['blink_threshold']:
            if self.last_eye_state != 'closed':
                self.blink_count += 1
            self.last_eye_state = 'closed'
        else:
            self.last_eye_state = 'open'
        
        return self.blink_count > 0
    
    def _detect_head_movement(self, landmarks):
        """检测头部运动"""
        if self.last_landmarks is not None:
            movement = np.mean(np.abs(landmarks - self.last_landmarks))
            self.movement_history.append(movement)
            if len(self.movement_history) > 10:
                self.movement_history.pop(0)
        
        self.last_landmarks = landmarks.copy()
        
        if len(self.movement_history) >= 3:
            return np.mean(self.movement_history) > LIVENESS_DETECTION['head_move_threshold']
        return False
    
    def _detect_expression_change(self, landmarks):
        """检测表情变化"""
        # 计算嘴部和眉毛的关键点变化
        mouth_points = landmarks[48:68]
        mouth_shape = self._get_shape_features(mouth_points)
        
        if len(self.expression_history) > 0:
            change = np.abs(mouth_shape - self.expression_history[-1])
            expression_changed = np.mean(change) > LIVENESS_DETECTION['mouth_threshold']
        else:
            expression_changed = False
            
        self.expression_history.append(mouth_shape)
        if len(self.expression_history) > 10:
            self.expression_history.pop(0)
            
        return expression_changed
    
    def _analyze_texture(self, frame, landmarks):
        """分析图像纹理以检测打印照片"""
        # 提取面部区域
        hull = cv2.convexHull(landmarks)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, hull, 255)
        
        # 应用LBP或其他纹理分析
        face_texture = frame[mask > 0]
        
        # 计算纹理特征
        gray = cv2.cvtColor(face_texture, cv2.COLOR_BGR2GRAY)
        gradient_magnitude = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 1))
        texture_score = np.mean(gradient_magnitude)
        
        return texture_score > 50  # 阈值需要根据实际情况调整
    
    def _compute_liveness_score(self, blink_detected, head_movement, 
                              expression_change, texture_score):
        """计算综合活体得分"""
        weights = {
            'blink': 0.3,
            'movement': 0.3,
            'expression': 0.2,
            'texture': 0.2
        }
        
        score = (
            weights['blink'] * float(blink_detected) +
            weights['movement'] * float(head_movement) +
            weights['expression'] * float(expression_change) +
            weights['texture'] * float(texture_score)
        )
        
        return score 