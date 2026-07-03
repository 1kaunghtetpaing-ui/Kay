import telebot
from telebot import types

# ====================== ဖြည့်စွက်ရန် ======================
API_TOKEN = '8936459122:AAFXkdJlZqE5UxwnQOUh-MwBxQ50HAxBl2A'
CHANNEL_ID = '@kyii_mall'   # ဥပမာ: @mymoviechannel
ADMIN_ID = 5984517116                     # သင့် Telegram ID
# =========================================================

bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

# Admin state သိမ်းရန်
admin_state = {}

# ==================== Helper Functions ====================
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        print(f"Channel check error: {e}")
        return False


def send_join_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_link = types.InlineKeyboardButton("🔗 Join Channel", 
                                        url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
    btn_check = types.InlineKeyboardButton("✅ I've Joined", callback_data="check_joined")
    markup.add(btn_link, btn_check)

    bot.send_message(chat_id, 
        "👋 <b>Welcome!</b>\n\n"
        "Bot ကို အသုံးပြုဖို့ ကျွန်တော်တို့ Channel ကို ပထမ ပါဝင်ပေးပါ။",
        reply_markup=markup)


def send_welcome_instructions(chat_id):
    text = (
        "✅ <b>မှန်ကန်စွာ ပါဝင်ပြီးပါပြီ!</b>\n\n"
        "အောက်ပါ command များကို အသုံးပြုနိုင်ပါပြီ :\n\n"
        "🎬 <code>/movie_name ရုပ်ရှင်အမည်</code>\n"
        "🖼 <code>/reference_picture</code> + ပုံတစ်ပုံ (Caption မှာ)\n\n"
        "<i>ဥပမာ : /movie_name Avatar 2</i>"
    )
    bot.send_message(chat_id, text)


# ====================== Commands ======================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🛠 <b>Admin Panel</b>\n\nBot is running normally.")
        return
        
    if is_user_joined(user_id):
        send_welcome_instructions(message.chat.id)
    else:
        send_join_markup(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def callback_check_joined(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if is_user_joined(user_id):
        bot.answer_callback_query(call.id, "🎉 Thank you for joining!")
        bot.delete_message(chat_id, call.message.message_id)
        send_welcome_instructions(chat_id)
    else:
        bot.answer_callback_query(call.id, "❌ မပါဝင်သေးပါဘူး။ Channel ပါဝင်ပြီး ပြန်နှိပ်ပါ။", 
                                show_alert=True)


# ====================== User Text Handler ======================
@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID, content_types=['text'])
def handle_user_text(message):
    user_id = message.from_user.id
    
    if not is_user_joined(user_id):
        send_join_markup(message.chat.id)
        return

    if message.text.startswith('/movie_name'):
        forward_text = f"<b>🎬 New Movie Request</b>\n\n{message.text}\n\n👤 User: <code>{user_id}</code>"
        bot.send_message(ADMIN_ID, forward_text)
        bot.reply_to(message, "✅ သင့်တောင်းဆိုမှုကို Admin ထံ ပို့ပြီးပါပြီ။ စောင့်ပါ။")
    else:
        bot.reply_to(message, "❌ မှားယွင်းနေပါတယ်။\n\n<code>/movie_name ရုပ်ရှင်အမည်</code> ပုံစံနဲ့ ရိုက်ပါ။")


# ====================== User Photo Handler ======================
@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID, content_types=['photo'])
def handle_user_photo(message):
    user_id = message.from_user.id
    
    if not is_user_joined(user_id):
        send_join_markup(message.chat.id)
        return

    if message.caption and message.caption.startswith('/reference_picture'):
        forward_text = f"<b>🖼 New Reference Picture</b>\n\n👤 User: <code>{user_id}</code>"
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=forward_text)
        bot.reply_to(message, "✅ Reference ပုံကို Admin ထံ ပို့ပြီးပါပြီ။")
    else:
        bot.reply_to(message, "❌ ပုံနဲ့အတူ <code>/reference_picture</code> လို့ Caption ရေးပေးပါ။")


# ====================== Polling ======================
print("Bot is running...")
bot.infinity_polling()
