import psutil
import time
import threading
from datetime import datetime
from config.config import SYSTEM_STATUS, VOICE_RESPONSES
from modules.utils.logger import Logger

class SystemMonitor:
    def __init__(self, speech_recognizer):
        self.logger = Logger.get_logger("SystemMonitor")
        self.speech_recognizer = speech_recognizer
        self.running = True
        self.recording = False
        self.camera_active = True
        self.base_speed = BASE_SPEED
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("System monitor initialized")
    
    def _monitor_loop(self):
        """持续监控系统状态"""
        last_check = 0
        while self.running:
            current_time = time.time()
            if current_time - last_check >= SYSTEM_STATUS['status_interval']:
                self._check_system_status()
                last_check = current_time
            time.sleep(1)
    
    def _check_system_status(self):
        """检查系统状态"""
        try:
            # 获取系统信息
            cpu_temp = self._get_cpu_temperature()
            battery = self._get_battery_status()
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            status_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_temperature': cpu_temp,
                'battery_level': battery,
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'camera_active': self.camera_active,
                'recording': self.recording,
                'base_speed': self.base_speed
            }
            
            self.logger.info(f"System status: {status_data}")
            
            # 检查警告条件
            self._check_warnings(status_data)
            
            return status_data
            
        except Exception as e:
            self.logger.error(f"Error checking system status: {str(e)}")
            return None
    
    def _get_cpu_temperature(self):
        """获取CPU温度"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
            return temp
        except:
            return None
    
    def _get_battery_status(self):
        """获取电池状态"""
        try:
            # 这里需要根据实际硬件实现电池状态检测
            # 临时返回模拟值
            return 75
        except:
            return None
    
    def _check_warnings(self, status):
        """检查是否需要发出警告"""
        if status['battery_level'] is not None and \
           status['battery_level'] < SYSTEM_STATUS['battery_warning']:
            self.speech_recognizer.speak(VOICE_RESPONSES['battery_low'])
            
        if status['cpu_temperature'] is not None and \
           status['cpu_temperature'] > SYSTEM_STATUS['temp_warning']:
            self.speech_recognizer.speak(VOICE_RESPONSES['temp_high'])
    
    def get_status_report(self):
        """获取状态报告"""
        status = self._check_system_status()
        if status:
            report = (
                f"系统状态报告：\n"
                f"电池电量：{status['battery_level']}%\n"
                f"CPU温度：{status['cpu_temperature']}°C\n"
                f"CPU使用率：{status['cpu_usage']}%\n"
                f"内存使用率：{status['memory_usage']}%"
            )
            return report
        return VOICE_RESPONSES['error']
    
    def adjust_speed(self, increase=True):
        """调整基础速度"""
        if increase:
            self.base_speed = min(MAX_SPEED, self.base_speed + 10)
        else:
            self.base_speed = max(MIN_SPEED, self.base_speed - 10)
        return f"当前速度已调整为{self.base_speed}"
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        self.monitor_thread.join() 