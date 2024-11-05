import time
from config.config import PID_KP, PID_KI, PID_KD

class PIDController:
    def __init__(self, kp=PID_KP, ki=PID_KI, kd=PID_KD):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.last_time = time.time()
        
    def compute(self, error):
        current_time = time.time()
        dt = current_time - self.last_time
        
        # 计算积分项
        self.integral += error * dt
        
        # 计算微分项
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        
        # PID输出
        output = (self.kp * error + 
                 self.ki * self.integral + 
                 self.kd * derivative)
        
        # 更新状态
        self.prev_error = error
        self.last_time = current_time
        
        return output 