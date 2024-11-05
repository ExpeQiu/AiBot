import RPi.GPIO as GPIO
from config.config import (
    MOTOR_LEFT_FORWARD, 
    MOTOR_LEFT_BACKWARD,
    MOTOR_RIGHT_FORWARD, 
    MOTOR_RIGHT_BACKWARD,
    BASE_SPEED,
    MAX_SPEED,
    MIN_SPEED,
    TURN_SPEED
)
from modules.utils.logger import Logger

class MotorController:
    def __init__(self):
        self.logger = Logger.get_logger("MotorController")
        self.logger.info("Initializing motor controller")
        # 设置GPIO模式
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # 设置电机引脚为输出
        self.pins = [
            MOTOR_LEFT_FORWARD, 
            MOTOR_LEFT_BACKWARD,
            MOTOR_RIGHT_FORWARD, 
            MOTOR_RIGHT_BACKWARD
        ]
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            
        # 创建PWM对象，频率为100Hz
        self.pwm_left_forward = GPIO.PWM(MOTOR_LEFT_FORWARD, 100)
        self.pwm_left_backward = GPIO.PWM(MOTOR_LEFT_BACKWARD, 100)
        self.pwm_right_forward = GPIO.PWM(MOTOR_RIGHT_FORWARD, 100)
        self.pwm_right_backward = GPIO.PWM(MOTOR_RIGHT_BACKWARD, 100)
        
        # 启动PWM
        self.pwm_left_forward.start(0)
        self.pwm_left_backward.start(0)
        self.pwm_right_forward.start(0)
        self.pwm_right_backward.start(0)
        
        self.is_avoiding = False
    
    def move_with_obstacle_avoidance(self, control_signal, sensor_data):
        """使用改进的避障逻辑控制运动"""
        action = sensor_data.analyze_surroundings()
        distances = sensor_data.get_all_distances()
        
        if action == 'backward':
            self.logger.warning("Obstacle too close, moving backward")
            self.move_backward()
            return
            
        if action in ['turn_left', 'turn_right']:
            self.logger.info(f"Avoiding obstacle: {action}")
            if action == 'turn_left':
                self.turn_left(TURN_SPEED)
            else:
                self.turn_right(TURN_SPEED)
            return
            
        # 正常跟随模式
        optimal_speed = sensor_data.get_optimal_speed(BASE_SPEED, distances)
        self._move_with_speed(control_signal, optimal_speed)
    
    def _move_with_speed(self, control_signal, base_speed):
        """根据控制信号和基础速度计算电机速度"""
        control_signal = max(-100, min(100, control_signal))
        
        if control_signal > 0:  # 向右转
            left_speed = base_speed
            right_speed = base_speed * (1 - control_signal/100)
        else:  # 向左转
            left_speed = base_speed * (1 + control_signal/100)
            right_speed = base_speed
            
        # 确保速度在有效范围内
        left_speed = max(MIN_SPEED, min(MAX_SPEED, left_speed))
        right_speed = max(MIN_SPEED, min(MAX_SPEED, right_speed))
        
        self.logger.debug(f"Motor speeds - Left: {left_speed}, Right: {right_speed}")
        
        self.pwm_left_forward.ChangeDutyCycle(left_speed)
        self.pwm_right_forward.ChangeDutyCycle(right_speed)
        self.pwm_left_backward.ChangeDutyCycle(0)
        self.pwm_right_backward.ChangeDutyCycle(0)
    
    def turn_left(self, speed=TURN_SPEED):
        """左转"""
        self.pwm_left_forward.ChangeDutyCycle(0)
        self.pwm_right_forward.ChangeDutyCycle(speed)
        self.pwm_left_backward.ChangeDutyCycle(speed)
        self.pwm_right_backward.ChangeDutyCycle(0)
    
    def turn_right(self, speed=TURN_SPEED):
        """右转"""
        self.pwm_left_forward.ChangeDutyCycle(speed)
        self.pwm_right_forward.ChangeDutyCycle(0)
        self.pwm_left_backward.ChangeDutyCycle(0)
        self.pwm_right_backward.ChangeDutyCycle(speed)
    
    def move_backward(self):
        """后退"""
        self.pwm_left_forward.ChangeDutyCycle(0)
        self.pwm_right_forward.ChangeDutyCycle(0)
        self.pwm_left_backward.ChangeDutyCycle(50)
        self.pwm_right_backward.ChangeDutyCycle(50)
    
    def stop(self):
        """停止所有电机"""
        for pwm in [self.pwm_left_forward, self.pwm_left_backward,
                   self.pwm_right_forward, self.pwm_right_backward]:
            pwm.ChangeDutyCycle(0)
    
    def cleanup(self):
        """清理GPIO设置"""
        self.stop()
        GPIO.cleanup() 