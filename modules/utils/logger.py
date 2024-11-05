import logging
import os
from logging.handlers import RotatingFileHandler
from config.config import LOG_DIR, LOG_FILE, LOG_FORMAT, LOG_LEVEL, LOG_BACKUP_COUNT, LOG_MAX_BYTES

class Logger:
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name):
        if name in cls._loggers:
            return cls._loggers[name]
            
        # 创建日志目录
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # 创建logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger 