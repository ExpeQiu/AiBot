import speech_recognition as sr
import pyttsx3
from config.config import (
    MICROPHONE_INDEX, 
    WAKE_WORD, 
    LANGUAGE, 
    VOICE_COMMANDS,
    SPEECH_RATE,
    SPEECH_VOLUME,
    VOICE_RESPONSES,
    WEATHER_API
)
import threading
import queue
from modules.utils.logger import Logger
import random
import asyncio

class SpeechRecognizer:
    def __init__(self):
        self.logger = Logger.get_logger("SpeechRecognizer")
        self.logger.info("Initializing speech recognizer")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=MICROPHONE_INDEX)
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', SPEECH_RATE)
        self.engine.setProperty('volume', SPEECH_VOLUME/100)
        
        # 命令队列
        self.command_queue = queue.Queue()
        
        # 调整麦克风噪声阈值
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        # 启动语音识别线程
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.chat_assistant = None  # 将在main中设置
    
    def set_chat_assistant(self, assistant):
        """设置聊天助手"""
        self.chat_assistant = assistant
    
    async def _process_chat_input(self, text):
        """处理聊天输入"""
        if "天气" in text:
            # 提取城市名（这里需要更复杂的NLP处理）
            city = WEATHER_API['default_city']
            response = await self.chat_assistant.query_weather(city)
        elif "新闻" in text:
            response = await self.chat_assistant.query_news()
        else:
            response = await self.chat_assistant.chat(text)
            
        self.speak(response)
    
    def _handle_command(self, command):
        """处理语音命令"""
        if command == "set_reminder":
            self._handle_reminder_setup()
            return None
        elif command == "list_reminders":
            self._list_reminders()
            return None
        elif command == "delete_reminder":
            self._handle_reminder_deletion()
            return None
            
        if command in ['greeting', 'goodbye']:
            response = random.choice(VOICE_RESPONSES[command])
            self.speak(response)
            return None
            
        if command in VOICE_COMMANDS.values():
            self.speak(VOICE_RESPONSES['command_accepted'].format(command))
            return command
            
        self.speak(VOICE_RESPONSES['command_rejected'])
        return None
    
    def _handle_reminder_setup(self):
        """处理提醒设置"""
        self.speak("请说出提醒类型，可以是吃药提醒、会议提醒或其他提醒")
        reminder_type = self._get_user_input()
        
        self.speak("请说出提醒标题")
        title = self._get_user_input()
        
        self.speak("请说出提醒时间，格式为年月日时分")
        time_str = self._get_user_input()
        
        self.speak("是否需要添加描述？请说是或否")
        if self._get_user_input().lower() == "是":
            self.speak("请说出描述内容")
            description = self._get_user_input()
        else:
            description = None
        
        self.speak("是否需要重复提醒？请说是或否")
        if self._get_user_input().lower() == "是":
            self.speak("请说出重复间隔，单位为小时")
            repeat_interval = int(self._get_user_input()) * 3600
        else:
            repeat_interval = None
        
        if self.reminder_manager.add_reminder(
            reminder_type, title, time_str, description, repeat_interval
        ):
            self.speak("提醒设置成功")
        else:
            self.speak("提醒设置失败，请重试")
    
    def _list_reminders(self):
        """列出所有提醒"""
        reminders = self.reminder_manager.list_reminders()
        if not reminders:
            self.speak("当前没有设置的提醒")
            return
            
        self.speak("以下是您的提醒事项：")
        for reminder in reminders:
            _, r_type, title, desc, time, _ = reminder
            message = f"{title}，时间是{time.strftime('%Y年%m月%d日%H时%M分')}"
            if desc:
                message += f"，{desc}"
            self.speak(message)
    
    def _handle_reminder_deletion(self):
        """处理提醒删除"""
        reminders = self.reminder_manager.list_reminders()
        if not reminders:
            self.speak("当前没有设置的提醒")
            return
            
        self.speak("请说出要删除的提醒的标题")
        title = self._get_user_input()
        
        # 查找匹配的提醒
        matching_reminders = [r for r in reminders if r[2].lower() == title.lower()]
        
        if not matching_reminders:
            self.speak("未找到匹配的提醒")
            return
            
        if len(matching_reminders) > 1:
            self.speak("找到多个匹配的提醒，请更具体地描述")
            return
            
        if self.reminder_manager.delete_reminder(matching_reminders[0][0]):
            self.speak("提醒删除成功")
        else:
            self.speak("提醒删除失败，请重试")
    
    def _get_user_input(self):
        """获取用户语音输入"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language=LANGUAGE)
                return text
        except Exception as e:
            self.logger.error(f"Error getting user input: {str(e)}")
            return None
    
    def _listen_loop(self):
        """持续监听语音命令的循环"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio, language=LANGUAGE)
                    self.logger.debug(f"Recognized speech: {text}")
                    
                    if self.chat_assistant and self.chat_assistant.is_chat_mode():
                        if "退出聊天" in text:
                            self.chat_assistant.exit_chat_mode()
                        else:
                            asyncio.run(self._process_chat_input(text))
                    elif WAKE_WORD in text:
                        command = text.replace(WAKE_WORD, "").strip()
                        
                        if command in VOICE_COMMANDS:
                            command_type = VOICE_COMMANDS[command]
                            if command_type == "chat_mode":
                                self.chat_assistant.enter_chat_mode()
                            else:
                                result = self._handle_command(command_type)
                                if result:
                                    self.command_queue.put(result)
                            
                except sr.UnknownValueError:
                    self.logger.debug("Could not understand audio")
                except sr.RequestError as e:
                    self.logger.error(f"Speech service error: {str(e)}")
                    self.speak(VOICE_RESPONSES['error'])
                    
            except Exception as e:
                self.logger.error(f"Error in listen loop: {str(e)}")
                continue
    
    def get_command(self):
        """获取最新的语音命令"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def speak(self, text):
        """文本转语音输出"""
        # 设置语音参数
        self.engine.setProperty('rate', SPEECH_RATE)     # 语速
        self.engine.setProperty('volume', SPEECH_VOLUME) # 音量
        self.engine.setProperty('voice', VOICE_ID)       # 声音类型
        
        # 执行语音合成
        self.engine.say(text)
        self.engine.runAndWait()
    
    def cleanup(self):
        """清理资源"""
        self.is_listening = False
        self.listen_thread.join() 

    def listen(self):
        with sr.Microphone() as source:
            print("听取命令中...")
            audio = self.recognizer.listen(source)
            try:
                # 可以选择不同的识别引擎:
                # 1. Google Speech Recognition (默认)
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                
                # 2. 百度语音识别
                # text = self.recognizer.recognize_baidu(audio, api_key, secret_key)
                
                # 3. 科大讯飞
                # text = self.recognizer.recognize_xfyun(audio, api_id, api_key)
                
                return text
            except sr.UnknownValueError:
                return None

    async def process_command(self, command):
        """处理语音命令"""
        # 1. 基础指令处理
        if command in VOICE_COMMANDS:
            return VOICE_COMMANDS[command]
            
        # 2. AI对话处理
        elif self.chat_assistant:
            response = await self.chat_assistant.chat(command)
            self.speak(response)
            
        # 3. 特殊查询处理
        elif "天气" in command:
            city = self._extract_city(command)
            weather = await self.chat_assistant.query_weather(city)
            self.speak(weather)