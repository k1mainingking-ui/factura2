"""
Модуль для работы с AI-ассистентом
Интеграция с OpenAI API через ProxyAPI
"""
from typing import Dict, List
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
from config import AI_API_KEY, AI_BASE_URL, AI_MODEL, logger

# Системный промпт для AI-ассистента
SYSTEM_PROMPT = """Ты — вежливый и профессиональный консультант премиального бутика красоты Factura в Новосибирске (ул. Титова, 21).
Ты помогаешь клиентам выбрать услуги, консультируешь по процедурам, отвечаешь на вопросы о красоте и уходе.
Общайся тепло, премиально, с заботой.
Если клиент хочет записаться — предложи позвонить по номеру +7 (913) 917-66-49.
Не выдумывай цены, если их нет в списке услуг.
Всегда отвечай на русском языке.
"""

# Хранилище истории диалогов (в оперативной памяти)
# user_id: List[messages]
conversation_history: Dict[int, List[Dict[str, str]]] = {}

# Максимальное количество сообщений в истории (последние 10)
MAX_HISTORY_LENGTH = 10

# Инициализация OpenAI клиента
import httpx

# Инициализация OpenAI клиента с отключенной проверкой SSL
import requests

# Инициализация OpenAI клиента с отключенной проверкой SSL
client = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL,
    timeout=60.0,
    max_retries=3,
    http_client=httpx.AsyncClient(verify=False)
)

# Проверка подключения к API
try:
    response = requests.get(AI_BASE_URL, timeout=10, verify=False)
    if response.status_code == 200:
        logger.info("✅ API доступен: " + AI_BASE_URL)
    else:
        logger.error(f"❌ API недоступен: {response.status_code}")
except Exception as e:
    logger.error(f"❌ Ошибка подключения к API: {repr(e)}")

def init_user_conversation(user_id: int) -> None:
    """Инициализирует или сбрасывает историю диалога для пользователя"""
    conversation_history[user_id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    logger.info(f"Инициализирована история диалога для пользователя {user_id}")

def add_message(user_id: int, role: str, content: str) -> None:
    """Добавляет сообщение в историю диалога"""
    if user_id not in conversation_history:
        init_user_conversation(user_id)
    
    conversation_history[user_id].append({"role": role, "content": content})
    
    # Ограничиваем историю последними 10 сообщениями (плюс системный промпт)
    if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH + 1:
        # Сохраняем системный промпт и последние сообщения
        conversation_history[user_id] = [
            conversation_history[user_id][0]
        ] + conversation_history[user_id][-MAX_HISTORY_LENGTH:]

def reset_conversation(user_id: int) -> None:
    """Очищает историю диалога пользователя"""
    init_user_conversation(user_id)

def get_conversation_history(user_id: int) -> List[Dict[str, str]]:
    """Возвращает историю диалога пользователя"""
    if user_id not in conversation_history:
        init_user_conversation(user_id)
    
    return conversation_history[user_id]

async def send_ai_request(user_id: int, user_message: str) -> str:
    """
    Отправляет запрос к AI и возвращает ответ
    В случае ошибки возвращает сообщение для пользователя
    """
    try:
        add_message(user_id, "user", user_message)
        
        response = await client.chat.completions.create(
            model=AI_MODEL,
            messages=get_conversation_history(user_id),
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content.strip()
        add_message(user_id, "assistant", ai_response)
        
        logger.info(f"Получен ответ от AI для пользователя {user_id}")
        return ai_response
    
    except APIConnectionError as e:
        logger.error(f"Ошибка подключения к AI API: {e}")
        logger.error(f"Полная ошибка: {repr(e)}")
        return "Извините, AI-ассистент временно недоступен. Позвоните нам: +7 (913) 917-66-49"
    
    except RateLimitError as e:
        logger.error(f"Превышен лимит запросов к AI API: {e}")
        return "Извините, сервис перегружен. Попробуйте позже или позвоните нам: +7 (913) 917-66-49"
    
    except APIError as e:
        logger.error(f"Ошибка API AI: {e}")
        return "Извините, произошла ошибка при обработке запроса. Позвоните нам: +7 (913) 917-66-49"
    
    except Exception as e:
        logger.error(f"Неизвестная ошибка в AI сервисе: {e}")
        return "Извините, временные неполадки. Позвоните нам: +7 (913) 917-66-49"