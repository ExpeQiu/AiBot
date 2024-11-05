import cv2
import dlib
import numpy as np
from config.config import FACE_DETECTION_CONFIDENCE
from .face_database import FaceDatabase
from modules.utils.logger import Logger
from .face_quality import FaceQualityAssessor, LivenessDetector
import collections
from .face_matcher import FaceMatcher
from .liveness_detection import LivenessDetector

class FaceDetector:
    def __init__(self):
        self.logger = Logger.get_logger("FaceDetector")
        self.logger.info("Initializing face detector")
        # 使用dlib的人脸检测器
        self.detector = dlib.get_frontal_face_detector()
        # 加载人脸特征点预测器
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        # 加载人脸识别模型
        self.face_rec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
        self.face_db = FaceDatabase()
        self.quality_assessor = FaceQualityAssessor()
        self.liveness_detector = LivenessDetector()
        self.face_tracker = collections.defaultdict(list)  # 用于多帧确认
        self.pose_estimator = None  # TODO: 添加姿态估计器
        self.face_matcher = FaceMatcher()
        
    def detect_faces(self, frame):
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 检测人脸
        faces = self.detector(gray)
        
        face_locations = []
        face_encodings = []
        
        for face in faces:
            # 获取人脸区域和特征编码
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            face_locations.append((x1, y1, x2, y2))
            
            # 获取人脸特征点并计算编码
            shape = self.predictor(gray, face)
            face_encoding = np.array(self.face_rec.compute_face_descriptor(frame, shape))
            face_encodings.append(face_encoding)
            
        return face_locations, face_encodings 
    
    def detect_and_identify_faces(self, frame):
        """检测并识别人脸"""
        face_locations, face_encodings = self.detect_faces(frame)
        identities = []
        confirmed_faces = []
        
        if face_encodings:
            # 批量特征匹配
            names, distances = self.face_matcher.batch_match_faces(face_encodings)
            
            for i, (face_location, name, distance) in enumerate(zip(face_locations, names, distances)):
                # 质量检查
                quality_ok, quality_scores = self.quality_assessor.assess_quality(frame, face_location)
                if not quality_ok:
                    continue
                
                # 获取面部关键点
                shape = self.predictor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                     dlib.rectangle(*face_location))
                
                # 活体检测
                if not self.liveness_detector.detect_liveness(frame, shape):
                    continue
                
                # 多帧确认
                if name:
                    self.face_tracker[name].append((face_location, distance))
                    if len(self.face_tracker[name]) >= FACE_TRACKING['confirm_frames']:
                        recent_distances = [d for _, d in self.face_tracker[name][-FACE_TRACKING['confirm_frames']:]]
                        if np.mean(recent_distances) <= FACE_TRACKING['tracking_threshold']:
                            confirmed_faces.append(face_location)
                            identities.append(name)
                            self.logger.info(f"Confirmed identity: {name}")
                            continue
                
                identities.append("Unknown")
                
        return confirmed_faces, face_encodings, identities
    
    def _cleanup_tracking_data(self):
        """清理过期的人脸跟踪数据"""
        for name in list(self.face_tracker.keys()):
            if len(self.face_tracker[name]) > FACE_TRACKING['max_frames_missing']:
                self.face_tracker[name] = self.face_tracker[name][-FACE_TRACKING['max_frames_missing']:]
    
    def register_face(self, frame, name):
        """注册新的人脸"""
        self.logger.info(f"Attempting to register new face for: {name}")
        result = super().register_face(frame, name)
        if result:
            self.logger.info(f"Successfully registered face for: {name}")
        else:
            self.logger.warning(f"Failed to register face for: {name}")
        return result