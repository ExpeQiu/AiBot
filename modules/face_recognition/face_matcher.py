import numpy as np
from sklearn.neighbors import KDTree
import threading
from modules.utils.logger import Logger

class FaceMatcher:
    def __init__(self):
        self.logger = Logger.get_logger("FaceMatcher")
        self.face_tree = None
        self.names = []
        self.encodings = []
        self.lock = threading.Lock()
        
    def update_database(self, known_faces):
        """更新人脸特征数据库并构建KD树"""
        with self.lock:
            self.names = list(known_faces.keys())
            self.encodings = np.array(list(known_faces.values()))
            if len(self.encodings) > 0:
                self.face_tree = KDTree(self.encodings)
                self.logger.info("Face matching KD-tree updated")
            else:
                self.face_tree = None
    
    def match_face(self, face_encoding, threshold=0.6):
        """使用KD树进行快速特征匹配"""
        with self.lock:
            if self.face_tree is None or len(self.encodings) == 0:
                return None, None
                
            # 使用KD树查找最近邻
            distances, indices = self.face_tree.query(
                face_encoding.reshape(1, -1), 
                k=1
            )
            
            distance = distances[0][0]
            if distance <= threshold:
                return self.names[indices[0][0]], distance
                
            return None, None
    
    def batch_match_faces(self, face_encodings, threshold=0.6):
        """批量匹配多个人脸特征"""
        with self.lock:
            if self.face_tree is None or len(self.encodings) == 0:
                return [None] * len(face_encodings), [None] * len(face_encodings)
                
            # 批量查询KD树
            distances, indices = self.face_tree.query(
                np.array(face_encodings), 
                k=1
            )
            
            names = []
            match_distances = []
            
            for distance, idx in zip(distances, indices):
                if distance <= threshold:
                    names.append(self.names[idx[0]])
                    match_distances.append(distance)
                else:
                    names.append(None)
                    match_distances.append(None)
                    
            return names, match_distances 