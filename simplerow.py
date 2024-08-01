from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_inline_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    row = [[InlineKeyboardButton(text=items[i], callback_data=str(i))] for i in range(len(items))]
    return InlineKeyboardMarkup(inline_keyboard=row)