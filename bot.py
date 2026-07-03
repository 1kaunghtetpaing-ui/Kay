import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# အောက်က 'YOUR_BOT_TOKEN' နေရာမှာ အစ်ကို့ Bot Token ကို ထည့်ပါ
BOT_TOKEN = '8936459122:AAFXkdJlZqE5UxwnQOUh-MwBxQ50HAxBl2A'
ADMIN_ID = 5984517116
CHANNEL_USERNAME = '@kyii_mall'  # Channel ရဲ့ username

bot = telebot.TeleBot(BOT_TOKEN)

# User တွေရဲ့ request တွေကို မှတ်ထားဖို့ (Admin video ပို့ချိန် ID တောင်းဖို့)
admin_states = {}

def check_membership(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        show_main_menu(message.chat.id)
    else:
        markup = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton("Channel ကို Join ပါ", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        check_btn = InlineKeyboardButton("JOIN ပြီးပါပြီ", callback_data="check_join")
        markup.add(join_btn)
        markup.add(check_btn)
        bot.send_message(message.chat.id, "Welcome! ကျေးဇူးပြု၍ အောက်ပါ Channel ကို အရင် Join ပေးပါ။", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "Channel ကို မ Join ရသေးပါ။ ကျေးဇူးပြု၍ Join ပေးပါ။", show_alert=True)

def show_main_menu(chat_id):
    text = ("movie တောင်းချင်ရင် /moviename Toystory-3 ဒီလိုရေးပြီးတောင်းပေးပါ။\n"
            "နာမည်မသိရင် /moviepic လို့ရိုက်ပြီးပုံတင်ပေးပါ")
    bot.send_message(chat_id, text)

@bot.message_handler(content_types=['text', 'photo'])
def handle_user_requests(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Admin က Video forward လာပြီး User ID ရိုက်ထည့်တဲ့ အချိန်
    if user_id == ADMIN_ID and user_id in admin_states:
        target_user_id = message.text.strip()
        video_message_id = admin_states[user_id]
        try:
            bot.forward_message(target_user_id, ADMIN_ID, video_message_id)
            bot.send_message(ADMIN_ID, f"✅ User {target_user_id} ထံသို့ Video ပို့ပြီးပါပြီ။")
            del admin_states[user_id]
        except Exception as e:
            bot.send_message(ADMIN_ID, "❌ အမှားအယွင်းဖြစ်နေပါတယ်။ User ID မှားနေတာ ဖြစ်နိုင်ပါတယ်။")
        return

    # Admin ကလွဲပြီး ကျန်တဲ့ User တွေအတွက်
    if user_id != ADMIN_ID:
        if not check_membership(user_id):
            bot.send_message(chat_id, "ကျေးဇူးပြု၍ Channel ကို အရင် Join ပါ။ /start ကို ပြန်နှိပ်ပါ။")
            return

        text = message.text or message.caption
        
        if text and text.startswith('/moviename'):
            bot.send_message(ADMIN_ID, f"🎬 Movie Request:\n{text}\n\n👤 User ID: `{user_id}`", parse_mode='Markdown')
            bot.send_message(chat_id, "✅ Admin ထံသို့ တောင်းဆိုချက် ပို့ပြီးပါပြီ။")
        
        elif message.photo and text and text.startswith('/moviepic'):
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📸 Photo Request:\n{text}\n\n👤 User ID: `{user_id}`", parse_mode='Markdown')
            bot.send_message(chat_id, "✅ Admin ထံသို့ ပုံဖြင့် တောင်းဆိုချက် ပို့ပြီးပါပြီ။")
        else:
            bot.send_message(chat_id, "❌ မှားယွင်းနေပါတယ်။ /moviename သို့မဟုတ် /moviepic ကိုသာ အသုံးပြုပါ။")

@bot.message_handler(content_types=['video', 'document'], func=lambda message: message.from_user.id == ADMIN_ID)
def handle_admin_video(message):
    # Admin က Video ပို့/Forward လုပ်တဲ့အခါ
    admin_states[ADMIN_ID] = message.message_id
    bot.reply_to(message, "လက်ခံရရှိမည့် User ၏ ID ကို ရိုက်ထည့်ပေးပါ။")

bot.polling(none_stop=True)