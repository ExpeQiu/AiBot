import numpy as np
import pickle
import os

class FaceDatabase:
    def __init__(self, database_file='face_database.pkl'):
        self.database_file = database_file
        self.known_faces = {}  # {name: face_encoding}
        self.load_database()
    
    def load_database(self):
        """加载人脸数据库"""
        if os.path.exists(self.database_file):
            with open(self.database_file, 'rb') as f:
                self.known_faces = pickle.load(f)
    
    def save_database(self):
        """保存人脸数据库"""
        with open(self.database_file, 'wb') as f:
            pickle.dump(self.known_faces, f)
    
    def add_face(self, name, face_encoding):
        """添加新的人脸特征"""
        self.known_faces[name] = face_encoding
        self.save_database()
    
    def identify_face(self, face_encoding, threshold=0.6):
        """识别人脸"""
        if not self.known_faces:
            return None, None
            
        min_distance = float('inf')
        best_match = None
        
        # 与数据库中的人脸特征进行比对
        for name, known_encoding in self.known_faces.items():
            distance = np.linalg.norm(face_encoding - known_encoding)
            if distance < min_distance:
                min_distance = distance
                best_match = name
        
        if min_distance <= threshold:
            return best_match, min_distance
        return None, None 