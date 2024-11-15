import sys
from scripts.model_manager import ModelManager
from modules.utils.logger import Logger

# 在初始化时检查模型
def check_models():
    model_manager = ModelManager()
    missing_models = model_manager.verify_models()
    
    if missing_models:
        logger.error(f"Missing required models: {', '.join(missing_models)}")
        logger.info("Please run 'python scripts/download_models.py' to download missing models")
        sys.exit(1)

async def main():
    logger = Logger.get_logger("Main")
    logger.info("Starting robot control system")
    
    try:
        # 检查模型文件
        check_models()
        
        # 初始化组件
        ...


t = threading.Thread(target=Video_display)
t.setDaemon(True)
t.start()