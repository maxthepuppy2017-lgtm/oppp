#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# أداة صيد حسابات Safeum برمجة وتطوير ابن الحسني @VIP_7_I
# حقوق الملكية الفكرية محفوظة © 2024 ابن الحسني

import os
import sys
import time
import random
import string
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from ssl import CERT_NONE
from gzip import decompress
from random import choices
from websocket import create_connection
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التحقق من صلاحية التفعيل
current_time = datetime.now()
expiry_time = datetime(2029, 9, 30, 21, 40, 0)

if current_time > expiry_time:
    print('\033[1;31mانتهى التفعيل المجاني، راسل المطور @VIP_7_I للاشتراك المدفوع\033[0m')
    exit(0)

# الألوان
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'

# إعدادات البوت
TELEGRAM_BOT_TOKEN = "8255173841:AAENBw0QRv4qJ9Un2mG_XTf3chqRavbmnL8"
ADMIN_IDS = [6447367175]  # قائمة بآيدي المشرفين
CHANNEL_USERNAME = "@R_R_R_R_i0"  # قناة الاشتراك الإجباري

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# قاعدة البيانات
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TEXT,
                subscription_end TEXT,
                is_active INTEGER DEFAULT 1,
                accounts_count INTEGER DEFAULT 0
            )
        ''')

        # جدول الحسابات المصيدة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                password TEXT,
                capture_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # جدول مفاتيح التفعيل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activation_keys (
                key TEXT PRIMARY KEY,
                days INTEGER,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                created_date TEXT,
                created_by INTEGER,
                is_active INTEGER DEFAULT 1
            )
        ''')

        self.conn.commit()

    def add_user(self, user_id, username, first_name, last_name):
        cursor = self.conn.cursor()
        try:
            join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, join_date))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

    def update_subscription(self, user_id, days):
        cursor = self.conn.cursor()
        current_end = cursor.execute('SELECT subscription_end FROM users WHERE user_id = ?', (user_id,)).fetchone()

        if current_end and current_end[0]:
            # إذا كان هناك اشتراك ساري، نضيف الأيام الجديدة لنهاية الاشتراك الحالي
            current_end_date = datetime.strptime(current_end[0], '%Y-%m-%d %H:%M:%S')
            if current_end_date > datetime.now():
                end_date = current_end_date + timedelta(days=days)
            else:
                end_date = datetime.now() + timedelta(days=days)
        else:
            # إذا لم يكن هناك اشتراك ساري، نبدأ من الآن
            end_date = datetime.now() + timedelta(days=days)

        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            UPDATE users SET subscription_end = ? WHERE user_id = ?
        ''', (end_date_str, user_id))
        self.conn.commit()
        return True

    def is_subscribed(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False

        subscription_end = user[5]
        if not subscription_end:
            return False

        try:
            end_date = datetime.strptime(subscription_end, '%Y-%m-%d %H:%M:%S')
            return datetime.now() < end_date
        except:
            return False

    def add_account(self, user_id, username, password):
        cursor = self.conn.cursor()
        try:
            capture_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO accounts (user_id, username, password, capture_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, password, capture_date))

            cursor.execute('''
                UPDATE users SET accounts_count = accounts_count + 1
                WHERE user_id = ?
            ''', (user_id,))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding account: {e}")
            return False

    def get_user_accounts(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, password, capture_date FROM accounts WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, join_date, subscription_end, accounts_count FROM users')
        return cursor.fetchall()

    def get_bot_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accounts")
        total_accounts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_end IS NOT NULL AND subscription_end > datetime('now')")
        subscribed_users = cursor.fetchone()[0]

        return total_users, active_users, total_accounts, subscribed_users

    # وظائف جديدة لإدارة مفاتيح التفعيل
    def create_activation_key(self, key, days, max_uses, created_by):
        cursor = self.conn.cursor()
        try:
            created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO activation_keys (key, days, max_uses, used_count, created_date, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (key, days, max_uses, 0, created_date, created_by, 1))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating activation key: {e}")
            return False

    def get_activation_key(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM activation_keys WHERE key = ? AND is_active = 1', (key,))
        return cursor.fetchone()

    def use_activation_key(self, key, user_id):
        cursor = self.conn.cursor()
        try:
            key_data = self.get_activation_key(key)
            if not key_data:
                return False, "المفتاح غير صالح أو غير موجود"

            key_text, days, max_uses, used_count, created_date, created_by, is_active = key_data

            if used_count >= max_uses:
                return False, "تم استخدام هذا المفتاح لأقصى عدد من المرات"

            # تحديث عدد مرات الاستخدام
            cursor.execute('''
                UPDATE activation_keys SET used_count = used_count + 1
                WHERE key = ?
            ''', (key,))

            # تفعيل الاشتراك للمستخدم
            self.update_subscription(user_id, days)

            self.conn.commit()
            return True, f"تم تفعيل الاشتراك بنجاح لمدة {days} يوم"

        except Exception as e:
            print(f"Error using activation key: {e}")
            return False, f"خطأ في استخدام المفتاح: {str(e)}"

    def get_all_activation_keys(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM activation_keys ORDER BY created_date DESC')
        return cursor.fetchall()

    def delete_activation_key(self, key):
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM activation_keys WHERE key = ?', (key,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting activation key: {e}")
            return False

db = Database()

# نظام الصيد الأساسي
class SafeumHunter:
    def __init__(self, user_id):
        self.user_id = user_id
        self.success = 0
        self.failed = 0
        self.retry = 0
        self.accounts = []
        self.running = True
        self.password = "aaaa"
        self.hunting = False

    def generate_username(self, length):
        chars = string.ascii_lowercase + string.digits
        return ''.join(choices(chars, k=length))

    def create_account(self, username_length):
        if not self.running or not self.hunting:
            return

        username = self.generate_username(username_length)

        try:
            con = create_connection("wss://195.13.182.213/Auth",
                                  header={
                                      "app": "com.safeum.android",
                                      "host": None,
                                      "remoteIp": "195.13.182.213",
                                      "remotePort": str(8080),
                                      "sessionId": "b6cbb22d-06ca-41ff-8fda-c0ddeb148195",
                                      "time": "2024-04-11 11:00:00",
                                      "url": "wss://51.79.208.190/Auth"
                                  },
                                  sslopt={"cert_reqs": CERT_NONE})

            payload = {
                "action": "Register",
                "subaction": "Desktop",
                "locale": "ar_EG",
                "gmt": "+03",
                "password": {
                    "m1x": "674aa02c68df3f5c3fa11c7904b897532a17e50757f5a4252338aa00b49b2932",
                    "m1y": "9333b68c189bffa2935cdada6043ed9335c07ee9261535d8ddb4d7c0eb38c13c",
                    "m2": "9ddf1837873f902e9988d41f95f260303718bc8e3db872eebef871044a082975",
                    "iv": "87fa6e2284c7e219026975f72a5d423f",
                    "message": "d94df8c6593e7984970a41adf9dabd695265fa7363403717c7d7255060aa7a092997fd9c34ee6f055529eca9a7275a38bb0073c3209233c94b7f2c9b7a6971d5924317b481075c1ce1dde807ea5ea1d8"
                },
                "magicword": {
                    "m1x": "fa9dc82e219d8580e79acdc107f2593e73990034e386da7e53ef0552e42a1395",
                    "m1y": "25d2d66f684bc7a661cc2085ade22c41051b654f46ee2865bc171db38307c151",
                    "m2": "e85b5efc89564e1572861db4853af60cbc3b92e5a093f5735605ebdd8e1ddd8a",
                    "iv": "f7c847f7152dacf890a18f34bdfc07e3",
                    "message": "4f36925ed7fca213fb0f6b37ba906808"
                },
                "magicwordhint": "0000",
                "login": username,
                "devicename": "INFINIX Infinix X678B",
                "softwareversion": "1.1.0.2300",
                "nickname": "skksoskzhjdjridbn",
                "os": "AND",
                "deviceuid": "4b81ce4e8c8208f4",
                "devicepushuid": "*fZigg-TFSgij1Gr09Zduj3:APA91bH3N3I0dXrTR8lQ5SCYdbKLSDq6B-N5c3GF_ZkF5kRFQeHEc08hyAbq7Mn25v1d0jpjSxZopdyuIGFfTyq0jgpE7G8GNV-jI8j_ouOgysLe-DYzP7q9czJlkmA6UJn6QDDdxMzw",
                "osversion": "and_13.0.0",
                "id": "543208426"
            }

            con.send(json.dumps(payload))
            response = decompress(con.recv()).decode('utf-8')

            if '"status":"Success"' in response:
                self.success += 1
                account = f"{username}:{self.password}"
                self.accounts.append(account)

                # حفظ الحساب في قاعدة البيانات
                db.add_account(self.user_id, username, self.password)

                # حفظ في الملف
                with open(f'حسابات_{self.user_id}.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{account} | @VIP_7_I\n")

                # إرسال إشعار للمستخدم
                try:
                    stats_msg = f"""
✅ <b>تم صيد حساب جديد!</b>

👤 <b>اليوزر:</b> <code>{username}</code>
🔑 <b>الباسورد:</b> <code>{self.password}</code>

📊 <b>الإحصائيات:</b>
• الناجحة: {self.success}
• الفاشلة: {self.failed}
• المحاولات: {self.retry}

🛠 <b>المطور:</b> @VIP_7_I
                    """
                    bot.send_message(self.user_id, stats_msg, parse_mode='HTML')
                except:
                    pass

            else:
                self.failed += 1
        except Exception as e:
            self.retry += 1

    def start_hunting(self, username_length):
        self.hunting = True
        self.running = True

        def hunt():
            with ThreadPoolExecutor(max_workers=50) as executor:
                try:
                    while self.hunting and self.running:
                        executor.submit(self.create_account, username_length)
                        time.sleep(0.9)
                except Exception as e:
                    print(f"Error in hunting: {e}")

        thread = threading.Thread(target=hunt)
        thread.daemon = True
        thread.start()

    def stop_hunting(self):
        self.hunting = False
        self.running = False

# متغيرات الصيد لكل مستخدم
user_hunters = {}

# الأزرار
def main_menu(user_id):
    user = db.get_user(user_id)
    markup = InlineKeyboardMarkup()

    if db.is_subscribed(user_id):
        markup.row(
            InlineKeyboardButton("🎯 صيد 6 أحرف", callback_data="hunt_6"),
            InlineKeyboardButton("🎯 صيد 7 أحرف", callback_data="hunt_7")
        )
        markup.row(
            InlineKeyboardButton("🎯 صيد 8 أحرف", callback_data="hunt_8"),
            InlineKeyboardButton("🎯 صيد 9 أحرف", callback_data="hunt_9")
        )
        markup.row(
            InlineKeyboardButton("⏹ إيقاف الصيد", callback_data="stop_hunt"),
            InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")
        )
        markup.row(
            InlineKeyboardButton("📋 حساباتي", callback_data="my_accounts"),
            InlineKeyboardButton("👤 عضويتي", callback_data="my_subscription")
        )
    else:
        markup.row(
            InlineKeyboardButton("💳 تفعيل العضوية", callback_data="activate_subscription"),
            InlineKeyboardButton("🔑 تفعيل بالكود", callback_data="activate_with_key")
        )

    if user_id in ADMIN_IDS:
        markup.row(InlineKeyboardButton("👨‍💼 لوحة التحكم", callback_data="admin_panel"))

    return markup

def admin_panel():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats"),
        InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast")
    )
    markup.row(
        InlineKeyboardButton("➕ إضافة عضوية", callback_data="admin_add_sub"),
        InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")
    )
    markup.row(
        InlineKeyboardButton("🔑 إدارة المفاتيح", callback_data="admin_keys"),
        InlineKeyboardButton("➕ إنشاء مفتاح", callback_data="admin_create_key")
    )
    markup.row(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main"))
    return markup

def keys_management_panel():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📋 عرض المفاتيح", callback_data="admin_view_keys"),
        InlineKeyboardButton("🗑 حذف مفتاح", callback_data="admin_delete_key")
    )
    markup.row(InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel"))
    return markup

# التحقق من الاشتراك في القناة
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# معالجة الأوامر
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    # إضافة المستخدم إلى قاعدة البيانات
    db.add_user(user_id, username, first_name, last_name)

    # التحقق من الاشتراك
    if not check_subscription(user_id):
        bot.send_message(
            user_id,
            f"👋 أهلاً بك {first_name}!\n\n"
            f"📢 يجب الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}\n\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📢 الانضمام للقناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
            )
        )
        return

    # التحقق من العضوية
    if not db.is_subscribed(user_id):
        bot.send_message(
            user_id,
            f"👋 أهلاً بك {first_name}!\n\n"
            f"⚠️ العضوية غير مفعلة!\n"
            f"يمكنك تفعيل العضوية عبر:\n"
            f"• الشراء من المطور\n"
            f"• استخدام كود التفعيل\n\n"
            f"🛠 للمساعدة: @VIP_7_I",
            reply_markup=main_menu(user_id)
        )
    else:
        user = db.get_user(user_id)
        end_date = user[5] if user and user[5] else 'غير معروف'
        bot.send_message(
            user_id,
            f"👋 أهلاً بك {first_name}!\n\n"
            f"✅ العضوية مفعلة حتى:\n{end_date}\n\n"
            f"🎯 اختر نوع الصيد:",
            reply_markup=main_menu(user_id)
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    message_id = call.message.message_id

    if not check_subscription(user_id):
        bot.answer_callback_query(call.id, "يجب الاشتراك في القناة أولاً!")
        return

    if call.data == "back_to_main":
        bot.edit_message_text(
            "🎯 القائمة الرئيسية:",
            user_id,
            message_id,
            reply_markup=main_menu(user_id)
        )

    elif call.data.startswith("hunt_"):
        if not db.is_subscribed(user_id):
            bot.answer_callback_query(call.id, "العضوية غير مفعلة!")
            return

        username_length = int(call.data.split("_")[1])

        # إنشاء صياد جديد للمستخدم إذا لم يكن موجوداً
        if user_id not in user_hunters:
            user_hunters[user_id] = SafeumHunter(user_id)

        hunter = user_hunters[user_id]

        if hunter.hunting:
            bot.answer_callback_query(call.id, "الصيد يعمل بالفعل!")
            return

        bot.answer_callback_query(call.id, f"بدأ الصيد بحسابات {username_length} أحرف!")
        bot.edit_message_text(
            f"🎯 بدأ الصيد بحسابات {username_length} أحرف...\n\n"
            f"⏳ جاري البحث عن الحسابات...\n"
            f"📝 كلمة السر: aaaa\n\n"
            f"⏹ استخدم زر إيقاف الصيد للتوقف",
            user_id,
            message_id,
            reply_markup=main_menu(user_id)
        )

        hunter.start_hunting(username_length)

    elif call.data == "stop_hunt":
        if user_id in user_hunters:
            hunter = user_hunters[user_id]
            if hunter.hunting:
                hunter.stop_hunting()
                bot.answer_callback_query(call.id, "تم إيقاف الصيد!")
                bot.edit_message_text(
                    f"⏹ تم إيقاف الصيد\n\n"
                    f"📊 إحصائيات الجلسة:\n"
                    f"• الناجحة: {hunter.success}\n"
                    f"• الفاشلة: {hunter.failed}\n"
                    f"• المحاولات: {hunter.retry}",
                    user_id,
                    message_id,
                    reply_markup=main_menu(user_id)
                )
            else:
                bot.answer_callback_query(call.id, "لا يوجد صيد نشط!")
        else:
            bot.answer_callback_query(call.id, "لا يوجد صيد نشط!")

    elif call.data == "my_stats":
        user = db.get_user(user_id)
        accounts = db.get_user_accounts(user_id)

        if not user:
            bot.answer_callback_query(call.id, "لم يتم العثور على بيانات المستخدم!")
            return

        stats_text = f"""
📊 <b>إحصائياتك الشخصية</b>

👤 <b>المستخدم:</b> {user[2]}
📅 <b>تاريخ الانضمام:</b> {user[4]}
✅ <b>الحسابات المصيدة:</b> {user[7]}
⏰ <b>انتهاء العضوية:</b> {user[5] if user[5] else 'غير مفعلة'}

🛠 <b>المطور:</b> @VIP_7_I
        """

        bot.edit_message_text(
            stats_text,
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=main_menu(user_id)
        )

    elif call.data == "my_accounts":
        accounts = db.get_user_accounts(user_id)

        if not accounts:
            bot.answer_callback_query(call.id, "لا توجد حسابات مصيدة بعد!")
            return

        # إرسال ملف الحسابات
        try:
            with open(f'حسابات_{user_id}.txt', 'rb') as f:
                bot.send_document(
                    user_id,
                    f,
                    caption=f"📋 حساباتك المصيدة ({len(accounts)} حساب)"
                )
        except:
            # إذا لم يوجد ملف، ننشئ واحد
            with open(f'حسابات_{user_id}.txt', 'w', encoding='utf-8') as f:
                for acc in accounts[-50:]:  # آخر 50 حساب
                    f.write(f"{acc[0]}:{acc[1]} | {acc[2]}\n")

            with open(f'حسابات_{user_id}.txt', 'rb') as f:
                bot.send_document(
                    user_id,
                    f,
                    caption=f"📋 حساباتك المصيدة ({len(accounts)} حساب)"
                )

    elif call.data == "my_subscription":
        user = db.get_user(user_id)

        if not user:
            bot.answer_callback_query(call.id, "لم يتم العثور على بيانات المستخدم!")
            return

        sub_text = f"""
👤 <b>معلومات العضوية</b>

🆔 <b>آيدي:</b> <code>{user_id}</code>
👤 <b>الاسم:</b> {user[2]}
📅 <b>تاريخ الانضمام:</b> {user[4]}
✅ <b>الحسابات المصيدة:</b> {user[7]}

⏰ <b>حالة العضوية:</b> {'مفعلة' if db.is_subscribed(user_id) else 'غير مفعلة'}
📅 <b>انتهاء العضوية:</b> {user[5] if user[5] else 'غير مفعلة'}

💳 <b>لتفعيل العضوية:</b>
@VIP_7_I
        """

        bot.edit_message_text(
            sub_text,
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=main_menu(user_id)
        )

    elif call.data == "activate_subscription":
        bot.edit_message_text(
            "💳 <b>تفعيل العضوية</b>\n\n"
            "لتفعيل العضوية، راسل المطور:\n"
            "@VIP_7_I\n\n"
            "📦 <b>الباقات المتاحة:</b>\n"
            "• 7 أيام: 5$ 💵\n"
            "• 30 يوم: 15$ 💵\n"
            "• 90 يوم: 35$ 💵\n\n"
            "أو استخدم كود التفعيل إذا كان لديك واحد",
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton("🔑 تفعيل بالكود", callback_data="activate_with_key"),
                InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
            )
        )

    elif call.data == "activate_with_key":
        msg = bot.send_message(
            user_id,
            "🔑 <b>تفعيل العضوية بالكود</b>\n\n"
            "أرسل كود التفعيل الآن:",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_activation_key)

    # لوحة التحكم للمشرفين
    elif call.data == "admin_panel" and user_id in ADMIN_IDS:
        bot.edit_message_text(
            "👨‍💼 <b>لوحة تحكم المشرفين</b>",
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=admin_panel()
        )

    elif call.data == "admin_stats" and user_id in ADMIN_IDS:
        total_users, active_users, total_accounts, subscribed_users = db.get_bot_stats()

        stats_text = f"""
📊 <b>إحصائيات البوت</b>

👥 <b>إجمالي المستخدمين:</b> {total_users}
✅ <b>المستخدمين النشطين:</b> {active_users}
🎯 <b>الحسابات المصيدة:</b> {total_accounts}
💳 <b>المشتركين:</b> {subscribed_users}

🛠 <b>المطور:</b> @VIP_7_I
        """

        bot.edit_message_text(
            stats_text,
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=admin_panel()
        )

    elif call.data == "admin_broadcast" and user_id in ADMIN_IDS:
        msg = bot.send_message(
            user_id,
            "📢 <b>أرسل الرسالة للإذاعة:</b>\n\n"
            "يمكنك استخدام HTML للتنسيق",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_broadcast)

    elif call.data == "admin_add_sub" and user_id in ADMIN_IDS:
        msg = bot.send_message(
            user_id,
            "➕ <b>إضافة عضوية</b>\n\n"
            "أرسل آيدي المستخدم وعدد الأيام بالصيغة:\n"
            "<code>آيدي_المستخدم عدد_الأيام</code>\n\n"
            "مثال:\n<code>6447367175 30</code>",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_add_subscription)

    elif call.data == "admin_users" and user_id in ADMIN_IDS:
        users = db.get_all_users()

        if not users:
            bot.answer_callback_query(call.id, "لا يوجد مستخدمين!")
            return

        users_text = "👥 <b>قائمة المستخدمين</b>\n\n"
        for user in users[:10]:  # عرض أول 10 مستخدمين فقط
            user_id, username, first_name, join_date, sub_end, accounts_count = user
            status = "مفعل" if db.is_subscribed(user_id) else "غير مفعل"
            users_text += f"👤 {first_name} (@{username})\n"
            users_text += f"🆔: {user_id} | 📊: {accounts_count}\n"
            users_text += f"📅: {join_date} | ✅: {status}\n\n"

        bot.edit_message_text(
            users_text,
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=admin_panel()
        )

    # إدارة المفاتيح
    elif call.data == "admin_keys" and user_id in ADMIN_IDS:
        bot.edit_message_text(
            "🔑 <b>إدارة مفاتيح التفعيل</b>\n\n"
            "اختر الإجراء المطلوب:",
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=keys_management_panel()
        )

    elif call.data == "admin_create_key" and user_id in ADMIN_IDS:
        msg = bot.send_message(
            user_id,
            "➕ <b>إنشاء مفتاح تفعيل جديد</b>\n\n"
            "أرسل البيانات بالصيغة:\n"
            "<code>عدد_الأيام عدد_الاستخدامات</code>\n\n"
            "مثال:\n<code>30 5</code>\n\n"
            "سيتم إنشاء مفتاح عشوائي تلقائياً",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_create_key)

    elif call.data == "admin_view_keys" and user_id in ADMIN_IDS:
        keys = db.get_all_activation_keys()

        if not keys:
            bot.answer_callback_query(call.id, "لا توجد مفاتيح!")
            return

        keys_text = "🔑 <b>قائمة مفاتيح التفعيل</b>\n\n"
        for key_data in keys[:10]:  # عرض أول 10 مفاتيح فقط
            key, days, max_uses, used_count, created_date, created_by, is_active = key_data
            status = "نشط" if is_active else "غير نشط"
            keys_text += f"🔑 <code>{key}</code>\n"
            keys_text += f"⏰ {days} يوم | 🔄 {used_count}/{max_uses}\n"
            keys_text += f"📅 {created_date} | ✅ {status}\n\n"

        bot.edit_message_text(
            keys_text,
            user_id,
            message_id,
            parse_mode='HTML',
            reply_markup=keys_management_panel()
        )

    elif call.data == "admin_delete_key" and user_id in ADMIN_IDS:
        msg = bot.send_message(
            user_id,
            "🗑 <b>حذف مفتاح تفعيل</b>\n\n"
            "أرسل المفتاح الذي تريد حذفه:",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_delete_key)

def generate_activation_key(length=16):
    """إنشاء مفتاح تفعيل عشوائي"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(choices(chars, k=length))

def process_activation_key(message):
    user_id = message.from_user.id
    key = message.text.strip()

    success, result = db.use_activation_key(key, user_id)

    if success:
        bot.send_message(
            user_id,
            f"✅ {result}\n\n"
            f"🎉 تم تفعيل العضوية بنجاح!\n"
            f"يمكنك الآن استخدام جميع ميزات البوت",
            reply_markup=main_menu(user_id)
        )
    else:
        bot.send_message(
            user_id,
            f"❌ {result}\n\n"
            f"⚠️ يرجى التأكد من صحة الكود والمحاولة مرة أخرى",
            reply_markup=main_menu(user_id)
        )

def process_create_key(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.from_user.id, "❌ صيغة غير صحيحة! استخدم: عدد_الأيام عدد_الاستخدامات")
            return

        days = int(parts[0])
        max_uses = int(parts[1])

        # إنشاء مفتاح عشوائي
        key = generate_activation_key()

        # حفظ المفتاح في قاعدة البيانات
        success = db.create_activation_key(key, days, max_uses, message.from_user.id)

        if success:
            bot.send_message(
                message.from_user.id,
                f"✅ <b>تم إنشاء المفتاح بنجاح!</b>\n\n"
                f"🔑 <b>المفتاح:</b> <code>{key}</code>\n"
                f"⏰ <b>المدة:</b> {days} يوم\n"
                f"🔄 <b>الاستخدامات:</b> {max_uses} مرة\n\n"
                f"📋 يمكنك مشاركة هذا المفتاح مع المستخدمين",
                parse_mode='HTML',
                reply_markup=admin_panel()
            )
        else:
            bot.send_message(message.from_user.id, "❌ حدث خطأ أثناء إنشاء المفتاح!")

    except ValueError:
        bot.send_message(message.from_user.id, "❌ يرجى إدخال أرقام صحيحة!")
    except Exception as e:
        bot.send_message(message.from_user.id, f"❌ حدث خطأ: {str(e)}")

def process_delete_key(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    key = message.text.strip()

    success = db.delete_activation_key(key)

    if success:
        bot.send_message(
            message.from_user.id,
            f"✅ <b>تم حذف المفتاح بنجاح!</b>\n\n"
            f"🔑 المفتاح المحذوف: <code>{key}</code>",
            parse_mode='HTML',
            reply_markup=admin_panel()
        )
    else:
        bot.send_message(
            message.from_user.id,
            f"❌ <b>فشل في حذف المفتاح!</b>\n\n"
            f"تأكد من صحة المفتاح وحاول مرة أخرى",
            parse_mode='HTML',
            reply_markup=admin_panel()
        )

def process_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    users = db.get_all_users()
    success = 0
    failed = 0

    broadcast_msg = bot.send_message(
        message.from_user.id,
        f"⏳ جاري إرسال الرسالة لـ {len(users)} مستخدم..."
    )

    for user in users:
        try:
            bot.send_message(user[0], message.text, parse_mode='HTML')
            success += 1
        except:
            failed += 1
        time.sleep(0.5)  # تجنب حظر التيليجرام

    bot.edit_message_text(
        f"✅ <b>تمت الإذاعة بنجاح!</b>\n\n"
        f"📊 النتائج:\n"
        f"• ✅ الناجحة: {success}\n"
        f"• ❌ الفاشلة: {failed}\n"
        f"• 👥 الإجمالي: {len(users)}",
        message.from_user.id,
        broadcast_msg.message_id,
        parse_mode='HTML'
    )

def process_add_subscription(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.from_user.id, "❌ صيغة غير صحيحة! استخدم: آيدي_المستخدم عدد_الأيام")
            return

        target_user_id = int(parts[0])
        days = int(parts[1])

        # التحقق من وجود المستخدم
        user = db.get_user(target_user_id)
        if not user:
            bot.send_message(message.from_user.id, "❌ المستخدم غير موجود!")
            return

        # إضافة العضوية
        success = db.update_subscription(target_user_id, days)

        if success:
            bot.send_message(
                message.from_user.id,
                f"✅ <b>تم تفعيل العضوية بنجاح!</b>\n\n"
                f"👤 المستخدم: {user[2]}\n"
                f"🆔 الآيدي: {target_user_id}\n"
                f"⏰ المدة: {days} يوم\n\n"
                f"📅 تنتهي العضوية في: {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='HTML',
                reply_markup=admin_panel()
            )

            # إرسال إشعار للمستخدم
            try:
                bot.send_message(
                    target_user_id,
                    f"🎉 <b>تم تفعيل عضوية جديدة لك!</b>\n\n"
                    f"⏰ المدة: {days} يوم\n"
                    f"📅 تنتهي في: {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"يمكنك الآن استخدام جميع ميزات البوت 🎯",
                    parse_mode='HTML',
                    reply_markup=main_menu(target_user_id)
                )
            except:
                pass
        else:
            bot.send_message(message.from_user.id, "❌ حدث خطأ أثناء تفعيل العضوية!")

    except ValueError:
        bot.send_message(message.from_user.id, "❌ يرجى إدخال أرقام صحيحة!")
    except Exception as e:
        bot.send_message(message.from_user.id, f"❌ حدث خطأ: {str(e)}")

# تشغيل البوت
print(f"{Colors.GREEN}بوت صيد حسابات Safeum يعمل بنجاح...{Colors.RESET}")
print(f"{Colors.YELLOW}المطور: @VIP_7_I{Colors.RESET}")

try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"{Colors.RED}خطأ في تشغيل البوت: {e}{Colors.RESET}")