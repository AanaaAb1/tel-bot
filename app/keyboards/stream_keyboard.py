from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def stream_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Natural Science", callback_data="stream_natural")],
        [InlineKeyboardButton("Social Science", callback_data="stream_social")]
    ])