"""
Модуль с клавиатурами для бота
Все Reply и Inline клавиатуры
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services_data import SERVICES, CATEGORIES

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота (ReplyKeyboard)"""
    keyboard = [
        [
            KeyboardButton(text="💅 Услуги"),
            KeyboardButton(text="📍 Контактные данные")
        ],
        [
            KeyboardButton(text="💬 Спросить AI-ассистента"),
            KeyboardButton(text="ℹ️ О салоне")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )

def get_services_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с категориями услуг"""
    builder = InlineKeyboardBuilder()
    
    for category_id in CATEGORIES:
        category = SERVICES[category_id]
        builder.button(
            text=category["name"],
            callback_data=f"category_{category_id}"
        )
    
    builder.button(text="⬅️ Назад в меню", callback_data="main_menu")
    builder.adjust(2)
    
    return builder.as_markup()

def get_category_services_keyboard(category_id: str) -> InlineKeyboardMarkup:
    """Клавиатура с услугами выбранной категории"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="⬅️ Назад к категориям", callback_data="services_list")
    
    return builder.as_markup()

def get_contacts_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с контактными данными"""
    keyboard = [
        [
            InlineKeyboardButton(text="💬 Telegram", url="https://t.me/Factura_Beauty")
        ],
        [
            InlineKeyboardButton(text="🗺 Открыть на карте", url="https://yandex.ru/maps/-/CCU67zH7wD")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_ai_chat_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура во время чата с AI"""
    keyboard = [
        [
            KeyboardButton(text="⬅️ Выйти из чата с AI")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Напишите ваш вопрос..."
    )