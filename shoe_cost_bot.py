import os
from bale import Bot, Message, MenuKeyboardMarkup, MenuKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# ───────────────── تعریف آیتم‌ها ─────────────────
# هر آیتم: (بخش، نام آیتم، لیست نوع‌ها برای دکمه)
# اگر لیست نوع‌ها خالی باشد یعنی فقط مبلغ تایپ می‌شود.

# بخش ۱: مواد اولیه (E3:E18)
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
    ("کلوچه", ["چسبی", "آماده"]),
    ("مدل‌سازی و قالب و ماهیچه", []),
    ("هزینه بسته‌بندی", []),
    ("ملزومات (قالب، تیغ، تخته پرس و سایر)", []),
    ("ضایعات", []),
]

# بخش ۲: دستمزد مستقیم (فقط مبلغ)
DASTMOZD = [
    "آستر بر", "لویس کار", "رومیزکار", "چرخکار",
    "دورنعلکی", "لفاف کن", "پرداخت‌چی", "کار جمع‌کن",
    "لیزر", "دوخت زیگزال", "حک مارک", "مدل‌گیر",
    "حسابدار", "کنترل کیفی", "کارفرما",
]

# بخش ۳: سایر هزینه‌ها (فقط مبلغ)
SAYER = [
    "اجاره", "تعمیرات و نگهداری ماشین‌آلات", "انرژی", "بیمه", "حمل و نقل و پیک",
    "خدمات پس از فروش", "آبدارخانه", "مالیات عملکرد",
]

# ساخت لیست تخت سوالات: هر عنصر دیکشنری با کلیدهای section, label, choices
QUESTIONS = []
for label, choices in MOAD_AVALIYE:
    QUESTIONS.append({"section": "mavad", "label": label, "choices": choices})
for label in DASTMOZD:
    QUESTIONS.append({"section": "dastmozd", "label": label, "choices": []})
for label in SAYER:
    QUESTIONS.append({"section": "sayer", "label": label, "choices": []})

N_MAVAD = len(MOAD_AVALIYE)
N_DASTMOZD = len(DASTMOZD)
TOTAL_Q = len(QUESTIONS)

HEADERS = {
    "mavad": "🧵 مواد اولیه",
    "dastmozd": "👷 دستمزد مستقیم",
    "sayer": "🏭 سایر هزینه‌ها",
}

# وضعیت هر کاربر
# chat_id -> {step, answers:[], types:[], profit, stage, await_type:bool}
sessions = {}


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
    """ساخت کیبورد دکمه‌ای از روی لیست نوع‌ها، دو دکمه در هر ردیف."""
    kb = MenuKeyboardMarkup()
    row = 1
    for i, c in enumerate(choices):
        kb.add(MenuKeyboardButton(c), row)
        if i % 2 == 1:
            row += 1
    return kb


async def ask_question(message: Message, s):
    """پرسیدن سوال فعلی؛ اگر نوع دارد اول دکمه‌ها را نشان می‌دهد."""
    step = s["step"]
    q = QUESTIONS[step]
    prefix = section_prefix(step)
    num = f"({step + 1}/{TOTAL_Q})"

    if q["choices"]:
        # مرحله انتخاب نوع با دکمه
        s["await_type"] = True
        kb = make_keyboard(q["choices"])
        await message.reply(
            f"{prefix}{num} {q['label']}\nنوع را انتخاب کنید:",
            components=kb,
        )
    else:
        # مستقیم مبلغ
        s["await_type"] = False
        await message.reply(f"{prefix}{num} {q['label']} :\nمبلغ را به تومان وارد کنید:")


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

    # شروع / ریست
    if text in ("/start", "start", "شروع"):
        sessions[chat_id] = {
            "step": 0, "answers": [], "types": [],
            "profit": None, "stage": "items", "await_type": False,
        }
        await message.reply(
            "👞 ربات محاسبه‌ی بهای تمام‌شده‌ی یک جفت کفش دست‌دوز\n\n"
            "برای آیتم‌هایی که نوع دارند، اول نوع را با دکمه انتخاب می‌کنید،\n"
            "سپس مبلغ آن را برای یک جفت کفش وارد می‌کنید.\n"
            "اگر آیتمی ندارید عدد ۰ را بفرستید.\n"
            "برای شروع مجدد هر زمان /start را بزنید.\n"
            "─────────────────"
        )
        s = sessions[chat_id]
        await ask_question(message, s)
        return

    if chat_id not in sessions:
        await message.reply("برای شروع محاسبه، دستور /start را بفرستید.")
        return

    s = sessions[chat_id]

    # ── مرحله انتخاب نوع (دکمه) ──
    if s["stage"] == "items" and s.get("await_type"):
        q = QUESTIONS[s["step"]]
        # متن دکمه باید جزو نوع‌ها باشد
        if text in q["choices"]:
            s["types"].append(text)
            s["await_type"] = False
            await message.reply(
                f"✅ نوع انتخاب‌شده: {text}\nحالا مبلغ این آیتم را به تومان وارد کنید:"
            )
        else:
            await message.reply("لطفاً یکی از دکمه‌های نوع را انتخاب کنید.")
        return

    # ── خواندن عدد (مبلغ یا درصد سود) ──
    try:
        value = fa_num(text)
    except (ValueError, AttributeError):
        await message.reply("⚠️ لطفاً فقط عدد وارد کنید.")
        return

    if s["stage"] == "items":
        q = QUESTIONS[s["step"]]
        # اگر این آیتم نوع نداشت، یک placeholder در types بگذار
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

    # خلاصه نوع جنس‌های انتخاب‌شده برای مواد اولیه
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
        f"👷 جمع حقوق و دستمزد: {fmt(total_dastmozd)} تومان\n"
        f"🏭 جمع سایر هزینه‌ها: {fmt(total_sayer)} تومان\n"
        f"➕ هزینه‌ی حقوق و سایر: {fmt(hoghoogh_va_sayer)} تومان\n"
        "─────────────────\n"
        f"💰 قیمت تمام‌شده: {fmt(tamam_shode)} تومان\n"
        f"📈 سود کارگاه ({int(profit_pct)}٪): {fmt(sood)} تومان\n"
        f"🏷️ قیمت فروش: {fmt(forosh)} تومان\n"
        "═════════════════\n\n"
        f"📝 نوع جنس‌های انتخاب‌شده:\n{types_summary}\n\n"
        "برای محاسبه‌ی مجدد /start را بزنید."
    )
    # حذف کیبورد دکمه‌ای در پیام نتیجه
    await message.reply(text)


if __name__ == "__main__":
    bot.run()
