import requests
import random
from time import time, sleep
from user_agent import generate_user_agent
import secrets
import json
import os
from random import randrange, choice
from concurrent.futures import ThreadPoolExecutor
from faker import Faker
import telebot
from telebot import types
import threading
import asyncio


BOT_TOKEN = "7305585141:AAHO6z6VXEWb6xest37dyLU1WIYMvWdKen0"
bot = telebot.TeleBot(BOT_TOKEN)


active_sessions = {}
stop_flags = {}
user_counts = {}


O = '\x1b[38;5;208m'
Z = '\033[1;31m'
F = '\033[2;32m'
R = '\033[1;31m'

def get_username(chat_id, min_uid, uid):

    while chat_id in active_sessions and not stop_flags.get(chat_id, False):
        try:
            re = str(randrange(min_uid, uid))
            csrftoken = secrets.token_hex(32)
            mmidd = secrets.token_hex(27)
            ig_ = secrets.token_hex(36)
            datrr = secrets.token_hex(24)
            faker = Faker()
            fak = faker.user_agent()
            app = ''.join(random.choice('936619743392459') for i in range(15))

            cookies = {
                'csrftoken': csrftoken,
                'ps_l': '0',
                'ps_n': '0',
                'ig_did': f'{ig_}',
                'ig_nrcb': '1',
                'dpr': '2.1988937854766846',
                'mid': mmidd,
                'datr': datrr,
            }

            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded',
                'dpr': '2.19889',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': fak,
                'viewport-width': '891',
                'x-asbd-id': '129477',
                'x-csrftoken': csrftoken,
                'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
                'x-fb-lsd': 'AVoRhvRPoRs',
                'x-ig-app-id': app,
            }

            data = {
                'av': '0',
                '__d': 'www',
                '__user': '0',
                '__a': '1',
                '__req': '1',
                '__hs': '19820.HYP:instagram_web_pkg.2.1..0.0',
                'dpr': '2',
                '__ccg': 'UNKNOWN',
                '__rev': '1012604142',
                '__s': 'dmjo05:l5d6wo:20s0u7',
                '__hsi': '7355192092986103751',
                '__dyn': '7xeUjG1mxu1syUbFp40NonwgU29zEdF8aUco2qwJw5ux609vCwjE1xoswaq0yE7i0n24oaEd86a3a1YwBgao6C0Mo2swaO4U2zxe2GewGwso88cobEaU2eUlwhEe87q7U88138bpEbUGdwtU662O0Lo6-3u2WE5B0bK1Iwqo5q1IQp1yUoxe4UrAwCAxW6U',
                '__csr': 'gVb2snsIjkIQyjRmBaFGECih59Fb98nQBzbZ2IN8BqBGl7h9Am4ohAAD-vGBh4GizA-4aAiJ2vFDUR3qx596AhrBgzJlBKmu6VHiypryUkByrGiicgPAx6iUpGEOmqfykFA4801kXEkOwmU1Tqwvk8wCix64E0b_EaWdguwozat2F61-wiokxG0d9w2MFU5Kzo0k6wiU7Kut2F601_Ew1me',
                '__comet_req': '7',
                'lsd': 'AVoRhvRPoRs',
                'jazoest': '21036',
                '__spin_r': '1012604142',
                '__spin_b': 'trunk',
                '__spin_t': '1712514108',
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'PolarisProfilePageContentQuery',
                'variables': '{"id":"' + re + '","relay_header":false,"render_surface":"PROFILE"}',
                'server_timestamps': 'true',
                'doc_id': '7381344031985950',
            }

            response = requests.post('https://www.instagram.com/api/graphql',
                                   cookies=cookies, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                response_data = response.json()
                if 'data' in response_data and response_data['data'] and 'user' in response_data['data']:
                    username = response_data['data']['user']['username']


                    if chat_id not in user_counts:
                        user_counts[chat_id] = 0
                    user_counts[chat_id] += 1




                    with open(f'aras-user-{chat_id}.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{username}\n')

                    sleep(0.5)

        except Exception as e:
            sleep(1)
            continue

@bot.message_handler(commands=['start'])
def start_message(message):

    chat_id = message.chat.id


    markup = types.InlineKeyboardMarkup(row_width=3)

    years_buttons = [
        types.InlineKeyboardButton("2010", callback_data="year_2010"),
        types.InlineKeyboardButton("2011", callback_data="year_2011"),
        types.InlineKeyboardButton("2012", callback_data="year_2012"),
        types.InlineKeyboardButton("2013", callback_data="year_2013"),
        types.InlineKeyboardButton("2014", callback_data="year_2014"),
        types.InlineKeyboardButton("2015", callback_data="year_2015"),
        types.InlineKeyboardButton("2016", callback_data="year_2016"),
        types.InlineKeyboardButton("2017", callback_data="year_2017"),
        types.InlineKeyboardButton("2018", callback_data="year_2018"),
        types.InlineKeyboardButton("2019", callback_data="year_2019"),
        types.InlineKeyboardButton("2020", callback_data="year_2020"),
        types.InlineKeyboardButton("2021", callback_data="year_2021"),
        types.InlineKeyboardButton("2022", callback_data="year_2022"),
        types.InlineKeyboardButton("2023", callback_data="year_2023"),
        types.InlineKeyboardButton("2024", callback_data="year_2024"),
    ]

    markup.add(*years_buttons)
    markup.add(types.InlineKeyboardButton("ڪـل سـنـوات", callback_data="year_all"))

    bot.send_message(chat_id, "🔥 يابه منور بوت اراس @W4_M4                                قـنـاتي : https://t.me/pytho1n", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('year_'))
def handle_year_selection(call):

    chat_id = call.message.chat.id
    year = call.data.split('_')[1]


    if chat_id in active_sessions:
        stop_flags[chat_id] = True
        del active_sessions[chat_id]


    years_uid = {
        '2010': (1, 10000000),
        '2011': (10000000, 18000000),
        '2012': (18000000, 26000000),
        '2013': (26000000, 36000000),
        '2014': (36000000, 100000000),
        '2015': (100000000, 300000000),
        '2016': (300000000, 500000000),
        '2017': (500000000, 700000000),
        '2018': (700000000, 1000000000),
        '2019': (1000000000, 1500000000),
        '2020': (1500000000, 2000000000),
        '2021': (2000000000, 2500000000),
        '2022': (2500000000, 3000000000),
        '2023': (3000000000, 3500000000),
        '2024': (3500000000, 4000000000),
        'all': (1, 4200000000),
    }

    if year in years_uid:
        min_uid, uid = years_uid[year]


        active_sessions[chat_id] = True
        stop_flags[chat_id] = False
        user_counts[chat_id] = 0


        try:
            os.remove(f'aras-user-{chat_id}.txt')
        except:
            pass


        stop_markup = types.InlineKeyboardMarkup()
        stop_markup.add(types.InlineKeyboardButton("أيقاف صـيـد", callback_data="stop_hunt"))

        bot.edit_message_text(
            f"تـم بدأ سحب يوزࢪات سنه {year}\n"
            f"مـطـوࢪ البوت @W4_M4"
            f" انتضࢪ 10 دقايق ودوس ايقاف \n\n"
            f"أضغط زر جوه للايقاف",
            chat_id, call.message.message_id, reply_markup=stop_markup
        )


        for i in range(15):
            thread = threading.Thread(target=get_username, args=(chat_id, min_uid, uid))
            thread.daemon = True
            thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop_hunt')
def stop_hunting_callback(call):

    chat_id = call.message.chat.id
    stop_hunting_process(chat_id, call.message.message_id)

@bot.message_handler(commands=['stop'])
def stop_hunting_command(message):

    chat_id = message.chat.id
    stop_hunting_process(chat_id)

def stop_hunting_process(chat_id, message_id=None):

    if chat_id in active_sessions:
        stop_flags[chat_id] = True
        del active_sessions[chat_id]

        count = user_counts.get(chat_id, 0)


        try:
            if os.path.exists(f'aras-user-{chat_id}.txt'):
                with open(f'aras-user-{chat_id}.txt', 'rb') as f:
                    bot.send_document(chat_id, f,
                                    caption=f" تـم سحب {count} يـوزࢪ ")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ في الاࢪسال حبي {str(e)}")


        if message_id:
            try:
                bot.edit_message_text(
                    f"تـم أيقاف صـيـد\n"
                    f"تـم سحب {count} يوزر\n"
                    f"تـم الاࢪسال",
                    chat_id, message_id
                )
            except:
                pass
        else:
            bot.send_message(chat_id, f" تـم سحب {count} يـوزࢪ")

        # تنظيف
        user_counts[chat_id] = 0
        try:
            os.remove(f'aras-user-{chat_id}.txt')
        except:
            pass
    else:
        bot.send_message(chat_id, "⚠️")


@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):

    chat_id = message.chat.id
    if chat_id not in active_sessions:
        bot.send_message(chat_id, "دوس سارت للبدء بوتت🗿")

if __name__ == "__main__":
    print("@W4_M4")
    print("تـم تشـغـيـل الـبـوت")
    bot.infinity_polling()