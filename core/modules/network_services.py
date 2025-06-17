"""
Network Services Module
Handles email services and third-party API integrations
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
    """Custom exception for email service errors"""
    pass


class APIServiceError(Exception):
    """Custom exception for API service errors"""
    pass


class EmailService:
    """
    Modern email service with improved error handling and templating
    """
    
    def __init__(self):
        """Initialize email service with configuration"""
        try:
            email_config = config_manager.get_email_config()
            self._smtp_host = email_config['Host']
            self._smtp_port = email_config['Port']
            self._username = email_config['Username']
            self._password = email_config['Password']
            self._sender_address = email_config['Sender']
        except Exception as e:
            raise EmailServiceError(f"Failed to initialize email service: {e}")
        
        self._verification_template = self._get_verification_template()
    
    def _get_verification_template(self) -> str:
        """Get email verification template"""
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
        Send verification code to recipient
        
        Args:
            recipient_email: Recipient's email address
            verification_code: Verification code to send
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            EmailServiceError: If email configuration is invalid
        """
        try:
            # Ensure verification code is string
            if isinstance(verification_code, int):
                verification_code = str(verification_code)
            
            # Format email content
            email_content = self._verification_template.format(verification_code)
            
            # Create message
            message = MIMEText(email_content, 'html', 'utf-8')
            message['Subject'] = "墨韵读书平台 - 密码重置验证码"
            message['From'] = self._sender_address
            message['To'] = recipient_email
            
            return self._send_email(recipient_email, message)
            
        except Exception as e:
            raise EmailServiceError(f"Failed to send verification code: {e}")
    
    def _send_email(self, recipient: str, message: MIMEText) -> bool:
        """
        Send email via SMTP
        
        Args:
            recipient: Recipient email address
            message: Email message object
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            with SMTP_SSL(self._smtp_host, self._smtp_port) as smtp_server:
                smtp_server.set_debuglevel(0)  # Disable debug for production
                smtp_server.login(self._username, self._password)
                smtp_server.sendmail(self._sender_address, [recipient], message.as_string())
            return True
            
        except SMTPException as e:
            print(f"SMTP Error: {e}")
            return False
        except Exception as e:
            print(f"Email sending error: {e}")
            return False


class ExternalAPIService:
    """
    External API service for third-party integrations
    """
    
    # AI Model configurations
    AI_MODELS = {
        "qwen-turbo": "qwen-turbo",
        "qwen-plus": "qwen-plus", 
        "qwen-max": "qwen-max",
        "qwen-max-1201": "qwen-max-1201",
        "qwen-max-longcontext": "qwen-max-longcontext"
    }
    
    def __init__(self):
        """Initialize external API service"""
        self._user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'
        )
        
        # Load API configurations
        try:
            self._weather_config = config_manager.get_api_config('Yiketianqi')
            if DASHSCOPE_AVAILABLE:
                self._ai_config = config_manager.get_api_config('Qwen')
        except Exception as e:
            print(f"Warning: Some API configurations not available: {e}")
    
    def get_weather_by_ip(self, client_ip: str) -> Dict[str, Any]:
        """
        Get weather information based on client IP address
        
        Args:
            client_ip: Client's IP address
            
        Returns:
            Weather information dictionary
            
        Raises:
            APIServiceError: If weather API request fails
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