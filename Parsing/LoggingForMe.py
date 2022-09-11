import telebot  # pip install pyTelegramBotAPI
import Data.const as CONST

bot = telebot.TeleBot(CONST.TOKEN_LOG)


def log(system, message):
    bot.send_message(CONST.USER, '*' + system + ':* ' + message, parse_mode="Markdown")
