from datetime import datetime
import pandas as pd
import sqlite3
import telebot
from telebot import types
import Data.const as CONST

bot = telebot.TeleBot(CONST.TOKEN_BUYPHONE)
search_mode = 'Min'


def rec_user(message, s_m):
    today = datetime.today()
    record = [[message.from_user.id, message.from_user.first_name, message.from_user.last_name,
               message.from_user.username, today, s_m]]
    conn = sqlite3.connect(r'Data/smartphone.db')
    z = pd.DataFrame(record)
    z.columns = ['id_user', 'first_name', 'last_name', 'username', 'date', 'search_key']
    z.to_sql(name='users', if_exists='replace', con=conn, index=False)


def search_data(df, search_str):
    if df[df['model'].str.contains(search_str, case=False)].sort_values('price').shape[0] > 0:
        search_result = df[df['model'].str.contains(search_str, case=False)].sort_values('price')
    else:
        search_str = search_str.split(' ')
        base = r'^{}'
        expr = '(?=.*{})'
        search_result = df[df['model'].str.contains(base.format(''.join(expr.format(w) for w in search_str)),
                                                    case=False)].sort_values('price')
    return search_result


def print_res_bot(df, store, search_str):
    if df.shape[0] > 0:
        message = f'[{store[2]}]({store[4]}{"+".join(search_str.split(" "))}): найдено записей - {df.shape[0]},' + \
                  f' цены от *{df["price"].min()}* до *{df["price"].max()}*\n'
        if search_mode == 'Min':
            message += '*Показаны позиции с минимальной ценой*\n'
            for row in df[df['price'] == df['price'].min()].itertuples(index=False):
                if not pd.isna(row[4]):
                    message += f"[{row[2]}]({row[5]}) | {row[4]}\n"
                else:
                    message += f"[{row[2]}]({row[5]}) | Нет акций\n"
        elif search_mode == 'Max':
            message += '*Показаны позиции с максимальной ценой*\n'
            for row in df[df['price'] == df['price'].max()].itertuples(index=False):
                if not pd.isna(row[2]):
                    message += f"[{row[2]}]({row[5]}) | {row[4]}\n"
                else:
                    message += f"[{row[2]}]({row[5]}) | Нет акций\n"
        else:
            message += '*Показаны все позиции*\n'
            for row in df.itertuples(index=False):
                if not pd.isna(row[2]):
                    message += f"[{row[2]}]({row[5]}) | *{row[3]}* | {row[4]}\n"
                else:
                    message += f"[{row[2]}]({row[5]}) | *{row[3]}* | Нет акций\n"
        return message
    else:
        return f'[{store[2]}]({store[3]}): ничего не найдено'


@bot.message_handler(commands=['start'])  # создаем команду
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    btn2 = types.KeyboardButton("/config")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, CONST.START_MESSAGE, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=['config'])  # создаем команду
def config(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Min")
    btn2 = types.KeyboardButton("Max")
    btn3 = types.KeyboardButton("All")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, CONST.CONFIG_MESSAGE, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=['help'])  # создаем команду
def help_(message):
    bot.send_message(message.chat.id, CONST.HELP_MESSAGE, parse_mode="Markdown",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global search_mode
    if message.text == 'Min':
        search_mode = 'Min'
        bot.send_message(message.from_user.id, 'В результате поиска будут показаны товары с минимальной ценой',
                         reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Max':
        search_mode = 'Max'
        bot.send_message(message.from_user.id, 'В результате поиска будут показаны товары с максимальной ценой',
                         reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'All':
        search_mode = 'All'
        bot.send_message(message.from_user.id, 'В результате поиска будут показаны все товары',
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        search_str = message.text
        conn = sqlite3.connect(r'Data/smartphone.db')
        stores = pd.read_sql("SELECT * from stores", conn)
        phones = pd.read_sql("SELECT * from smartphones", conn)
        conn.close()
        for store in stores.itertuples(index=False):
            max_date = phones[phones['id_store'] == store[0]]['date'].max()
            df = search_data(phones[(phones['id_store'] == store[0]) & (phones['date'] == max_date)], search_str)
            result = print_res_bot(df, store, search_str)
            # разбиваем длинное сообщение
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.from_user.id, result[x:x + 4096],
                                     parse_mode="Markdown", disable_web_page_preview=True)
            else:
                bot.send_message(message.from_user.id, result, parse_mode="Markdown", disable_web_page_preview=True)
    rec_user(message, search_mode)


def start_bot():
    bot.polling(none_stop=True, interval=1)
