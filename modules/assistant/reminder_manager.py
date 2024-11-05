import sqlite3
import datetime
import threading
import time
import random
from config.config import REMINDER_CONFIG, REMINDER_TYPES
from modules.utils.logger import Logger

class ReminderManager:
    def __init__(self, speech_recognizer):
        self.logger = Logger.get_logger("ReminderManager")
        self.speech = speech_recognizer
        self.running = True
        
        # 初始化数据库
        self._init_database()
        
        # 启动提醒检查线程
        self.check_thread = threading.Thread(target=self._check_reminders_loop)
        self.check_thread.daemon = True
        self.check_thread.start()
        
        self.logger.info("Reminder manager initialized")
    
    def _init_database(self):
        """初始化提醒数据库"""
        try:
            self.conn = sqlite3.connect(REMINDER_CONFIG['database_file'])
            self.cursor = self.conn.cursor()
            
            # 创建提醒表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    time TIMESTAMP NOT NULL,
                    repeat_interval INTEGER,
                    last_reminded TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def add_reminder(self, reminder_type, title, time_str, description=None, repeat_interval=None):
        """添加新的提醒"""
        try:
            # 解析时间字符串
            reminder_time = self._parse_time(time_str)
            
            # 如果没有指定重复间隔，使用默认值
            if repeat_interval is None and reminder_type in REMINDER_TYPES:
                repeat_interval = REMINDER_TYPES[reminder_type].get('default_interval')
            
            # 检查是否超过最大提醒数量
            self.cursor.execute("SELECT COUNT(*) FROM reminders WHERE active = 1")
            if self.cursor.fetchone()[0] >= REMINDER_CONFIG['max_reminders']:
                raise Exception("已达到最大提醒数量限制")
            
            # 插入新提醒
            self.cursor.execute('''
                INSERT INTO reminders (type, title, description, time, repeat_interval)
                VALUES (?, ?, ?, ?, ?)
            ''', (reminder_type, title, description, reminder_time, repeat_interval))
            
            self.conn.commit()
            self.logger.info(f"Added new reminder: {title}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding reminder: {str(e)}")
            return False
    
    def list_reminders(self):
        """获取所有活动的提醒"""
        try:
            self.cursor.execute('''
                SELECT id, type, title, description, time, repeat_interval
                FROM reminders
                WHERE active = 1
                ORDER BY time
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error listing reminders: {str(e)}")
            return []
    
    def delete_reminder(self, reminder_id):
        """删除提醒"""
        try:
            self.cursor.execute('''
                UPDATE reminders
                SET active = 0
                WHERE id = ?
            ''', (reminder_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting reminder: {str(e)}")
            return False
    
    def _check_reminders_loop(self):
        """检查提醒的循环"""
        while self.running:
            try:
                current_time = datetime.datetime.now()
                
                # 查询需要提醒的事项
                self.cursor.execute('''
                    SELECT id, type, title, description, time, repeat_interval
                    FROM reminders
                    WHERE active = 1
                    AND time <= ?
                    AND (last_reminded IS NULL OR 
                         DATETIME(last_reminded, '+' || ? || ' seconds') <= ?)
                ''', (current_time, REMINDER_CONFIG['check_interval'], current_time))
                
                for reminder in self.cursor.fetchall():
                    self._trigger_reminder(reminder)
                    
                # 更新重复性提醒
                self._update_repeat_reminders()
                
            except Exception as e:
                self.logger.error(f"Error in reminder check loop: {str(e)}")
                
            time.sleep(REMINDER_CONFIG['check_interval'])
    
    def _trigger_reminder(self, reminder):
        """触发提醒"""
        reminder_id, r_type, title, description, r_time, repeat = reminder
        
        # 获取提醒消息
        messages = REMINDER_TYPES.get(r_type, REMINDER_TYPES['general'])['messages']
        message = random.choice(messages)
        
        # 组合完整提醒消息
        full_message = f"{message}：{title}"
        if description:
            full_message += f"，{description}"
        
        # 语音提醒
        self.speech.speak(full_message)
        
        # 更新最后提醒时间
        self.cursor.execute('''
            UPDATE reminders
            SET last_reminded = ?
            WHERE id = ?
        ''', (datetime.datetime.now(), reminder_id))
        self.conn.commit()
        
        self.logger.info(f"Triggered reminder: {title}")
    
    def _update_repeat_reminders(self):
        """更新重复性提醒的下次提醒时间"""
        self.cursor.execute('''
            UPDATE reminders
            SET time = DATETIME(time, '+' || repeat_interval || ' seconds')
            WHERE active = 1
            AND repeat_interval IS NOT NULL
            AND time <= DATETIME('now')
        ''')
        self.conn.commit()
    
    def _parse_time(self, time_str):
        """解析时间字符串"""
        try:
            # 这里可以添加更复杂的时间解析逻辑
            # 当前仅支持简单的datetime格式
            return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            raise ValueError(f"Invalid time format: {time_str}")
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        self.check_thread.join()
        self.conn.close() 