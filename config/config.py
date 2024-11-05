# 相机配置 - 可根据实际摄像头调整
CAMERA_WIDTH = 640      # 摄像头分辨率宽度
CAMERA_HEIGHT = 480     # 摄像头分辨率高度
CAMERA_FPS = 30         # 摄像头帧率

# 人脸识别配置 - 可根据识别效果调整
FACE_DETECTION_CONFIDENCE = 0.5  # 人脸检测置信度阈值
FACE_RECOGNITION_THRESHOLD = 0.6 # 人脸识别匹配阈值

# PID控制参数 - 需要根据小车实际运动效果调整
PID_KP = 0.8   # 比例系数:控制响应速度
PID_KI = 0.05  # 积分系数:消除稳态误差
PID_KD = 0.3   # 微分系数:抑制震荡

# GPIO引脚配置 - 【重要】需要根据实际硬件连接修改
MOTOR_LEFT_FORWARD = 17    # 左电机前进引脚
MOTOR_LEFT_BACKWARD = 18   # 左电机后退引脚
MOTOR_RIGHT_FORWARD = 22   # 右电机前进引脚
MOTOR_RIGHT_BACKWARD = 23  # 右电机后退引脚

# 超声波传感器引脚配置 - 【重要】需要根据实际连接修改
ULTRASONIC_SENSORS = {
    'front': {
        'trigger': 27,     # 前方传感器触发引脚
        'echo': 24,        # 前方传感器回响引脚
        'angle': 0         # 安装角度
    },
    'left': {
        'trigger': 25,
        'echo': 8,
        'angle': -45
    },
    'right': {
        'trigger': 23,
        'echo': 7,
        'angle': 45
    }
}

# 避障配置 - 可根据实际情况调整
SAFE_DISTANCE = 40      # 安全距离(厘米)
DANGER_DISTANCE = 20    # 危险距离(厘米)
TURN_THRESHOLD = 30     # 转向判断阈值(厘米)

# 语音识别配置 - 【重要】需要根据实际设备配置
MICROPHONE_INDEX = 0    # 麦克风设备索引
WAKE_WORD = "小车"      # 唤醒词
LANGUAGE = "zh-CN"      # 语音识别语言

# OpenAI配置 - 【重要】需要配置自己的API密钥
OPENAI_CONFIG = {
    'api_key': 'your_api_key_here',  # OpenAI API密钥
    'model': 'gpt-3.5-turbo',        # 使用的模型
    'temperature': 0.7,
    'max_tokens': 150
}

# 天气API配置 - 【重要】需要配置自己的API密钥
WEATHER_API = {
    'key': 'your_weather_api_key',
    'base_url': 'http://api.weatherapi.com/v1',
    'default_city': '北京'
}

# 新闻API配置 - 【重要】需要配置自己的API密钥
NEWS_API = {
    'key': 'your_news_api_key',
    'base_url': 'https://newsapi.org/v2',
    'country': 'cn',
    'language': 'zh'
}

# 日志配置 - 可根据需要调整
LOG_DIR = "logs"                    # 日志目录
LOG_FILE = os.path.join(LOG_DIR, "robot.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_BACKUP_COUNT = 5                # 保留的日志文件数量
LOG_MAX_BYTES = 5 * 1024 * 1024    # 每个日志文件最大大小(5MB)

# 运动控制参数 - 需要根据电机特性调整
BASE_SPEED = 50        # 基础速度
MAX_SPEED = 100        # 最大速度
MIN_SPEED = 20         # 最小速度
TURN_SPEED = 40        # 转向速度