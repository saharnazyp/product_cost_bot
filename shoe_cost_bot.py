import os
from bale import Bot, Message, MenuKeyboardMarkup, MenuKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# ───────────────── تعریف آیتم‌ها ─────────────────
# بخش ۱: مواد اولیه — (نام، لیست نوع‌ها)
MOAD_AVALIYE = [
    ("چرم رویه", ["فلوتر", "صافتی", "جیر", "نبوک", "اشوالت", "هورس", "پولیشی", "ناپا", "میلینگ"]),
    ("چرم آستری", ["گاوی", "بزی", "گوسفندی"]),
    ("زیره", ["ترمو", "لاستیک", "نیولایت", "میکرولایت", "پی‌یو", "چرم"]),
    ("کف ۲۵", ["تکسون", "اشتراول"]),
    ("قدک پشت و پنجه ۳۲", ["حرارتی", "تکنوژی", "بنزینی"]),
    ("انواع چسب", ["فرنگی", "کرپ", "پی‌یو", "دوغی"]),
    ("ابر", ["معمولی", "مموری فوم"]),
    ("خرجکار (میخ، منگنه، پرایمر، واکس، نخ و سایر)", []),
    ("یراق آلات", ["سگک", "منگنه", "سایر"]),
    ("بند", ["ایرانی", "خارجی"]),
    ("زیپ", []),
    ("گلچه", ["چسبی", "آماده"]),
    ("مدل‌سازی و قالب و ماهیچه", []),
    ("هزینه بسته‌بندی", []),
    ("ملزومات (قالب، تیغ، تخته پرس و سایر)", []),
    ("ضایعات", []),
]

# بخش ۲: دستمزد مستقیم (جفتی چند)
DASTMOZD = [
    "آستر بر", "لویس کار", "رومیزکار", "چرخکار",
    "دورنعلکی", "لفاف کن", "پرداخت‌چی", "کار جمع‌کن",
    "لیزر", "دوخت زیگزال", "حک مارک", "مدل‌گیر",
    "حسابدار", "کنترل کیفی", "کارفرما",
]

# بخش ۳: سایر هزینه‌ها (سهم هر جفت)
SAYER = [
    "اجاره", "تعمیرات و نگهداری ماشین‌آلات", "انرژی", "بیمه", "حمل و نقل و پیک",
    "خدمات پس از فروش", "آبدارخانه", "مالیات عملکرد",
]

# ساخت لیست تخت سوالات
QUESTIONS = []
for label, choices in MOAD_AVALIYE:
    multi = (label == "انواع چسب")  # فقط چسب چندانتخابی است
    QUESTIONS.append({"section": "mavad", "label": label, "choices": choices, "multi": multi})
for label in DASTMOZD:
    QUESTIONS.append({"section": "dastmozd", "label": label, "choices": [], "multi": False})
for label in SAYER:
    QUESTIONS.append({"section": "sayer", "label": label, "choices": [], "multi": False})

N_MAVAD = len(MOAD_AVALIYE)
N_DASTMOZD = len(DASTMOZD)
TOTAL_Q = len(QUESTIONS)

HEADERS = {
    "mavad": "🧵 مواد اولیه (مبلغ هر جفت)",
    "dastmozd": "👷 دستمزد مستقیم (جفتی چند)",
    "sayer": "🏭 سایر هزینه‌ها (سهم هر جفت)",
}

# متن راهنمای ورود مبلغ بر اساس بخش
PROMPT = {
    "mavad": "مبلغ هر جفت را به تومان وارد کنید:",
    "dastmozd": "جفتی چند؟ (کارمزد هر جفت به تومان):",
    "sayer": "سهم هر جفت را به تومان وارد کنید:",
}

sessions = {}  # chat_id -> {step, answers, types, profit, stage, await_type}


def fa_num(text):
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٬،", "0123456789,,")
    text = text.translate(trans).replace(",", "").replace(" ", "").strip()
    return float(text)


def fmt(x):
    return f"{int(round(x)):,}"


def section_prefix(step):
    section = QUESTIONS[step]["section"]
    prev = QUESTIONS[step - 1]["section"] if step > 0 else None
    if section != prev:
        return f"\n{HEADERS[section]}\n─────────────────\n"
    return ""


def make_keyboard(choices):
    kb = MenuKeyboardMarkup()
    row = 1
    for i, c in enumerate(choices):
        kb.add(MenuKeyboardButton(c), row)
        if i % 2 == 1:
            row += 1
    return kb


async def ask_question(message: Message, s):
    step = s["step"]
    q = QUESTIONS[step]
    prefix = section_prefix(step)
    num = f"({step + 1}/{TOTAL_Q})"

    if q["choices"]:
        s["await_type"] = True
        kb = make_keyboard(q["choices"])
        await message.reply(f"{prefix}{num} {q['label']}\nنوع را انتخاب کنید:", components=kb)
    else:
        s["await_type"] = False
        prompt = PROMPT[q["section"]]
        await message.reply(f"{prefix}{num} {q['label']}\n{prompt}")


@bot.event
async def on_before_ready():
    print("ربات آماده شد ✅")


@bot.event
async def on_message(message: Message):
    text = message.text
    if text is None:
        return
    text = text.strip()
    chat_id = message.chat.id

    if text in ("/start", "start", "شروع"):
        sessions[chat_id] = {
            "step": 0, "answers": [], "types": [],
            "profit": None, "stage": "items", "await_type": False,
        }
        await message.reply(
            "👞✨ ربات هوشمند محاسبه بهای تمام‌شده\n"
            "🏛️ تعاونی کفاشان دست‌دوز تهران | تأسیس ۱۳۴۸\n"
            "━━━━━━━━━━━━━━━━━\n"
            "به سامانه هوشمند محاسبه بهای تمام‌شده کفش دست‌دوز خوش آمدید. 🌟\n\n"
            "این ربات با اطلاعاتی که وارد می‌کنید، هزینه واقعی تولید هر جفت کفش را "
            "دقیق محاسبه کرده و حداقل قیمت فروش پیشنهادی را به شما می‌دهد.\n\n"
            "📌 با محاسبه صحیح بهای تمام‌شده می‌توانید:\n"
            "   ◾️ از زیان‌های پنهان جلوگیری کنید\n"
            "   ◾️ قیمت‌گذاری دقیق و حرفه‌ای داشته باشید\n"
            "   ◾️ سود واقعی کسب‌وکارتان را مدیریت کنید\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📝 نحوه ورود اطلاعات\n"
            "تمام مبالغ مربوط به «یک جفت کفش» هستند:\n\n"
            "🧵 مواد اولیه ← هزینه مواد مصرفی برای یک جفت\n"
            "👨🏻‍🔧 دستمزد ← کارمزد پرداختی برای تولید یک جفت\n"
            "🏭 سایر هزینه‌ها ← سهم هر جفت از اجاره، برق، استهلاک، حمل‌ونقل و…\n\n"
            "▫️ ابتدا نوع آیتم را از دکمه‌ها انتخاب کنید، سپس مبلغ را وارد نمایید.\n"
            "▫️ اگر هزینه‌ای ندارید، عدد ۰ را ارسال کنید.\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📊 در پایان، ربات این موارد را نمایش می‌دهد:\n"
            "   ✅ مجموع بهای تمام‌شده\n"
            "   ✅ قیمت فروش پیشنهادی\n"
            "   ✅ سود و حاشیه سود\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🚀 برای شروع، بزن بریم!"
        )
        await ask_question(message, sessions[chat_id])
        return

    if chat_id not in sessions:
        await message.reply("برای شروع محاسبه، دستور /start را بفرستید.")
        return

    s = sessions[chat_id]

    # ── مرحله انتخاب نوع (دکمه) ──
    if s["stage"] == "items" and s.get("await_type"):
        q = QUESTIONS[s["step"]]
        if text in q["choices"]:
            s["types"].append(text)
            s["await_type"] = False
            await message.reply(f"✅ نوع: {text}\nحالا مبلغ هر جفت این آیتم را به تومان وارد کنید:")
        else:
            await message.reply("لطفاً یکی از دکمه‌های نوع را انتخاب کنید.")
        return

    # ── خواندن عدد ──
    try:
        value = fa_num(text)
    except (ValueError, AttributeError):
        await message.reply("⚠️ لطفاً فقط عدد وارد کنید.")
        return

    if s["stage"] == "items":
        q = QUESTIONS[s["step"]]
        if not q["choices"]:
            s["types"].append("-")
        s["answers"].append(value)
        s["step"] += 1

        if s["step"] < TOTAL_Q:
            await ask_question(message, s)
        else:
            s["stage"] = "profit"
            await message.reply(
                "✅ همه‌ی هزینه‌ها وارد شد.\n\n"
                "حالا درصد سود کارگاه را وارد کنید (مثلاً برای ۲۰ درصد عدد 20):"
            )
        return

    if s["stage"] == "profit":
        s["profit"] = value
        await send_result(message, s)
        del sessions[chat_id]
        return


async def send_result(message: Message, s):
    ans = s["answers"]
    total_mavad = sum(ans[:N_MAVAD])
    total_dastmozd = sum(ans[N_MAVAD:N_MAVAD + N_DASTMOZD])
    total_sayer = sum(ans[N_MAVAD + N_DASTMOZD:])

    hoghoogh_va_sayer = total_dastmozd + total_sayer
    tamam_shode = total_mavad + hoghoogh_va_sayer
    profit_pct = s["profit"]
    sood = tamam_shode * profit_pct / 100
    forosh = tamam_shode + sood

    selected = []
    for i in range(N_MAVAD):
        t = s["types"][i] if i < len(s["types"]) else "-"
        if t and t != "-":
            selected.append(f"• {MOAD_AVALIYE[i][0]}: {t}")
    types_summary = ("\n".join(selected)) if selected else "—"

    text = (
        "📊 نتیجه‌ی محاسبه — بهای تمام‌شده‌ی یک جفت کفش\n"
        "═════════════════\n"
        f"🧵 جمع مواد اولیه: {fmt(total_mavad)} تومان\n"
        f"👷 جمع دستمزد: {fmt(total_dastmozd)} تومان\n"
        f"🏭 جمع سایر هزینه‌ها: {fmt(total_sayer)} تومان\n"
        f"➕ هزینه‌ی حقوق و سایر: {fmt(hoghoogh_va_sayer)} تومان\n"
        "─────────────────\n"
        f"💰 قیمت تمام‌شده: {fmt(tamam_shode)} تومان\n"
        f"📈 سود کارگاه ({int(profit_pct)}٪): {fmt(sood)} تومان\n"
        f"🏷️ قیمت فروش: {fmt(forosh)} تومان\n"
        "═════════════════\n\n"
        f"📝 نوع جنس‌های انتخاب‌شده:\n{types_summary}\n\n"
        "🔄 برای محاسبه‌ی مجدد /start را بزنید.\n"
        "🏛️ تعاونی کفاشان دست‌دوز تهران | تأسیس ۱۳۴۸"
    )
    await message.reply(text)


if __name__ == "__main__":
    bot.run()
