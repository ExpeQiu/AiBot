import torch
import torch.nn as nn
import numpy as np
import cv2
from torchvision import transforms
from config.config import BEHAVIOR_DETECTION, BEHAVIOR_CLASSES, ALERT_CONFIG
from modules.utils.logger import Logger
import time
import threading
import pygame

class BehaviorDetectionModel(nn.Module):
    def __init__(self):
        super(BehaviorDetectionModel, self).__init__()
        # 使用预训练的ResNet作为特征提取器
        self.backbone = torch.hub.load('pytorch/vision:v0.10.0', 
                                     'resnet50', pretrained=True)
        # 修改最后的全连接层以适应行为分类
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, len(BEHAVIOR_CLASSES))
        )
        
    def forward(self, x):
        return self.backbone(x)

class BehaviorDetector:
    def __init__(self, speech_recognizer):
        self.logger = Logger.get_logger("BehaviorDetector")
        self.speech = speech_recognizer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载行为检测模型
        self.model = BehaviorDetectionModel()
        self.model.load_state_dict(torch.load(BEHAVIOR_DETECTION['model_path']))
        self.model.to(self.device)
        self.model.eval()
        
        # 初始化姿态估计器
        self.pose_estimator = self._init_pose_estimator()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        # 状态变量
        self.last_detection_time = 0
        self.detection_history = []
        self.last_alert_time = 0
        self.is_monitoring = True
        
        # 初始化报警声音
        pygame.mixer.init()
        self.alert_sound = pygame.mixer.Sound(ALERT_CONFIG['alert_sound'])
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _init_pose_estimator(self):
        """初始化姿态估计器"""
        return cv2.dnn.readNetFromTensorflow(BEHAVIOR_DETECTION['pose_model_path'])
    
    def detect_behavior(self, frame):
        """检测行为"""
        current_time = time.time()
        if current_time - self.last_detection_time < BEHAVIOR_DETECTION['detection_interval']:
            return None
            
        self.last_detection_time = current_time
        
        try:
            # 姿态估计
            pose_data = self._estimate_pose(frame)
            
            # 行为检测
            with torch.no_grad():
                # 预处理图像
                image_tensor = self.transform(frame).unsqueeze(0).to(self.device)
                
                # 模型预测
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                behavior_idx = torch.argmax(probabilities).item()
                confidence = probabilities[0][behavior_idx].item()
                
                behavior = BEHAVIOR_CLASSES[behavior_idx]
                
                # 结合姿态信息进行判断
                if behavior == 'fall' and confidence > BEHAVIOR_DETECTION['fall_threshold']:
                    if self._confirm_fall_detection(pose_data):
                        self._handle_alert('fall')
                        return 'fall'
                elif confidence > BEHAVIOR_DETECTION['abnormal_threshold']:
                    self._update_detection_history(behavior)
                    if self._check_continuous_abnormal():
                        self._handle_alert(behavior)
                        return behavior
                
                return 'normal'
                
        except Exception as e:
            self.logger.error(f"Behavior detection error: {str(e)}")
            return None
    
    def _estimate_pose(self, frame):
        """估计人体姿态"""
        blob = cv2.dnn.blobFromImage(frame, 1.0, (368, 368), 
                                    (127.5, 127.5, 127.5), swapRB=True, crop=False)
        self.pose_estimator.setInput(blob)
        output = self.pose_estimator.forward()
        
        # 处理输出，获取关键点
        points = []
        for i in range(output.shape[1]):
            heatMap = output[0, i, :, :]
            _, conf, _, point = cv2.minMaxLoc(heatMap)
            x = (frame.shape[1] * point[0]) / output.shape[3]
            y = (frame.shape[0] * point[1]) / output.shape[2]
            points.append((int(x), int(y)) if conf > 0.1 else None)
            
        return points
    
    def _confirm_fall_detection(self, pose_data):
        """确认跌倒检测"""
        if not pose_data:
            return False
            
        # 分析姿态数据确认是否跌倒
        # 这里可以添加更复杂的姿态分析逻辑
        head_point = pose_data[0]
        hip_point = pose_data[8]
        
        if head_point and hip_point:
            # 检查头部和臀部的相对位置
            vertical_distance = abs(head_point[1] - hip_point[1])
            horizontal_distance = abs(head_point[0] - hip_point[0])
            
            # 如果水平距离大于垂直距离，可能是跌倒
            return horizontal_distance > vertical_distance
            
        return False
    
    def _update_detection_history(self, behavior):
        """更新检测历史"""
        self.detection_history.append((time.time(), behavior))
        # 清理旧记录
        current_time = time.time()
        self.detection_history = [
            (t, b) for t, b in self.detection_history 
            if current_time - t <= BEHAVIOR_DETECTION['detection_interval'] * 
            BEHAVIOR_DETECTION['min_detection_frames']
        ]
    
    def _check_continuous_abnormal(self):
        """检查连续异常行为"""
        if len(self.detection_history) < BEHAVIOR_DETECTION['min_detection_frames']:
            return False
            
        # 检查最近几帧是否都是异常行为
        recent_behaviors = [b for _, b in self.detection_history[-BEHAVIOR_DETECTION['min_detection_frames']:]]
        return all(b != 'normal' for b in recent_behaviors)
    
    def _handle_alert(self, behavior_type):
        """处理报警"""
        current_time = time.time()
        if current_time - self.last_alert_time < ALERT_CONFIG['alert_interval']:
            return
            
        self.last_alert_time = current_time
        
        # 播放报警声音
        self.alert_sound.play()
        
        # 语音提醒
        alert_message = f"警告！检测到{behavior_type}行为！"
        self.speech.speak(alert_message)
        
        self.logger.warning(f"Abnormal behavior detected: {behavior_type}")
        
        # TODO: 实现紧急联系人通知功能
    
    def _monitor_loop(self):
        """持续监控循环"""
        while self.is_monitoring:
            time.sleep(0.1)  # 避免过度占用CPU
    
    def cleanup(self):
        """清理资源"""
        self.is_monitoring = False
        self.monitor_thread.join()
        pygame.mixer.quit() 