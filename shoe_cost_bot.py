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
    ("انواع چسب (فرنگی، کرپ، پی‌یو، دوغی)", []),
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
    QUESTIONS.append({"section": "mavad", "label": label, "choices": choices})
for label in DASTMOZD:
    QUESTIONS.append({"section": "dastmozd", "label": label, "choices": []})
for label in SAYER:
    QUESTIONS.append({"section": "sayer", "label": label, "choices": []})

N_MAVAD = len(MOAD_AVALIYE)
N_DASTMOZD = len(DASTMOZD)
TOTAL_Q = len(QUESTIONS)

HEADERS = {
    "mavad": "🧵 مواد اولیه (مبلغ هر جفت)",
    "dastmozd": "👷 دستمزد مستقیم (جفتی چند)",
    "sayer": "🏭 سایر هزینه‌ها (سهم هر جفت)",
}

PROMPT = {
    "mavad": "مبلغ هر جفت را به تومان وارد کنید:",
    "dastmozd": "جفتی چند؟ (کارمزد هر جفت به تومان):",
    "sayer": "سهم هر جفت را به تومان وارد کنید:",
}

BACK_BTN = "⬅️ قبلی"
EDIT_BTN = "✏️ ویرایش یک آیتم"
CONFIRM_BTN = "✅ تأیید و ادامه"

sessions = {}  # chat_id -> state


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


def make_keyboard(choices, with_back=False):
    """کیبورد انتخاب نوع. اگر with_back باشد دکمه قبلی هم اضافه می‌شود."""
    kb = MenuKeyboardMarkup()
    row = 1
    for i, c in enumerate(choices):
        kb.add(MenuKeyboardButton(c), row)
        if i % 2 == 1:
            row += 1
    if with_back:
        kb.add(MenuKeyboardButton(BACK_BTN), row + 1)
    return kb


def back_keyboard():
    """فقط دکمه قبلی، برای مرحله‌ی ورود مبلغ."""
    kb = MenuKeyboardMarkup()
    kb.add(MenuKeyboardButton(BACK_BTN), 1)
    return kb


async def ask_question(message: Message, s):
    """پرسیدن سوال مرحله فعلی."""
    step = s["step"]
    q = QUESTIONS[step]
    prefix = section_prefix(step)
    num = f"({step + 1}/{TOTAL_Q})"
    can_back = step > 0  # در سوال اول دکمه قبلی نداریم

    if q["choices"]:
        s["await_type"] = True
        kb = make_keyboard(q["choices"], with_back=can_back)
        await message.reply(f"{prefix}{num} {q['label']}\nنوع را انتخاب کنید:", components=kb)
    else:
        s["await_type"] = False
        prompt = PROMPT[q["section"]]
        kb = back_keyboard() if can_back else None
        await message.reply(f"{prefix}{num} {q['label']}\n{prompt}", components=kb)


def go_back(s):
    """یک قدم به عقب: آخرین جواب و نوع را پاک می‌کند."""
    if s["step"] <= 0:
        return False
    s["step"] -= 1
    if s["answers"]:
        s["answers"].pop()
    if s["types"]:
        s["types"].pop()
    s["await_type"] = False
    return True


def compute(s):
    ans = s["answers"]
    total_mavad = sum(ans[:N_MAVAD])
    total_dastmozd = sum(ans[N_MAVAD:N_MAVAD + N_DASTMOZD])
    total_sayer = sum(ans[N_MAVAD + N_DASTMOZD:])
    hoghoogh_va_sayer = total_dastmozd + total_sayer
    tamam_shode = total_mavad + hoghoogh_va_sayer
    return total_mavad, total_dastmozd, total_sayer, hoghoogh_va_sayer, tamam_shode


def build_summary(s):
    """خلاصه‌ی شماره‌دار همه‌ی آیتم‌ها برای بازبینی/ویرایش."""
    lines = ["📋 خلاصه‌ی اطلاعات واردشده:\n"]
    for i, q in enumerate(QUESTIONS):
        val = s["answers"][i] if i < len(s["answers"]) else 0
        t = s["types"][i] if i < len(s["types"]) else "-"
        type_part = f" [{t}]" if t and t != "-" else ""
        lines.append(f"{i + 1}. {q['label']}{type_part}: {fmt(val)} تومان")
    lines.append("\nبرای ویرایش، «✏️ ویرایش یک آیتم» را بزنید.")
    lines.append("اگر همه‌چیز درست است، «✅ تأیید و ادامه» را بزنید.")
    return "\n".join(lines)


def review_keyboard():
    kb = MenuKeyboardMarkup()
    kb.add(MenuKeyboardButton(EDIT_BTN), 1)
    kb.add(MenuKeyboardButton(CONFIRM_BTN), 2)
    return kb


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

    # ── شروع / ریست ──
    if text in ("/start", "start", "شروع"):
        sessions[chat_id] = {
            "step": 0, "answers": [], "types": [],
            "profit": None, "stage": "items", "await_type": False,
            "edit_target": None,
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
            "▫️ آیتم‌های دارای نوع، اول با دکمه انتخاب می‌شوند، سپس مبلغ.\n"
            "▫️ اگر هزینه‌ای ندارید، عدد ۰ را ارسال کنید.\n"
            "▫️ هر زمان می‌توانید با «⬅️ قبلی» یک قدم به عقب برگردید.\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📊 در پایان، خلاصه را می‌بینید و می‌توانید هر آیتم را ویرایش کنید.\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🚀 برای شروع، بزن بریم!"
        )
        await ask_question(message, sessions[chat_id])
        return

    if chat_id not in sessions:
        await message.reply("برای شروع محاسبه، دستور /start را بفرستید.")
        return

    s = sessions[chat_id]

    # ── دکمه قبلی (در مرحله آیتم‌ها) ──
    if s["stage"] == "items" and (text == BACK_BTN or text.replace("⬅️", "").strip() == "قبلی"):
        if go_back(s):
            await message.reply("⬅️ به سوال قبل برگشتیم:")
            await ask_question(message, s)
        else:
            await message.reply("این اولین سوال است؛ امکان برگشت نیست.")
            await ask_question(message, s)
        return

    # ── مرحله انتخاب نوع (دکمه) ──
    if s["stage"] == "items" and s.get("await_type"):
        q = QUESTIONS[s["step"]]
        if text in q["choices"]:
            # اگر در حال ویرایش این آیتم بودیم، نوع را جایگزین کن
            if s["step"] < len(s["types"]):
                s["types"][s["step"]] = text
            else:
                s["types"].append(text)
            s["await_type"] = False
            await message.reply(
                f"✅ نوع: {text}\nحالا مبلغ هر جفت این آیتم را به تومان وارد کنید:",
                components=back_keyboard(),
            )
        else:
            await message.reply("لطفاً یکی از دکمه‌های نوع را انتخاب کنید.")
        return

    # ── مرحله بازبینی پایانی ──
    if s["stage"] == "review":
        if text == EDIT_BTN or "ویرایش" in text:
            s["stage"] = "edit_pick"
            await message.reply(
                "شماره‌ی آیتمی که می‌خواهید ویرایش کنید را بفرستید (مثلاً 14):"
            )
            return
        if text == CONFIRM_BTN or "تأیید" in text or "تایید" in text:
            s["stage"] = "profit"
            await message.reply(
                "✅ عالی. حالا درصد سود کارگاه را وارد کنید (مثلاً برای ۲۰ درصد عدد 20):"
            )
            return
        await message.reply("لطفاً «✏️ ویرایش یک آیتم» یا «✅ تأیید و ادامه» را بزنید.")
        return

    # ── انتخاب شماره آیتم برای ویرایش ──
    if s["stage"] == "edit_pick":
        try:
            idx = int(fa_num(text))
        except (ValueError, AttributeError):
            await message.reply("لطفاً شماره‌ی آیتم را به عدد بفرستید (مثلاً 14):")
            return
        if not (1 <= idx <= TOTAL_Q):
            await message.reply(f"شماره باید بین ۱ تا {TOTAL_Q} باشد. دوباره بفرستید:")
            return
        s["edit_target"] = idx - 1
        s["step"] = idx - 1
        s["stage"] = "items"
        q = QUESTIONS[idx - 1]
        await message.reply(f"در حال ویرایش آیتم {idx}: {q['label']}")
        # اگر نوع دارد، اول نوع را بپرس، وگرنه مستقیم مبلغ
        if q["choices"]:
            s["await_type"] = True
            kb = make_keyboard(q["choices"])
            await message.reply("نوع را دوباره انتخاب کنید:", components=kb)
        else:
            s["await_type"] = False
            await message.reply(f"{PROMPT[q['section']]}")
        return

    # ── خواندن عدد (مبلغ یا درصد سود) ──
    try:
        value = fa_num(text)
    except (ValueError, AttributeError):
        await message.reply("⚠️ لطفاً فقط عدد وارد کنید.")
        return

    # ── ثبت مبلغ آیتم ──
    if s["stage"] == "items":
        q = QUESTIONS[s["step"]]
        # نوع برای آیتم‌های بدون انتخاب
        if not q["choices"]:
            if s["step"] < len(s["types"]):
                pass  # در ویرایش، نوع تغییری نمی‌کند
            else:
                s["types"].append("-")

        # ثبت یا جایگزینی مبلغ
        if s["step"] < len(s["answers"]):
            s["answers"][s["step"]] = value      # ویرایش
            editing = (s.get("edit_target") is not None)
        else:
            s["answers"].append(value)            # ثبت عادی
            editing = False

        # اگر در حال ویرایش بودیم، برگرد به خلاصه
        if editing:
            s["edit_target"] = None
            s["stage"] = "review"
            await message.reply("✅ اصلاح شد.")
            await message.reply(build_summary(s), components=review_keyboard())
            return

        # حالت عادی: برو سوال بعد
        s["step"] += 1
        if s["step"] < TOTAL_Q:
            await ask_question(message, s)
        else:
            # پایان آیتم‌ها → نمایش خلاصه برای بازبینی
            s["stage"] = "review"
            await message.reply(build_summary(s), components=review_keyboard())
        return

    # ── درصد سود و نتیجه ──
    if s["stage"] == "profit":
        s["profit"] = value
        await send_result(message, s)
        del sessions[chat_id]
        return


async def send_result(message: Message, s):
    total_mavad, total_dastmozd, total_sayer, hoghoogh_va_sayer, tamam_shode = compute(s)
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
