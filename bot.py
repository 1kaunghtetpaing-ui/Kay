import telebot
from telebot import types
import os
import json
from datetime import datetime

# ================= CONFIG (မဖြစ်မနေ ဖြည့်ပေးပါ) =================
BOT_TOKEN = "8936459122:AAFXkdJlZqE5UxwnQOUh-MwBxQ50HAxBl2A"   
ADMIN_ID = 5984517116  # ← မင်းရဲ့ Telegram User ID ကို ဒီမှာ ပြောင်းထည့်ပါ
CHANNEL_USERNAME = "@kyii_mall"     # Custom Link သုံးရင်လည်း username ကို ဒီမှာ စစ်ဖို့ ထည့်ရပါတယ်

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATA STORAGE (JSON FILE) =================
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "vip_codes": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# VIP Code စနစ်အတွက် Admin ရဲ့ ယာယီအခြေအနေကို သိမ်းရန်
admin_state = {}

# ================= HELPER FUNCTIONS =================

# Channel Join/Not Join စစ်ဆေးခြင်း
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Channel Check Error: {e}")
        return False

# User တစ်ယောက်ရဲ့ နေ့စဉ်အသုံးပြုခွင့်ကို စစ်ဆေး/နုတ်ခြင်း
def check_and_use_limit(user_id):
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    user_id_str = str(user_id)
    
    if user_id_str not in data["users"]:
        data["users"][user_id_str] = {"last_used_date": today, "free_limit": 1, "vip_balance": 0}
    
    user = data["users"][user_id_str]
    
    # ရက်အသစ်ဖြစ်သွားရင် နေ့စဉ် Free 1 ကြိမ် ပြန်ပေးမယ်
    if user["last_used_date"] != today:
        user["last_used_date"] = today
        user["free_limit"] = 1
        
    # အလှည့်ကျ စစ်ဆေးမယ်
    if user["free_limit"] > 0:
        user["free_limit"] -= 1
        save_data(data)
        return True, "free"
    elif user["vip_balance"] > 0:
        user["vip_balance"] -= 1
        save_data(data)
        return True, f"vip ({user['vip_balance']} times left)"
        
    return False, None

# ================= COMMAND HANDLERS =================

# /start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # Welcome message & Channel Link + I've Joined Button
    markup = types.InlineKeyboardMarkup()
    btn_link = types.InlineKeyboardButton("📢 Channel ကို Join ရန်", url="https://t.me/kyii_mall")
    btn_joined = types.InlineKeyboardButton("✅ I've Joined (မန်ဘာဝင်ပြီးပါပြီ)", callback_data="check_joined")
    markup.add(btn_link)
    markup.add(btn_joined)
    
    bot.send_message(
        message.chat.id, 
        "👋 Welcome! ကျွန်တော်တို့ရဲ့ Bot မှ ကြိုဆိုပါတယ်။\n\nရှေ့ဆက်သွားဖို့အတွက် အောက်ကလင့်ခ်မှာ Channel ကို အရင် Join ပေးပါ။", 
        reply_markup=markup
    )

# Callback Query Handler (I've Joined ခလုတ်နှိပ်ရင် စစ်မယ့်အပိုင်း)
@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def check_joined_callback(call):
    user_id = call.from_user.id
    
    if is_user_joined(user_id):
        # အမှန်တကယ် Join ပြီးမှ ပြမယ့်စာ
        instructions = (
            "🎉 ကျေးဇူးတင်ပါတယ်။ Channel Join မှု အောင်မြင်ပါတယ်။\n\n"
            "If u want to search a movies, u can use /zatcar this Tag, U don't know name use /zatcarpic for picture search.\n\n"
            "👇 အသုံးပြုနိုင်မယ့် Tag များ -\n"
            "/zatcar\n"
            "/zatcarpic"
        )
        bot.edit_message_text(instructions, chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        # မ Join ရသေးရင် ခလုတ်ပြန်ပြမယ်
        bot.answer_callback_query(call.id, "❗ သင် Channel ကို မ Join ရသေးပါ။", show_alert=True)
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("📢 Channel ကို Join ရန်", url="https://t.me/kyii_mall")
        btn_joined = types.InlineKeyboardButton("✅ I've Joined (မန်ဘာဝင်ပြီးပါပြီ)", callback_data="check_joined")
        markup.add(btn_link)
        markup.add(btn_joined)
        
        # စာကို ပြန်ပြင်ပြီး သတိပေးမယ်
        bot.edit_message_text("❗ Channel ကို မ Join ရသေးပါ။ အရင် Join ပြီးမှ I've Joined ကို နှိပ်ပါ။", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

# ================= USER REQUESTS & ADMIN RECEIVE =================

# 1. စာဖြင့်ရှာခြင်း: /zatcar *စာထည့်
@bot.message_handler(commands=['zatcar'])
def handle_zatcar(message):
    user_id = message.from_user.id
    if not is_user_joined(user_id): return
    
    # နေ့စဉ် Limit စစ်ဆေးခြင်း
    allowed, mode = check_and_use_limit(user_id)
    if not allowed:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👨‍💻 Contact Admin (VIP ဝယ်ရန်)", url="https://t.me/kyii_mall")) # ⚠️ မင်းရဲ့ Contact Link ပြောင်းပါ
        bot.reply_to(message, "⚠️ သင်၏ ယနေ့အတွက် Free ၁ ကြိမ် ရှာဖွေခွင့် ကုန်ဆုံးသွားပါပြီ။\nဆက်လက်သုံးစွဲလိုပါက VIP Code ထည့်သွင်းပါ သို့မဟုတ် Admin ကို ဆက်သွယ်ပါ။", reply_markup=markup)
        return

    try:
        search_text = message.text.split(maxsplit=1)[1]
        # Admin ဆီ ပို့ခြင်း
        bot.send_message(ADMIN_ID, f"🎥 **New Movie Request (Text)**\n\nUser ရေးလိုက်သည့်စာ:\n`{search_text}`\n\n👤 User ID: `{user_id}`", parse_mode="Markdown")
        bot.reply_to(message, f"✅ တောင်းဆိုမှု အောင်မြင်သည်။ အုပ်ချုပ်သူ (Admin) ထံ ပို့ဆောင်ပြီးပါပြီ။\n(Status: Used {mode} search)")
    except IndexError:
        bot.reply_to(message, "⚠️ စာသား ထည့်သွင်းရန် လိုအပ်ပါသည်။ ဥပမာ - `/zatcar kft`", parse_mode="Markdown")

# 2. ပုံဖြင့်ရှာခြင်း: /zatcarpic *ပုံတင်
@bot.message_handler(commands=['zatcarpic'])
def handle_zatcarpic(message):
    user_id = message.from_user.id
    if not is_user_joined(user_id): return
    
    # ပုံနဲ့အတူ caption မှာ တွဲမပို့ရင် ငြင်းမယ်
    bot.reply_to(message, "⚠️ ပုံဖြင့် ရှာဖွေရန်အတွက် ပုံကို အရင်ရွေးချယ်ပြီး **Add a caption** နေရာတွင် `/zatcarpic` ဟု ရေးသား၍ ပို့ပေးပါ။")

# ပုံကို /zatcarpic tag နဲ့ တွဲတင်တာကို ဖမ်းမယ့် handler
@bot.message_handler(content_types=['photo'])
def handle_photo_request(message):
    user_id = message.from_user.id
    if not is_user_joined(user_id): return
    
    caption = message.caption if message.caption else ""
    
    if caption.strip() == "/zatcarpic":
        allowed, mode = check_and_use_limit(user_id)
        if not allowed:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("👨‍💻 Contact Admin", url="https://t.me/kyii_mall"))
            bot.reply_to(message, "⚠️ သင်၏ ယနေ့အတွက် Free ၁ ကြိမ် ရှာဖွေခွင့် ကုန်ဆုံးသွားပါပြီ။ VIP Code သုံးပါ။", reply_markup=markup)
            return
            
        file_id = message.photo[-1].file_id
        # Admin ဆီ ပုံရော ID ပါ ပို့မယ်
        bot.send_photo(ADMIN_ID, file_id, caption=f"📸 **New Movie Request (Image)**\n\n👤 User ID: `{user_id}`", parse_mode="Markdown")
        bot.reply_to(message, f"✅ ပုံဖြင့် တောင်းဆိုမှု အောင်မြင်သည်။ Admin ထံ ပို့ထားပြီးပါပြီ။\n(Status: Used {mode} search)")
    else:
        # Tag မပါရင် Denied လုပ်မယ်
        bot.reply_to(message, "❌ Access Denied: Tag မပါဘဲ ပို့ခြင်းကို လက်မခံပါ။ စာဆို `/zatcar စာ`၊ ပုံဆိုရင် `/zatcarpic` လို့ Caption မှာ ရေးပြီး ပို့ပါ။")

# Tag မပါတဲ့ တခြားစာတွေ ပို့ရင် Denied လုပ်မယ်
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID and not message.text.startswith('/'))
def deny_other_messages(message):
    bot.reply_to(message, "❌ Access Denied: Tag မပါဘဲ ပို့ခြင်းကို လက်မခံပါ။ စာဆို `/zatcar စာ`၊ ပုံဆိုရင် `/zatcarpic` လို့ ရေးပြီး ပို့ပါ။")


# ================= ADMIN VIP CODE SETTING =================

# Admin က /vip လို့ ပို့ရင် စကုဒ်တောင်းမယ်
@bot.message_handler(commands=['vip'], func=lambda m: m.from_user.id == ADMIN_ID)
def admin_vip_start(message):
    admin_state[message.from_user.id] = "waiting_for_code"
    bot.reply_to(message, "ℹ️ Set code please (ကုဒ်နှင့် အကြိမ်ရေကို ပုံစံအတိုင်း ပို့ပေးပါ)\neg., `XCRH-3times,CBJO-5times,BFDI-10times`", parse_mode="Markdown")

# Admin ပို့လိုက်တဲ့ VIP စာရင်းကို သိမ်းဆည်းခြင်း
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and admin_state.get(m.from_user.id) == "waiting_for_code")
def admin_vip_save(message):
    raw_text = message.text.strip()
    data = load_data()
    
    try:
        # XCRH-3times,CBJO-5times စာသားကို ခွဲထုတ်မယ်
        pairs = raw_text.split(",")
        added_count = 0
        
        for pair in pairs:
            if "-" in pair:
                code, limit_str = pair.split("-")
                code = code.strip()
                # times ဆိုတဲ့ စာသားကို ဖယ်ပြီး ဂဏန်းသီးသန့် ယူမယ်
                limit = int(limit_str.lower().replace("times", "").replace("time", "").strip())
                
                data["vip_codes"][code] = limit
                added_count += 1
                
        save_data(data)
        admin_state[message.from_user.id] = None # State ကို ပြန်ဖျက်မယ်
        bot.reply_to(message, f"✅ VIP Codes {added_count} ခုကို Bot ထဲမှာ အောင်မြင်စွာ သိမ်းဆည်းလိုက်ပါပြီ။")
    except Exception as e:
        bot.reply_to(message, f"⚠️ ပုံစံ မှားယွင်းနေပါတယ်။ ပြန်လည် စစ်ဆေးပါ။ Error: {e}")

# User က VIP Code လာထည့်တဲ့ စနစ် (ကုဒ် သီးသန့် ရိုက်ပို့ရုံပဲ)
@bot.message_handler(func=lambda m: not m.text.startswith('/') and m.from_user.id != ADMIN_ID)
def check_user_vip_code(message):
    if not is_user_joined(message.from_user.id): return
    
    user_code = message.text.strip()
    data = load_data()
    
    # မရိုက်ခင် စစ်ဆေးမယ်၊ ကုဒ် မှန်ရင်
    if user_code in data["vip_codes"]:
        bonus_times = data["vip_codes"][user_code]
        user_id_str = str(message.from_user.id)
        
        if user_id_str not in data["users"]:
            data["users"][user_id_str] = {"last_used_date": datetime.now().strftime("%Y-%m-%d"), "free_limit": 1, "vip_balance": 0}
            
        # အကြိမ်ရေ ပေါင်းထည့်ပြီး သုံးပြီးသားကုဒ် ဖျက်မယ်
        data["users"][user_id_str]["vip_balance"] += bonus_times
        del data["vip_codes"][user_code]
        
        save_data(data)
        bot.reply_to(message, f"🎉 VIP Code အောင်မြင်ပါတယ်။ သင်ရှာဖွေနိုင်သည့် အကြိမ်ရေ +{bonus_times} ကြိမ် ထပ်တိုးပေးလိုက်ပါပြီ။")
    else:
        # အပေါ်က ကိစ္စတွေနဲ့ မဆိုင်ရင် Denied လုပ်မယ်
        bot.reply_to(message, "❌ ကုဒ် မှားယွင်းနေပါသည် သို့မဟုတ် သက်တမ်းကုန်သွားပါပြီ။ Tag မပါတဲ့ တခြားစာတွေကို ပို့ခွင့်မရှိပါ။")


# ================= ADMIN VIDEO FORWARD SYSTEM =================

# Admin က ဗီဒီယို ဖော်ဝပ် လုပ်လာရင် 
@bot.message_handler(content_types=['video'], func=lambda m: m.from_user.id == ADMIN_ID)
def handle_admin_video_forward(message):
    admin_state[message.from_user.id] = {"state": "waiting_for_userid", "video_message_id": message.message_id, "from_chat_id": message.chat.id}
    bot.reply_to(message, "🆔 ဗီဒီယို ရောက်ရှိပါသည်။ ပို့ပေးရမည့် **User ID** ကို ရိုက်ပို့ပေးပါ။")

# Admin ဆီက User ID စောင့်ပြီး တိုက်ရိုက် Forward ပို့ပေးခြင်း
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and isinstance(admin_state.get(m.from_user.id), dict) and admin_state[m.from_user.id].get("state") == "waiting_for_userid")
def handle_admin_giving_userid(message):
    target_user_id = message.text.strip()
    admin_info = admin_state[message.from_user.id]
    
    try:
        # Admin ပေးတဲ့ ID ဆီကို ဗီဒီယို Forward လုပ်မယ်
        bot.forward_message(
            chat_id=int(target_user_id),
            from_chat_id=admin_info["from_chat_id"],
            message_id=admin_info["video_message_id"]
        )
        bot.reply_to(message, f"🚀 ဗီဒီယိုကို User ID: `{target_user_id}` ဆီသို့ အောင်မြင်စွာ Forward ပြုလုပ်ပေးလိုက်ပါပြီ။", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ ဗီဒီယို ပို့လို့မရပါ။ ထို User က Bot ကို Block ထားခြင်း သို့မဟုတ် User ID မှားယွင်းနေခြင်း ဖြစ်နိုင်ပါသည်။\nError: {e}")
        
    # အခြေအနေကို ရှင်းလင်းမယ်
    admin_state[message.from_user.id] = None

# ================= RUN BOT =================
if __name__ == '__main__':
    print("Bot is successfully running with VIP & Forward system...")
    bot.infinity_polling()
    if message.caption and message.caption.startswith('/reference_picture'):
        forward_text = f"<b>🖼 New Reference Picture</b>\n\n👤 User: <code>{user_id}</code>"
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=forward_text)
        bot.reply_to(message, "✅ Reference ပုံကို Admin ထံ ပို့ပြီးပါပြီ။")
    else:
        bot.reply_to(message, "❌ ပုံနဲ့အတူ <code>/reference_picture</code> လို့ Caption ရေးပေးပါ။")


# ====================== Polling ======================
print("Bot is running...")
bot.infinity_polling()
