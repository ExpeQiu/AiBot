from modules.utils.camera import Camera
from modules.face_recognition.face_detector import FaceDetector
from modules.motion_control.pid_controller import PIDController
from modules.motion_control.motor_controller import MotorController
from modules.sensors.ultrasonic import MultiUltrasonicSensor
from modules.voice.speech_recognizer import SpeechRecognizer
from modules.utils.logger import Logger
from modules.ai.chat_assistant import ChatAssistant
from modules.behavior.behavior_detector import BehaviorDetector
from modules.assistant.reminder_manager import ReminderManager
import cv2
import time
import asyncio

async def main():
    logger = Logger.get_logger("Main")
    logger.info("Starting robot control system")
    
    try:
        # 初始化各个组件
        camera = Camera()                    # 初始化摄像头
        face_detector = FaceDetector()       # 初始化人脸检测器
        pid_controller = PIDController()     # 初始化PID控制器
        motor_controller = MotorController() # 初始化电机控制器
        ultrasonic = MultiUltrasonicSensor() # 初始化超声波传感器
        speech_recognizer = SpeechRecognizer() # 初始化语音识别器
        
        # 初始化AI助手 - 确保已配置OpenAI API密钥
        chat_assistant = ChatAssistant(speech_recognizer)
        speech_recognizer.set_chat_assistant(chat_assistant)
        
        # 初始化行为检测器 - 确保模型文件存在
        behavior_detector = BehaviorDetector(speech_recognizer)
        
        # 初始化提醒管理器 - 确保数据库目录可写
        reminder_manager = ReminderManager(speech_recognizer)
        speech_recognizer.reminder_manager = reminder_manager
        
        follow_mode = True  # 默认启动跟随模式
        logger.info("System initialized successfully")
        
        while True:
            # 主循环逻辑
            ...

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        # 清理资源
        camera.release()
        motor_controller.cleanup()
        reminder_manager.cleanup()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    asyncio.run(main()) 