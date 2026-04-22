"""
Модуль обработчиков команд и сообщений бота
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    get_main_keyboard,
    get_services_categories_keyboard,
    get_category_services_keyboard,
    get_contacts_keyboard,
    get_ai_chat_keyboard
)
from services_data import SERVICES
from ai_service import send_ai_request, reset_conversation, init_user_conversation
from config import logger

# Инициализация роутера
router = Router()

# Состояния FSM
class BotStates(StatesGroup):
    main_menu = State()
    ai_chat = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запустил бота")
    
    welcome_text = """
👋 Добро пожаловать в **Factura Beauty Boutique**!

✨ Премиальный бутик красоты в Новосибирске

Здесь вы найдёте полный спектр услуг для вашей красоты и здоровья.
Выберите нужный раздел в меню ниже:
    """
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    
    await state.set_state(BotStates.main_menu)

@router.message(BotStates.main_menu, F.text == "💅 Услуги")
async def show_services(message: Message):
    """Обработчик кнопки 'Услуги'"""
    logger.info(f"Пользователь {message.from_user.id} открыл список услуг")
    
    await message.answer(
        "💅 Наши услуги:\n\nВыберите категорию:",
        reply_markup=get_services_categories_keyboard()
    )

@router.callback_query(F.data == "services_list")
async def callback_show_services(callback: CallbackQuery):
    """Обработчик возврата к списку категорий услуг"""
    await callback.message.edit_text(
        "💅 Наши услуги:\n\nВыберите категорию:",
        reply_markup=get_services_categories_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def show_category_services(callback: CallbackQuery):
    """Обработчик выбора категории услуг"""
    category_id = callback.data.split("_", 1)[1]
    
    if category_id not in SERVICES:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    
    category = SERVICES[category_id]
    services_list = "\n".join([f"• {service}" for service in category["services"]])
    
    text = f"""
{category['name']}

{services_list}

📞 Для записи звоните: +7 (913) 917-66-49
    """
    
    await callback.message.edit_text(
        text,
        reply_markup=get_category_services_keyboard(category_id)
    )
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    await callback.message.edit_text(
        "Вы вернулись в главное меню. Выберите нужный раздел:"
    )
    await callback.answer()

@router.message(BotStates.main_menu, F.text == "📍 Контактные данные")
async def show_contacts(message: Message):
    """Обработчик кнопки 'Контактные данные'"""
    logger.info(f"Пользователь {message.from_user.id} открыл контакты")
    
    contacts_text = """
📍 **Контактные данные Factura Beauty Boutique**

📍 Адрес: г. Новосибирск, Титова 21
📞 Телефон: +79139176649
💬 Telegram
🕐 Часы работы:
Пн-Пт 10:00–20:00
Сб-Вс 11:00–18:00
    """
    
    await message.answer(
        contacts_text,
        reply_markup=get_contacts_keyboard(),
        parse_mode="Markdown"
    )

@router.message(BotStates.main_menu, F.text == "💬 Спросить AI-ассистента")
async def start_ai_chat(message: Message, state: FSMContext):
    """Обработчик входа в чат с AI"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вошёл в чат с AI")
    
    init_user_conversation(user_id)
    
    await message.answer(
        """
🤖 Вы вошли в чат с AI-ассистентом Factura.

Я могу:
• Ответить на вопросы об услугах
• Посоветовать подходящую процедуру
• Консультировать по уходу
• Ответить на любые вопросы о нашем бутике

Напишите ваш вопрос или нажмите кнопку для выхода.
        """,
        reply_markup=get_ai_chat_keyboard()
    )
    
    await state.set_state(BotStates.ai_chat)

@router.message(BotStates.ai_chat, F.text == "⬅️ Выйти из чата с AI")
async def exit_ai_chat(message: Message, state: FSMContext):
    """Обработчик выхода из чата с AI"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вышел из чата с AI")
    
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_keyboard()
    )
    
    await state.set_state(BotStates.main_menu)

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    """Обработчик команды /reset — очистка истории диалога"""
    user_id = message.from_user.id
    reset_conversation(user_id)
    logger.info(f"Пользователь {user_id} сбросил историю диалога AI")
    
    await message.answer("✅ История диалога очищена. Можете начать заново.")

@router.message(BotStates.ai_chat)
async def handle_ai_message(message: Message, state: FSMContext):
    """Обработчик сообщений в режиме чата с AI"""
    user_id = message.from_user.id
    
    if message.text:
        logger.info(f"Пользователь {user_id} отправил запрос к AI: {message.text[:50]}...")
        
        # Показываем что бот печатает
        try:
            await message.chat.do("typing")
        except:
            pass
        
        try:
            ai_response = await send_ai_request(user_id, message.text)
            await message.answer(ai_response)
        except Exception as e:
            logger.error(f"КРИТИЧЕСКАЯ ОШИБКА В ИИ ОБРАБОТЧИКЕ: {repr(e)}", exc_info=True)
            await message.answer("Извините, произошла ошибка. Попробуйте еще раз или обратитесь по телефону +7 (913) 917-66-49")

@router.message(BotStates.main_menu, F.text == "ℹ️ О салоне")
async def show_about(message: Message):
    """Обработчик кнопки 'О салоне'"""
    logger.info(f"Пользователь {message.from_user.id} открыл информацию о салоне")
    
    about_text = """
✨ **Factura Beauty Boutique**

Премиальный салон красоты в Новосибирске.

Мы предлагаем полный спектр услуг: косметология, парикмахерские услуги, маникюр и педикюр, массаж, оформление ресниц и бровей, SPA-процедуры.

Наши мастера — сертифицированные специалисты с многолетним опытом.
Мы используем только премиальную профессиональную косметику мировых брендов.

Каждый клиент для нас — особенная личность, заслуживающая самого лучшего ухода.
    """
    
    await message.answer(
        about_text,
        parse_mode="Markdown"
    )