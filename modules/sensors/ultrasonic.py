import RPi.GPIO as GPIO
import time
import math
from config.config import ULTRASONIC_SENSORS, SAFE_DISTANCE, DANGER_DISTANCE, TURN_THRESHOLD
from modules.utils.logger import Logger

class MultiUltrasonicSensor:
    def __init__(self):
        self.logger = Logger.get_logger("MultiUltrasonicSensor")
        self.sensors = {}
        
        # 初始化所有传感器
        for position, config in ULTRASONIC_SENSORS.items():
            GPIO.setup(config['trigger'], GPIO.OUT)
            GPIO.setup(config['echo'], GPIO.IN)
            GPIO.output(config['trigger'], False)
            self.sensors[position] = config
            
        time.sleep(0.5)  # 等待传感器稳定
        self.logger.info("Initialized multiple ultrasonic sensors")
        
    def get_distance(self, position):
        """获取指定位置传感器的距离测量值"""
        sensor = self.sensors[position]
        
        # 发送触发脉冲
        GPIO.output(sensor['trigger'], True)
        time.sleep(0.00001)
        GPIO.output(sensor['trigger'], False)
        
        start_time = time.time()
        timeout = start_time + 0.1
        
        # 等待回响
        while GPIO.input(sensor['echo']) == 0:
            if time.time() > timeout:
                return None
            pulse_start = time.time()
            
        while GPIO.input(sensor['echo']) == 1:
            if time.time() > timeout:
                return None
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        
        return round(distance, 2)
    
    def get_all_distances(self):
        """获取所有传感器的距离测量值"""
        distances = {}
        for position in self.sensors.keys():
            distances[position] = self.get_distance(position)
            time.sleep(0.05)  # 避免传感器之间的干扰
        return distances
    
    def analyze_surroundings(self):
        """分析周围环境并提供避障建议"""
        distances = self.get_all_distances()
        self.logger.debug(f"Sensor readings: {distances}")
        
        # 检查是否有任何传感器检测到危险距离
        danger = any(d is not None and d <= DANGER_DISTANCE for d in distances.values())
        if danger:
            self.logger.warning("Danger distance detected!")
            return 'backward'
            
        front_dist = distances.get('front')
        left_dist = distances.get('left')
        right_dist = distances.get('right')
        
        # 如果前方安全距离内有障碍物，决定转向方向
        if front_dist and front_dist <= SAFE_DISTANCE:
            if left_dist and right_dist:
                # 选择距离更大的方向转向
                if left_dist > right_dist:
                    return 'turn_left'
                else:
                    return 'turn_right'
            elif left_dist:
                return 'turn_left'
            elif right_dist:
                return 'turn_right'
            else:
                return 'backward'
                
        return 'forward'
    
    def get_optimal_speed(self, base_speed, distances):
        """根据障碍物距离调整速度"""
        if not distances.get('front'):
            return base_speed
            
        front_dist = distances['front']
        if front_dist > SAFE_DISTANCE:
            return base_speed
        elif front_dist > DANGER_DISTANCE:
            # 在安全距离和危险距离之间，线性降低速度
            speed_range = base_speed - MIN_SPEED
            dist_range = SAFE_DISTANCE - DANGER_DISTANCE
            speed_reduction = speed_range * (1 - (front_dist - DANGER_DISTANCE) / dist_range)
            return max(MIN_SPEED, base_speed - speed_reduction)
        else:
            return 0