import openai
import aiohttp
import asyncio
from datetime import datetime
from config.config import OPENAI_CONFIG, WEATHER_API, NEWS_API, CHAT_CONFIG
from modules.utils.logger import Logger

class ChatAssistant:
    def __init__(self, speech_recognizer):
        self.logger = Logger.get_logger("ChatAssistant")
        self.speech = speech_recognizer
        openai.api_key = OPENAI_CONFIG['api_key']
        self.chat_history = []
        self.chat_mode = False
        
    async def chat(self, user_input):
        """处理用户输入并生成回复"""
        try:
            # 准备对话上下文
            messages = [{"role": "system", "content": CHAT_CONFIG['default_context']}]
            
            # 添加对话历史
            for msg in self.chat_history[-CHAT_CONFIG['max_history']:]:
                messages.append(msg)
            
            # 添加用户输入
            messages.append({"role": "user", "content": user_input})
            
            # 调用OpenAI API
            response = await asyncio.wait_for(
                openai.ChatCompletion.acreate(
                    model=OPENAI_CONFIG['model'],
                    messages=messages,
                    temperature=OPENAI_CONFIG['temperature'],
                    max_tokens=OPENAI_CONFIG['max_tokens']
                ),
                timeout=CHAT_CONFIG['timeout']
            )
            
            reply = response.choices[0].message.content
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": reply})
            
            return reply
            
        except Exception as e:
            self.logger.error(f"Chat error: {str(e)}")
            return "抱歉，我遇到了一些问题，请稍后再试。"
    
    async def query_weather(self, city=None):
        """查询天气信息"""
        city = city or WEATHER_API['default_city']
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': WEATHER_API['key'],
                    'q': city,
                    'lang': 'zh'
                }
                async with session.get(f"{WEATHER_API['base_url']}/current.json", 
                                     params=params) as response:
                    data = await response.json()
                    
                    weather_info = (
                        f"{city}天气：\n"
                        f"温度：{data['current']['temp_c']}°C\n"
                        f"天气：{data['current']['condition']['text']}\n"
                        f"湿度：{data['current']['humidity']}%\n"
                        f"风速：{data['current']['wind_kph']}km/h"
                    )
                    return weather_info
                    
        except Exception as e:
            self.logger.error(f"Weather query error: {str(e)}")
            return "抱歉，天气查询失败。"
    
    async def query_news(self, category='general'):
        """查询新闻信息"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'apiKey': NEWS_API['key'],
                    'country': NEWS_API['country'],
                    'category': category,
                    'pageSize': 5
                }
                async with session.get(f"{NEWS_API['base_url']}/top-headlines",
                                     params=params) as response:
                    data = await response.json()
                    
                    news_list = []
                    for article in data['articles'][:3]:
                        news_list.append(f"标题：{article['title']}\n"
                                       f"来���：{article['source']['name']}")
                    
                    return "\n\n".join(news_list)
                    
        except Exception as e:
            self.logger.error(f"News query error: {str(e)}")
            return "抱歉，新闻查询失败。"
    
    def enter_chat_mode(self):
        """进入聊天模式"""
        self.chat_mode = True
        self.speech.speak("已进入聊天模式，你可以和我对话了")
    
    def exit_chat_mode(self):
        """退出聊天模式"""
        self.chat_mode = False
        self.speech.speak("已退出聊天模式")
    
    def is_chat_mode(self):
        """返回当前是否在聊天模式"""
        return self.chat_mode 