from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Submit Payment Proof", callback_data="submit_payment")]
    ])