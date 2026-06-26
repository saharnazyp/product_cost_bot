import os
from bale import Bot, Message

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # توکن از متغیر محیطی Railway خوانده می‌شود

bot = Bot(token=BOT_TOKEN)

# ───────────────── تعریف آیتم‌ها بر اساس فایل اکسل ─────────────────

# بخش ۱: مواد اولیه (E3:E18)
MOAD_AVALIYE = [
    "چرم رویه (فلوتر/صافتی/جیر/نبوک/اشوالت)",
    "چرم آستری (گاوی/بزی/گوسفندی)",
    "زیره (ترمو/لاستیک/نیولایت/چرم/پی‌یو)",
    "کف ۲۵ (تکسون/اشتراول)",
    "قدک پشت و پنجه ۳۲ (حرارتی/تکنوژی/بنزینی)",
    "انواع چسب (فرنگی/کرپ/پی‌یو/دوغی)",
    "ابر (معمولی/مموری فوم)",
    "خرجکار (میخ، منگنه، پرایمر، سمباده، واکس، پولیش، نخ، سوزن و سایر)",
    "یراق آلات (سگک/منگنه و سایر)",
    "بند",
    "زیپ",
    "کلوچه (چسبی/آماده)",
    "مدل‌سازی و قالب و ماهیچه (هزینه‌های تکی)",
    "هزینه بسته‌بندی (جعبه/کارتن مادر/نایلکس/سلفون/پاشنه‌کش)",
    "ملزومات (قالب/تیغ/تخته پرس/آلومنیوم پرس/تیغ لویس)",
    "ضایعات (چرم/آستر/زیره و سایر)",
]

# بخش ۲: دستمزد مستقیم
DASTMOZD = [
    "آستر بر", "لویس کار", "رومیزکار", "چرخکار",
    "دورنعلکی", "لفاف کن", "پرداخت‌چی", "کار جمع‌کن",
    "لیزر", "دوخت زیگزال", "حک مارک", "مدل‌گیر",
    "حسابدار", "کنترل کیفی", "کارفرما",
]

# بخش ۳: سایر هزینه‌ها
SAYER = [
    "اجاره", "تعمیرات و نگهداری ماشین‌آلات", "انرژی", "بیمه", "حمل و نقل و پیک",
    "خدمات پس از فروش", "آبدارخانه", "مالیات عملکرد",
]

# لیست تخت همه‌ی پرسش‌ها به ترتیب: (بخش، عنوان)
QUESTIONS = (
    [("mavad", x) for x in MOAD_AVALIYE]
    + [("dastmozd", x) for x in DASTMOZD]
    + [("sayer", x) for x in SAYER]
)

N_MAVAD = len(MOAD_AVALIYE)
N_DASTMOZD = len(DASTMOZD)

# نگهداری وضعیت هر کاربر بر اساس chat_id
sessions = {}  # chat_id -> {"step": int, "answers": [], "profit": None, "stage": str}

HEADERS = {
    "mavad": "🧵 مواد اولیه",
    "dastmozd": "👷 دستمزد مستقیم",
    "sayer": "🏭 سایر هزینه‌ها",
}


def fa_num(text):
    """تبدیل ارقام فارسی به انگلیسی و خواندن عدد"""
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٬،", "0123456789,,")
    text = text.translate(trans).replace(",", "").replace(" ", "").strip()
    return float(text)


def fmt(x):
    return f"{int(round(x)):,}"


@bot.event
async def on_before_ready():
    print("ربات آماده شد ✅")


def question_text(step):
    section, label = QUESTIONS[step]
    prev_section = QUESTIONS[step - 1][0] if step > 0 else None
    prefix = ""
    if section != prev_section:
        prefix = f"\n{HEADERS[section]}\n─────────────────\n"
    return f"{prefix}({step + 1}/{len(QUESTIONS)}) {label} :"


@bot.event
async def on_message(message: Message):
    text = message.text
    if text is None:
        return

    chat_id = message.chat.id

    # شروع / ریست
    if text.strip() in ("/start", "start", "شروع"):
        sessions[chat_id] = {"step": 0, "answers": [], "profit": None, "stage": "items"}
        await message.reply(
            "👞 ربات محاسبه‌ی بهای تمام‌شده‌ی یک جفت کفش دست‌دوز\n\n"
            "برای هر آیتم، هزینه‌ی آن برای یک جفت کفش را به تومان وارد کنید.\n"
            "اگر آیتمی ندارید عدد ۰ را بفرستید.\n"
            "برای شروع مجدد هر زمان /start را بزنید.\n"
            "─────────────────"
        )
        await message.reply(question_text(0))
        return

    # اگر کاربر بدون /start پیام داد
    if chat_id not in sessions:
        await message.reply("برای شروع محاسبه، دستور /start را بفرستید.")
        return

    s = sessions[chat_id]

    # خواندن عدد
    try:
        value = fa_num(text)
    except (ValueError, AttributeError):
        await message.reply("⚠️ لطفاً فقط عدد وارد کنید.")
        return

    if s["stage"] == "items":
        s["answers"].append(value)
        s["step"] += 1
        if s["step"] < len(QUESTIONS):
            await message.reply(question_text(s["step"]))
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
    tamam_shode = total_mavad + hoghoogh_va_sayer        # B38
    profit_pct = s["profit"]
    sood = tamam_shode * profit_pct / 100                # B39
    forosh = tamam_shode + sood                          # B40

    text = (
        "📊 نتیجه‌ی محاسبه — بهای تمام‌شده‌ی یک جفت کفش\n"
        "═════════════════\n"
        f"🧵 جمع مواد اولیه: {fmt(total_mavad)} تومان\n"
        f"👷 جمع حقوق و دستمزد: {fmt(total_dastmozd)} تومان\n"
        f"🏭 جمع سایر هزینه‌ها: {fmt(total_sayer)} تومان\n"
        f"➕ هزینه‌ی حقوق و سایر: {fmt(hoghoogh_va_sayer)} تومان\n"
        "─────────────────\n"
        f"💰 قیمت تمام‌شده‌ی یک جفت کفش: {fmt(tamam_shode)} تومان\n"
        f"📈 سود کارگاه ({int(profit_pct)}٪): {fmt(sood)} تومان\n"
        f"🏷️ قیمت فروش: {fmt(forosh)} تومان\n"
        "═════════════════\n\n"
        "ℹ️ محاسبه‌ی سایر هزینه‌ها بر اساس تعداد تولید در روز به‌صورت سالانه برای هر جفت در نظر گرفته می‌شود.\n\n"
        "برای محاسبه‌ی مجدد /start را بزنید."
    )
    await message.reply(text)


if __name__ == "__main__":
    bot.run()
