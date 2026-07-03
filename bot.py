import telebot
from telebot import types

# ================= CONFIG =================
BOT_TOKEN = "8936459122:AAFXkdJlZqE5UxwnQOUh-MwBxQ50HAxBl2A"   # ← ဒီမှာ မင်း bot token ထည့်ပါ
CHANNEL_USERNAME = "@kyii_mall"     # Force Subscribe လုပ်မယ့် channel

bot = telebot.TeleBot(BOT_TOKEN)

# Check if user joined the channel
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    if not is_user_joined(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Channel ကို Join လုပ်ပါ", url=f"https://t.me/kyii_mall"))
        bot.reply_to(message, "❗ Movie ရယူဖို့ ဦးစွာ ကျွန်တော်ရဲ့ Channel ကို Join လုပ်ပေးပါ။\n\nJoin ပြီးရင် /start ကို ပြန်နှိပ်ပါ။", reply_markup=markup)
        return
    
    bot.reply_to(message, "✅ Welcome! ရှာချင်တဲ့ movie နာမည်ကို ရိုက်ပေးပါ\nဥပမာ: `/moviename kft`", parse_mode='Markdown')

# Movie Request Handler
@bot.message_handler(commands=['moviename'])
def movie_request(message):
    if not is_user_joined(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/kyii_mall"))
        bot.reply_to(message, "❗ ကျေးဇူးပြု၍ Channel ကို ဦးစွာ Join လုပ်ပေးပါ။", reply_markup=markup)
        return
    
    try:
        movie_name = message.text.split(maxsplit=1)[1]
        bot.reply_to(message, f"🎥 **Movie Request:**\n`/moviename {movie_name}`\n\nUser ID: `{message.from_user.id}`", parse_mode='Markdown')
        # ဒီမှာ မင်း movie ရှာပြီး ပို့ပေးတဲ့ code ကို ဆက်ထည့်နိုင်ပါတယ်
    except:
        bot.reply_to(message, "⚠️ နာမည်မှားနေပါတယ်။ ဥပမာ: `/moviename kft`")

print("Bot is running...")
bot.infinity_polling()
