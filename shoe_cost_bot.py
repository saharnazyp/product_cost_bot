# -*- coding: utf-8 -*-
"""
ربات بهای تمام شده‌ی یک جفت کفش دست‌دوز — برای پیام‌رسان بله
ساختار آیتم‌ها دقیقاً مطابق فایل «قیمت تمام شده ربات 2.xlsx»

نصب کتابخانه:
    pip install python-bale-bot

اجرا:
    1) توکن ربات را از @BotFather در بله بگیرید و در BOT_TOKEN قرار دهید.
    2) python shoe_cost_bot.py
"""

from bale import Bot, Update, Message
from bale.handlers import CommandHandler, MessageHandler

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # توکن از متغیر محیطی Railway خوانده می‌شود

bot = Bot(token=BOT_TOKEN)

# ───────────────── تعریف آیتم‌ها بر اساس فایل اکسل ─────────────────

# بخش ۱: مواد اولیه (E3:E18)
MOAD_AVALIYE = [
    ("چرم رویه (فلوتر/صافتی/جیر/نبوک/اشوالت)", "چرم رویه"),
    ("چرم آستری (گاوی/بزی/گوسفندی)", "چرم آستری"),
    ("زیره (ترمو/لاستیک/نیولایت/چرم/پی‌یو)", "زیره"),
    ("کف ۲۵ (تکسون/اشتراول)", "کف"),
    ("قدک پشت و پنجه ۳۲ (حرارتی/تکنوژی/بنزینی)", "قدک"),
    ("انواع چسب (فرنگی/کرپ/پی‌یو/دوغی)", "چسب"),
    ("ابر (معمولی/مموری فوم)", "ابر"),
    ("خرجکار (میخ، منگنه، پرایمر، سمباده، واکس، پولیش، نخ، سوزن و سایر)", "خرجکار"),
    ("یراق آلات (سگک/منگنه و سایر)", "یراق آلات"),
    ("بند", "بند"),
    ("زیپ", "زیپ"),
    ("کلوچه (چسبی/آماده)", "کلوچه"),
    ("مدل‌سازی و قالب و ماهیچه (هزینه‌های تکی)", "مدل‌سازی"),
    ("هزینه بسته‌بندی (جعبه/کارتن مادر/نایلکس/سلفون/پاشنه‌کش)", "بسته‌بندی"),
    ("ملزومات (قالب/تیغ/تخته پرس/آلومنیوم پرس/تیغ لویس)", "ملزومات"),
    ("ضایعات (چرم/آستر/زیره و سایر)", "ضایعات"),
]

# بخش ۲: دستمزد مستقیم
DASTMOZD = [
    ("کاربری", "آستر بر", "لویس کار", "رومیزکار", "چرخکار"),
    ("پیشکار", "دورنعلکی", "لفاف کن", "پرداخت‌چی", "کار جمع‌کن"),
    ("بافت", "لیزر", "دوخت زیگزال", "حک مارک", "مدل‌گیر"),
    ("سرپرست", "حسابدار", "کنترل کیفی", "کارفرما"),
]

# بخش ۳: سایر هزینه‌ها
SAYER = [
    ("اجاره", "تعمیرات و نگهداری ماشین‌آلات", "انرژی", "بیمه", "حمل و نقل و پیک"),
    ("هزینه‌های جانبی", "خدمات پس از فروش", "آبدارخانه", "مالیات عملکرد"),
]

# لیست تخت همه‌ی پرسش‌ها به ترتیب
def build_questions():
    qs = []
    for label, _ in MOAD_AVALIYE:
        qs.append(("mavad", label))
    for row in DASTMOZD:
        for item in row:
            qs.append(("dastmozd", item))
    for row in SAYER:
        for item in row:
            qs.append(("sayer", item))
    return qs

QUESTIONS = build_questions()

# نگهداری وضعیت هر کاربر
sessions = {}  # user_id -> {"step": int, "answers": [], "profit": None, "stage": str}


def fa_num(text):
    """تبدیل ارقام فارسی به انگلیسی و خواندن عدد"""
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٬،", "0123456789,,")
    text = text.translate(trans).replace(",", "").replace(" ", "").strip()
    return float(text)


@bot.event
async def on_update(update: Update):
    pass


async def start(message: Message):
    uid = message.from_user.id
    sessions[uid] = {"step": 0, "answers": [], "profit": None, "stage": "items"}
    await message.reply(
        "👞 ربات محاسبه‌ی بهای تمام‌شده‌ی یک جفت کفش دست‌دوز\n\n"
        "برای هر آیتم، هزینه‌ی آن برای *یک جفت کفش* را به تومان وارد کنید.\n"
        "اگر آیتمی ندارید عدد ۰ را بفرستید.\n\n"
        "برای شروع مجدد هر زمان /start را بزنید.\n"
        "─────────────────"
    )
    await ask_next(message)


async def ask_next(message: Message):
    uid = message.from_user.id
    s = sessions[uid]
    step = s["step"]

    if step < len(QUESTIONS):
        section, label = QUESTIONS[step]
        headers = {
            "mavad": "🧵 مواد اولیه",
            "dastmozd": "👷 دستمزد مستقیم",
            "sayer": "🏭 سایر هزینه‌ها",
        }
        # نمایش عنوان بخش هنگام تغییر بخش
        prev_section = QUESTIONS[step - 1][0] if step > 0 else None
        prefix = ""
        if section != prev_section:
            prefix = f"\n*{headers[section]}*\n─────────────────\n"
        await message.reply(f"{prefix}({step+1}/{len(QUESTIONS)}) {label} :")
    else:
        # مرحله‌ی درصد سود
        s["stage"] = "profit"
        await message.reply(
            "✅ همه‌ی هزینه‌ها وارد شد.\n\n"
            "حالا *درصد سود کارگاه* را وارد کنید (مثلاً برای ۲۰ درصد عدد 20):"
        )


async def handle_text(message: Message):
    uid = message.from_user.id
    if uid not in sessions:
        await start(message)
        return

    s = sessions[uid]

    try:
        value = fa_num(message.text)
    except (ValueError, AttributeError):
        await message.reply("⚠️ لطفاً فقط عدد وارد کنید.")
        return

    if s["stage"] == "items":
        s["answers"].append(value)
        s["step"] += 1
        await ask_next(message)

    elif s["stage"] == "profit":
        s["profit"] = value
        await show_result(message)


async def show_result(message: Message):
    uid = message.from_user.id
    s = sessions[uid]
    ans = s["answers"]

    n_mavad = len(MOAD_AVALIYE)
    n_dastmozd = sum(len(r) for r in DASTMOZD)

    total_mavad = sum(ans[:n_mavad])
    total_dastmozd = sum(ans[n_mavad:n_mavad + n_dastmozd])
    total_sayer = sum(ans[n_mavad + n_dastmozd:])

    hoghoogh_va_sayer = total_dastmozd + total_sayer
    tamam_shode = total_mavad + hoghoogh_va_sayer  # B38

    profit_pct = s["profit"]
    sood = tamam_shode * profit_pct / 100  # B39
    forosh = tamam_shode + sood  # B40

    def f(x):
        return f"{int(round(x)):,}"

    text = (
        "📊 *نتیجه‌ی محاسبه — بهای تمام‌شده‌ی یک جفت کفش*\n"
        "═════════════════\n"
        f"🧵 جمع مواد اولیه: {f(total_mavad)} تومان\n"
        f"👷 جمع حقوق و دستمزد: {f(total_dastmozd)} تومان\n"
        f"🏭 جمع سایر هزینه‌ها: {f(total_sayer)} تومان\n"
        f"➕ هزینه‌ی حقوق و سایر: {f(hoghoogh_va_sayer)} تومان\n"
        "─────────────────\n"
        f"💰 *قیمت تمام‌شده‌ی یک جفت کفش: {f(tamam_shode)} تومان*\n"
        f"📈 سود کارگاه ({int(profit_pct)}٪): {f(sood)} تومان\n"
        f"🏷️ *قیمت فروش: {f(forosh)} تومان*\n"
        "═════════════════\n\n"
        "ℹ️ توجه: محاسبه‌ی سایر هزینه‌ها بر اساس تعداد تولید در روز به‌صورت سالانه برای هر جفت در نظر گرفته می‌شود.\n\n"
        "برای محاسبه‌ی مجدد /start را بزنید."
    )
    await message.reply(text)
    del sessions[uid]


# ───────────────── ثبت هندلرها ─────────────────

@bot.event
async def on_ready():
    print("ربات آماده شد ✅")


bot.add_handler(CommandHandler("start", start))
bot.add_handler(MessageHandler(handle_text))

if __name__ == "__main__":
    bot.run()
