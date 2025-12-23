from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def level_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Remedial", callback_data="level_remedial")],
        [InlineKeyboardButton("Freshman", callback_data="level_freshman")]
    ])