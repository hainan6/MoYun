"""
网络服务模块
==========

本模块负责处理邮件服务和第三方API集成。

主要功能:
    - 邮件发送服务
    - 验证码邮件模板
    - 天气API集成
    - AI模型API集成
    - 豆瓣图书API集成

依赖:
    - smtplib: SMTP客户端
    - requests: HTTP客户端
    - beautifulsoup4: HTML解析
    - dashscope: 通义千问API（可选）
"""

import re
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPException
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from requests import get as http_get, RequestException

from core.config.settings import config_manager

try:
    from dashscope import Generation
    from dashscope.api_entities.dashscope_response import Message
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class EmailServiceError(Exception):
    """邮件服务相关的自定义异常"""
    pass


class APIServiceError(Exception):
    """API服务相关的自定义异常"""
    pass


class EmailService:
    """
    现代化的邮件服务，提供改进的错误处理和模板功能
    
    主要职责:
        1. 发送验证码邮件
        2. 管理邮件模板
        3. 处理SMTP连接
        4. 错误处理和日志
        
    设计特点:
        - 模板化：使用HTML模板美化邮件
        - 安全性：使用SSL加密连接
        - 错误处理：详细的异常信息
    """
    
    def __init__(self):
        """
        初始化邮件服务
        
        初始化步骤:
            1. 加载邮件配置
            2. 设置SMTP参数
            3. 加载邮件模板
            
        异常:
            EmailServiceError: 当初始化失败时
        """
        try:
            email_config = config_manager.get_email_config()
            self._smtp_host = email_config['Host']
            self._smtp_port = email_config['Port']
            self._username = email_config['Username']
            self._password = email_config['Password']
            self._sender_address = email_config['Sender']
        except Exception as e:
            raise EmailServiceError(f"邮件服务初始化失败: {e}")
        
        self._verification_template = self._get_verification_template()
    
    def _get_verification_template(self) -> str:
        """
        获取验证码邮件模板
        
        返回:
            HTML格式的邮件模板字符串
            
        说明:
            模板包含以下部分:
            - 平台标题和Logo
            - 验证码显示区域
            - 重要提醒信息
            - 页脚版权信息
        """
        return """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 15px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">墨韵读书平台</h1>
                <p style="margin: 10px 0 0; opacity: 0.9;">MoYun Reading Platform</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; margin: 20px 0;">
                <h2 style="color: #333; margin-top: 0;">密码重置验证</h2>
                <p style="color: #666; line-height: 1.6;">
                    尊敬的用户，您好！<br><br>
                    您正在申请重置密码，为了确保您的账户安全，请使用以下验证码完成验证：
                </p>
                
                <div style="background: #667eea; color: white; padding: 20px; 
                           border-radius: 10px; text-align: center; margin: 25px 0;">
                    <h1 style="margin: 0; font-size: 32px; letter-spacing: 3px;">{}</h1>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; 
                           padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p style="margin: 0; color: #856404;">
                        <strong>重要提醒：</strong><br>
                        • 验证码10分钟内有效，请及时使用<br>
                        • 如非本人操作，请忽略此邮件<br>
                        • 请勿将验证码告知他人
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 14px;">
                <p>此邮件由系统自动发送，请勿回复</p>
                <p style="margin: 5px 0 0;">© 2024 墨韵读书平台 版权所有</p>
            </div>
        </div>
        """
    
    def send_verification_code(self, recipient_email: str, verification_code: str) -> bool:
        """
        发送验证码邮件
        
        参数:
            recipient_email: 接收者邮箱地址
            verification_code: 要发送的验证码
            
        返回:
            发送成功返回True，否则返回False
            
        异常:
            EmailServiceError: 当邮件配置无效时
            
        说明:
            1. 自动将数字验证码转换为字符串
            2. 使用HTML模板格式化邮件内容
            3. 设置UTF-8编码确保中文正常显示
        """
        try:
            # 确保验证码为字符串类型
            if isinstance(verification_code, int):
                verification_code = str(verification_code)
            
            # 格式化邮件内容
            email_content = self._verification_template.format(verification_code)
            
            # 创建邮件对象
            message = MIMEText(email_content, 'html', 'utf-8')
            message['Subject'] = "墨韵读书平台 - 密码重置验证码"
            message['From'] = self._sender_address
            message['To'] = recipient_email
            
            return self._send_email(recipient_email, message)
            
        except Exception as e:
            raise EmailServiceError(f"验证码发送失败: {e}")
    
    def _send_email(self, recipient: str, message: MIMEText) -> bool:
        """
        通过SMTP发送邮件
        
        参数:
            recipient: 接收者邮箱地址
            message: 邮件对象
            
        返回:
            发送成功返回True，否则返回False
            
        说明:
            1. 使用SSL加密连接
            2. 自动处理连接关闭
            3. 生产环境禁用调试输出
        """
        try:
            with SMTP_SSL(self._smtp_host, self._smtp_port) as smtp_server:
                smtp_server.set_debuglevel(0)  # 生产环境禁用调试
                smtp_server.login(self._username, self._password)
                smtp_server.sendmail(self._sender_address, [recipient], message.as_string())
            return True
            
        except SMTPException as e:
            print(f"SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"邮件发送错误: {e}")
            return False


class ExternalAPIService:
    """
    外部API服务，用于第三方集成
    
    主要职责:
        1. 天气信息获取
        2. AI模型调用
        3. 豆瓣图书信息获取
        
    支持的API:
        - 易客天气API
        - 通义千问API
        - 豆瓣图书API
    """
    
    # AI模型配置
    AI_MODELS = {
        "qwen-turbo": "qwen-turbo",           # 通义千问-涡轮版
        "qwen-plus": "qwen-plus",             # 通义千问-加强版
        "qwen-max": "qwen-max",               # 通义千问-最强版
        "qwen-max-1201": "qwen-max-1201",     # 通义千问-最强版(12.01)
        "qwen-max-longcontext": "qwen-max-longcontext"  # 通义千问-长文本版
    }
    
    def __init__(self):
        """
        初始化外部API服务
        
        初始化步骤:
            1. 设置HTTP请求头
            2. 加载API配置
            3. 检查可选依赖
        """
        self._user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'
        )
        
        # 加载API配置
        try:
            self._weather_config = config_manager.get_api_config('Yiketianqi')
            if DASHSCOPE_AVAILABLE:
                self._ai_config = config_manager.get_api_config('Qwen')
        except Exception as e:
            print(f"警告: 部分API配置不可用: {e}")
    
    def get_weather_by_ip(self, client_ip: str) -> Dict[str, Any]:
        """
        根据客户端IP获取天气信息
        
        参数:
            client_ip: 客户端IP地址
            
        返回:
            包含天气信息的字典
            
        异常:
            APIServiceError: 当天气API请求失败时
            
        说明:
            使用易客天气API获取:
            - 实时天气
            - 温度范围
            - 天气描述
            - 空气质量
        """
        try:
            response = http_get(
                "https://v1.yiketianqi.com/api",
                params={
                    "unescape": 1,
                    "ip": client_ip,
                    "version": self._weather_config.get("version"),
                    "appid": self._weather_config.get("appid"),
                    "appsecret": self._weather_config.get("appsecret")
                },
                timeout=10
            )
            
            response.raise_for_status()
            weather_data = response.json()
            
            return {
                'city': weather_data.get('city', 'Unknown'),
                'weather': weather_data.get('wea', 'Unknown'),
                'temperature': weather_data.get('tem', '0'),
                'temperature_range': (
                    weather_data.get('tem2', '0'), 
                    weather_data.get('tem1', '0')
                ),
                'wind': f"{weather_data.get('win', '')}{weather_data.get('win_speed', '')}"
            }
            
        except RequestException as e:
            raise APIServiceError(f"Weather API request failed: {e}")
        except Exception as e:
            raise APIServiceError(f"Weather data processing failed: {e}")
    
    def get_book_info_from_douban(self, douban_book_id: int) -> Dict[str, Any]:
        """
        Scrape book information from Douban (for reference, may not be actively used)
        
        Args:
            douban_book_id: Douban book ID
            
        Returns:
            Book information dictionary
            
        Raises:
            APIServiceError: If scraping fails
        """
        try:
            book_id_str = str(douban_book_id)
            response = http_get(
                f"https://book.douban.com/subject/{book_id_str}",
                headers={"User-Agent": self._user_agent},
                timeout=15
            )
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract book information
            title_element = soup.find('span', attrs={'property': 'v:itemreviewed'})
            title = title_element.text if title_element else 'Unknown'
            
            score_element = soup.find('strong', attrs={'class': 'll rating_num'})
            score = score_element.text.strip() if score_element else '0.0'
            
            # Extract metadata
            metadata = self._extract_book_metadata(soup)
            
            # Extract description
            description = self._extract_book_description(soup)
            
            return {
                'isbn': metadata.get('ISBN'),
                'title': title,
                'original_title': metadata.get('原作名'),
                'author': metadata.get('作者'),
                'pages': metadata.get('页数'),
                'publish_date': metadata.get('出版年'),
                'publisher': metadata.get('出版社'),
                'description': description,
                'douban_score': score,
                'douban_id': book_id_str
            }
            
        except Exception as e:
            raise APIServiceError(f"Douban book info extraction failed: {e}")
    
    def _extract_book_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract book metadata from Douban page"""
        metadata = {}
        info_div = soup.find('div', id='info')
        
        if info_div:
            info_text = info_div.text.split('\n')
            info_lines = [line.strip() for line in info_text if line.strip()]
            
            i = 0
            while i < len(info_lines):
                line = info_lines[i]
                
                if line.endswith(':'):
                    # Single key on its own line
                    key = line[:-1]
                    value = ""
                    j = i + 1
                    
                    while j < len(info_lines) and not re.match(r'.+:', info_lines[j]):
                        value += info_lines[j]
                        j += 1
                    
                    metadata[key] = value
                    i = j
                    
                elif ':' in line:
                    # Key:value format
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
                    i += 1
                else:
                    i += 1
        
        return metadata
    
    def _extract_book_description(self, soup: BeautifulSoup) -> str:
        """Extract book description from Douban page"""
        intro_element = soup.find('span', attrs={'class': 'all hidden'})
        
        if intro_element:
            paragraphs = intro_element.find_all('p')
            description_lines = [p.text.strip() for p in paragraphs]
            return '\n'.join(description_lines)
        
        return ""
    
    def get_ai_suggestion(
        self, 
        conversation: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Get AI-generated suggestions using Qwen model
        
        Args:
            conversation: List of conversation messages
            system_prompt: Optional system prompt to guide AI
            
        Returns:
            AI-generated response text or None if service unavailable
            
        Raises:
            APIServiceError: If AI API request fails
        """
        if not DASHSCOPE_AVAILABLE:
            raise APIServiceError("DashScope library not available")
        
        try:
            # Add system prompt if provided
            messages = conversation.copy()
            if system_prompt:
                messages.insert(0, {'role': 'system', 'content': system_prompt})
            
            # Get model configuration
            model_name = self._ai_config.get('model', 'qwen-turbo')
            if model_name in self.AI_MODELS:
                model = self.AI_MODELS[model_name]
            else:
                model = Generation.Models.qwen_turbo
            
            # Make API request
            response = Generation.call(
                model,
                api_key=self._ai_config.get('api_key'),
                messages=[Message(**msg) for msg in messages],
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise APIServiceError(f"AI API returned status code: {response.status_code}")
                
        except Exception as e:
            raise APIServiceError(f"AI suggestion generation failed: {e}")
    
    # Backward compatibility methods for old service interface
    def getWeather_YiKeTianQi(self, client_ip: str) -> Dict[str, Any]:
        """
        Backward compatibility method for getting weather
        
        Args:
            client_ip: Client's IP address
            
        Returns:
            Weather information in old format
        """
        return self.get_weather_by_ip(client_ip)
    
    def getLLMSuggestion_Qwen(self, conversation: List[Dict[str, str]], 
                             system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Backward compatibility method for AI suggestions
        
        Args:
            conversation: List of conversation messages
            system_prompt: Optional system prompt
            
        Returns:
            AI-generated response
        """
        return self.get_ai_suggestion(conversation, system_prompt) 