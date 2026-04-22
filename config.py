"""
Модуль конфигурации бота
Загружает переменные из .env файла и настраивает логирование
"""
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# AI API конфигурация
AI_API_KEY = os.getenv('AI_API_KEY')
AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://api.proxyapi.ru/openai/v1')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Проверка наличия обязательных переменных
def validate_config():
    """Проверяет что все необходимые переменные заданы"""
    required_vars = [
        ('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN),
        ('AI_API_KEY', AI_API_KEY)
    ]
    
    missing = [name for name, value in required_vars if not value]
    
    if missing:
        logger.error(f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}")
        return False
    
    logger.info("Конфигурация успешно загружена")
    return True