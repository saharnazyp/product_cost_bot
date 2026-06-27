# -*- coding: utf-8 -*-
"""
ربات بهای تمام شده‌ی یک جفت کفش دست‌دوز — دوزبانه (فارسی/انگلیسی)
Handmade Shoe Cost Calculator Bot — Bilingual (FA/EN) — for Bale messenger
تعاونی کفاشان دست‌دوز تهران | Tehran Handmade Shoemakers Cooperative

سازگار با python-bale-bot نسخه 2.5.0
اجرا روی Railway: توکن را در متغیر محیطی BOT_TOKEN قرار دهید.
"""

import os
from bale import Bot, Message, MenuKeyboardMarkup, MenuKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# ───────────────── تعریف آیتم‌ها (دوزبانه) ─────────────────
# هر آیتم: {"fa":..., "en":..., "choices_fa":[...], "choices_en":[...]}

MOAD_AVALIYE = [
    {"fa": "چرم رویه", "en": "Upper leather",
     "choices_fa": ["فلوتر", "صافتی", "جیر", "نبوک", "اشوالت", "هورس", "پولیشی", "ناپا", "میلینگ"],
     "choices_en": ["Floater", "Softy", "Suede", "Nubuck", "Asphalt", "Horse", "Polished", "Nappa", "Milled"]},
    {"fa": "چرم آستری", "en": "Lining leather",
     "choices_fa": ["گاوی", "بزی", "گوسفندی"],
     "choices_en": ["Cow", "Goat", "Sheep"]},
    {"fa": "زیره", "en": "Sole",
     "choices_fa": ["ترمو", "لاستیک", "نیولایت", "میکرولایت", "پی‌یو", "چرم"],
     "choices_en": ["Thermo", "Rubber", "Neolite", "Microlite", "PU", "Leather"]},
    {"fa": "کف ۲۵", "en": "Insole 25",
     "choices_fa": ["تکسون", "اشتراول"],
     "choices_en": ["Texon", "Strobel"]},
    {"fa": "قدک پشت و پنجه ۳۲", "en": "Counter & toe puff 32",
     "choices_fa": ["حرارتی", "تکنوژی", "بنزینی"],
     "choices_en": ["Thermal", "Technogel", "Solvent"]},
    {"fa": "انواع چسب (فرنگی، کرپ، پی‌یو، دوغی)", "en": "Adhesives (imported, crepe, PU, water-based)",
     "choices_fa": [], "choices_en": []},
    {"fa": "ابر", "en": "Foam",
     "choices_fa": ["معمولی", "مموری فوم"],
     "choices_en": ["Regular", "Memory foam"]},
    {"fa": "خرجکار (میخ، منگنه، پرایمر، واکس، نخ و سایر)", "en": "Consumables (nails, staples, primer, wax, thread, etc.)",
     "choices_fa": [], "choices_en": []},
    {"fa": "یراق آلات", "en": "Hardware",
     "choices_fa": ["سگک", "منگنه", "سایر"],
     "choices_en": ["Buckle", "Eyelet", "Other"]},
    {"fa": "بند", "en": "Laces",
     "choices_fa": ["ایرانی", "خارجی"],
     "choices_en": ["Domestic", "Imported"]},
    {"fa": "زیپ", "en": "Zipper",
     "choices_fa": [], "choices_en": []},
    {"fa": "کلوچه", "en": "Heel block",
     "choices_fa": ["چسبی", "آماده"],
     "choices_en": ["Adhesive", "Ready-made"]},
    {"fa": "مدل‌سازی و قالب و ماهیچه", "en": "Pattern, last & shank",
     "choices_fa": [], "choices_en": []},
    {"fa": "هزینه بسته‌بندی", "en": "Packaging cost",
     "choices_fa": [], "choices_en": []},
    {"fa": "ملزومات (قالب، تیغ، تخته پرس و سایر)", "en": "Tooling (lasts, blades, press boards, etc.)",
     "choices_fa": [], "choices_en": []},
    {"fa": "ضایعات", "en": "Waste",
     "choices_fa": [], "choices_en": []},
]

# دستمزد مستقیم — (fa, en)
DASTMOZD = [
    ("آستر بر", "Lining cutter"),
    ("لویس کار", "Lasting worker"),
    ("رومیزکار", "Bench worker"),
    ("چرخکار", "Stitcher"),
    ("دورنعلکی", "Welt/edge worker"),
    ("لفاف کن", "Wrapper"),
    ("پرداخت‌چی", "Finisher"),
    ("کار جمع‌کن", "Assembler"),
    ("لیزر", "Laser operator"),
    ("دوخت زیگزال", "Zigzag stitcher"),
    ("حک مارک", "Branding/embossing"),
    ("مدل‌گیر", "Pattern maker"),
    ("حسابدار", "Accountant"),
    ("کنترل کیفی", "Quality control"),
    ("کارفرما", "Employer"),
]

# سایر هزینه‌ها — (fa, en)
SAYER = [
    ("اجاره", "Rent"),
    ("تعمیرات و نگهداری ماشین‌آلات", "Machinery maintenance"),
    ("انرژی", "Energy/utilities"),
    ("بیمه", "Insurance"),
    ("حمل و نقل و پیک", "Transport & courier"),
    ("خدمات پس از فروش", "After-sales service"),
    ("آبدارخانه", "Pantry/refreshments"),
    ("مالیات عملکرد", "Income tax"),
]

# ساخت لیست تخت سوالات دوزبانه
QUESTIONS = []
for it in MOAD_AVALIYE:
    QUESTIONS.append({
        "section": "mavad", "fa": it["fa"], "en": it["en"],
        "choices_fa": it["choices_fa"], "choices_en": it["choices_en"],
    })
for fa, en in DASTMOZD:
    QUESTIONS.append({"section": "dastmozd", "fa": fa, "en": en, "choices_fa": [], "choices_en": []})
for fa, en in SAYER:
    QUESTIONS.append({"section": "sayer", "fa": fa, "en": en, "choices_fa": [], "choices_en": []})

N_MAVAD = len(MOAD_AVALIYE)
N_DASTMOZD = len(DASTMOZD)
TOTAL_Q = len(QUESTIONS)

# ───────────────── متن‌های دوزبانه ─────────────────
T = {
    "fa": {
        "headers": {
            "mavad": "🧵 مواد اولیه (مبلغ هر جفت)",
            "dastmozd": "👷 دستمزد مستقیم (جفتی چند)",
            "sayer": "🏭 سایر هزینه‌ها (سهم هر جفت)",
        },
        "prompt": {
            "mavad": "مبلغ هر جفت را به تومان وارد کنید:",
            "dastmozd": "جفتی چند؟ (کارمزد هر جفت به تومان):",
            "sayer": "سهم هر جفت را به تومان وارد کنید:",
        },
        "back": "⬅️ قبلی",
        "edit": "✏️ ویرایش یک آیتم",
        "confirm": "✅ تأیید و ادامه",
        "choose_type": "نوع را انتخاب کنید:",
        "type_set": "✅ نوع: {t}\nحالا مبلغ هر جفت این آیتم را به تومان وارد کنید:",
        "pls_btn_type": "لطفاً یکی از دکمه‌های نوع را انتخاب کنید.",
        "back_done": "⬅️ به سوال قبل برگشتیم:",
        "no_back": "این اولین سوال است؛ امکان برگشت نیست.",
        "only_num": "⚠️ لطفاً فقط عدد وارد کنید.",
        "welcome": (
            "👞✨ ربات هوشمند محاسبه بهای تمام‌شده\n"
            "🏛️ تعاونی کفاشان دست‌دوز تهران | تأسیس ۱۳۴۸\n"
            "━━━━━━━━━━━━━━━━━\n"
            "به سامانه هوشمند محاسبه بهای تمام‌شده کفش دست‌دوز خوش آمدید. 🌟\n\n"
            "تمام مبالغ مربوط به «یک جفت کفش» هستند:\n"
            "🧵 مواد اولیه ← هزینه مواد مصرفی برای یک جفت\n"
            "👨🏻‍🔧 دستمزد ← کارمزد پرداختی برای تولید یک جفت\n"
            "🏭 سایر هزینه‌ها ← سهم هر جفت از اجاره، برق، بیمه و…\n\n"
            "▫️ آیتم‌های دارای نوع، اول با دکمه انتخاب می‌شوند، سپس مبلغ.\n"
            "▫️ اگر هزینه‌ای ندارید، عدد ۰ را ارسال کنید.\n"
            "▫️ هر زمان با «⬅️ قبلی» یک قدم به عقب برگردید.\n"
            "▫️ در پایان، خلاصه را می‌بینید و می‌توانید هر آیتم را ویرایش کنید.\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🚀 شروع می‌کنیم!"
        ),
        "summary_title": "📋 خلاصه‌ی اطلاعات واردشده:\n",
        "summary_edit_hint": "\nبرای ویرایش، «✏️ ویرایش یک آیتم» را بزنید.\nاگر همه‌چیز درست است، «✅ تأیید و ادامه» را بزنید.",
        "toman": "تومان",
        "ask_edit_num": "شماره‌ی آیتمی که می‌خواهید ویرایش کنید را بفرستید (مثلاً 14):",
        "ask_profit": "✅ عالی. حالا درصد سود کارگاه را وارد کنید (مثلاً برای ۲۰ درصد عدد 20):",
        "pls_review_btn": "لطفاً «✏️ ویرایش یک آیتم» یا «✅ تأیید و ادامه» را بزنید.",
        "pls_num_idx": "لطفاً شماره‌ی آیتم را به عدد بفرستید (مثلاً 14):",
        "idx_range": "شماره باید بین ۱ تا {n} باشد. دوباره بفرستید:",
        "editing": "در حال ویرایش آیتم {i}: {label}",
        "choose_type_again": "نوع را دوباره انتخاب کنید:",
        "fixed": "✅ اصلاح شد.",
        "start_hint": "برای شروع محاسبه، دستور /start را بفرستید.",
        "result": (
            "📊 نتیجه‌ی محاسبه — بهای تمام‌شده‌ی یک جفت کفش\n"
            "═════════════════\n"
            "🧵 جمع مواد اولیه: {m} تومان\n"
            "👷 جمع دستمزد: {d} تومان\n"
            "🏭 جمع سایر هزینه‌ها: {s} تومان\n"
            "➕ هزینه‌ی حقوق و سایر: {hs} تومان\n"
            "─────────────────\n"
            "💰 قیمت تمام‌شده: {tc} تومان\n"
            "📈 سود کارگاه ({p}٪): {pr} تومان\n"
            "🏷️ قیمت فروش: {sell} تومان\n"
            "═════════════════\n\n"
            "📝 نوع جنس‌های انتخاب‌شده:\n{types}\n\n"
            "🔄 برای محاسبه‌ی مجدد /start را بزنید.\n"
            "🏛️ تعاونی کفاشان دست‌دوز تهران | تأسیس ۱۳۴۸"
        ),
    },
    "en": {
        "headers": {
            "mavad": "🧵 Raw materials (price per pair)",
            "dastmozd": "👷 Direct labor (wage per pair)",
            "sayer": "🏭 Other costs (share per pair)",
        },
        "prompt": {
            "mavad": "Enter the cost per pair (in Toman):",
            "dastmozd": "Wage per pair? (in Toman):",
            "sayer": "Enter the share per pair (in Toman):",
        },
        "back": "⬅️ Back",
        "edit": "✏️ Edit an item",
        "confirm": "✅ Confirm & continue",
        "choose_type": "Choose a type:",
        "type_set": "✅ Type: {t}\nNow enter the cost per pair for this item (in Toman):",
        "pls_btn_type": "Please pick one of the type buttons.",
        "back_done": "⬅️ Went back to the previous question:",
        "no_back": "This is the first question; can't go back.",
        "only_num": "⚠️ Please enter a number only.",
        "welcome": (
            "👞✨ Smart Shoe Cost Calculator\n"
            "🏛️ Tehran Handmade Shoemakers Cooperative | Est. 1969\n"
            "━━━━━━━━━━━━━━━━━\n"
            "Welcome to the handmade shoe cost calculator. 🌟\n\n"
            "All amounts are per ONE pair of shoes:\n"
            "🧵 Raw materials ← material cost for one pair\n"
            "👨🏻‍🔧 Labor ← wage paid to produce one pair\n"
            "🏭 Other costs ← per-pair share of rent, power, insurance, etc.\n\n"
            "▫️ Items with types: pick the type first, then enter the amount.\n"
            "▫️ If a cost doesn't apply, send 0.\n"
            "▫️ Use «⬅️ Back» anytime to go one step back.\n"
            "▫️ At the end you'll see a summary and can edit any item.\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🚀 Let's start!"
        ),
        "summary_title": "📋 Summary of your entries:\n",
        "summary_edit_hint": "\nTo edit, tap «✏️ Edit an item».\nIf everything is correct, tap «✅ Confirm & continue».",
        "toman": "Toman",
        "ask_edit_num": "Send the number of the item you want to edit (e.g. 14):",
        "ask_profit": "✅ Great. Now enter the profit percentage (e.g. 20 for 20%):",
        "pls_review_btn": "Please tap «✏️ Edit an item» or «✅ Confirm & continue».",
        "pls_num_idx": "Please send the item number (e.g. 14):",
        "idx_range": "Number must be between 1 and {n}. Send again:",
        "editing": "Editing item {i}: {label}",
        "choose_type_again": "Choose the type again:",
        "fixed": "✅ Updated.",
        "start_hint": "Send /start to begin the calculation.",
        "result": (
            "📊 Result — Cost price of one pair of shoes\n"
            "═════════════════\n"
            "🧵 Raw materials total: {m} Toman\n"
            "👷 Labor total: {d} Toman\n"
            "🏭 Other costs total: {s} Toman\n"
            "➕ Labor + other: {hs} Toman\n"
            "─────────────────\n"
            "💰 Cost price: {tc} Toman\n"
            "📈 Profit ({p}%): {pr} Toman\n"
            "🏷️ Selling price: {sell} Toman\n"
            "═════════════════\n\n"
            "📝 Selected material types:\n{types}\n\n"
            "🔄 Send /start to calculate again.\n"
            "🏛️ Tehran Handmade Shoemakers Cooperative"
        ),
    },
}

LANG_BTN_FA = "🇮🇷 فارسی"
LANG_BTN_EN = "🇬🇧 English"

sessions = {}  # chat_id -> state


def fa_num(text):
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٬،", "0123456789,,")
    text = text.translate(trans).replace(",", "").replace(" ", "").strip()
    return float(text)


def fmt(x):
    return f"{int(round(x)):,}"


def q_label(q, lang):
    return q["en"] if lang == "en" else q["fa"]


def q_choices(q, lang):
    return q["choices_en"] if lang == "en" else q["choices_fa"]


def section_prefix(step, lang):
    section = QUESTIONS[step]["section"]
    prev = QUESTIONS[step - 1]["section"] if step > 0 else None
    if section != prev:
        return f"\n{T[lang]['headers'][section]}\n─────────────────\n"
    return ""


def make_keyboard(choices, lang, with_back=False):
    kb = MenuKeyboardMarkup()
    row = 1
    for i, c in enumerate(choices):
        kb.add(MenuKeyboardButton(c), row)
        if i % 2 == 1:
            row += 1
    if with_back:
        kb.add(MenuKeyboardButton(T[lang]["back"]), row + 1)
    return kb


def back_keyboard(lang):
    kb = MenuKeyboardMarkup()
    kb.add(MenuKeyboardButton(T[lang]["back"]), 1)
    return kb


def lang_keyboard():
    kb = MenuKeyboardMarkup()
    kb.add(MenuKeyboardButton(LANG_BTN_FA), 1)
    kb.add(MenuKeyboardButton(LANG_BTN_EN), 1)
    return kb


def review_keyboard(lang):
    kb = MenuKeyboardMarkup()
    kb.add(MenuKeyboardButton(T[lang]["edit"]), 1)
    kb.add(MenuKeyboardButton(T[lang]["confirm"]), 2)
    return kb


async def ask_question(message, s):
    lang = s["lang"]
    step = s["step"]
    q = QUESTIONS[step]
    prefix = section_prefix(step, lang)
    num = f"({step + 1}/{TOTAL_Q})"
    can_back = step > 0
    choices = q_choices(q, lang)

    if choices:
        s["await_type"] = True
        kb = make_keyboard(choices, lang, with_back=can_back)
        await message.reply(f"{prefix}{num} {q_label(q, lang)}\n{T[lang]['choose_type']}", components=kb)
    else:
        s["await_type"] = False
        prompt = T[lang]["prompt"][q["section"]]
        kb = back_keyboard(lang) if can_back else None
        await message.reply(f"{prefix}{num} {q_label(q, lang)}\n{prompt}", components=kb)


def go_back(s):
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
    lang = s["lang"]
    lines = [T[lang]["summary_title"]]
    toman = T[lang]["toman"]
    for i, q in enumerate(QUESTIONS):
        val = s["answers"][i] if i < len(s["answers"]) else 0
        t = s["types"][i] if i < len(s["types"]) else "-"
        type_part = f" [{t}]" if t and t != "-" else ""
        lines.append(f"{i + 1}. {q_label(q, lang)}{type_part}: {fmt(val)} {toman}")
    lines.append(T[lang]["summary_edit_hint"])
    return "\n".join(lines)


@bot.event
async def on_before_ready():
    print("ربات آماده شد ✅ | Bot is ready")


@bot.event
async def on_message(message: Message):
    text = message.text
    if text is None:
        return
    text = text.strip()
    chat_id = message.chat.id

    # ── شروع: نمایش انتخاب زبان ──
    if text in ("/start", "start", "شروع"):
        sessions[chat_id] = {
            "lang": None, "step": 0, "answers": [], "types": [],
            "profit": None, "stage": "lang", "await_type": False, "edit_target": None,
        }
        await message.reply(
            "🌐 زبان را انتخاب کنید | Please choose your language:",
            components=lang_keyboard(),
        )
        return

    if chat_id not in sessions:
        await message.reply("Send /start to begin. | برای شروع /start را بفرستید.")
        return

    s = sessions[chat_id]

    # ── انتخاب زبان ──
    if s["stage"] == "lang":
        if text == LANG_BTN_FA or "فارسی" in text:
            s["lang"] = "fa"
        elif text == LANG_BTN_EN or "English" in text or "english" in text:
            s["lang"] = "en"
        else:
            await message.reply("لطفاً زبان را از دکمه‌ها انتخاب کنید. | Please pick a language.",
                                components=lang_keyboard())
            return
        s["stage"] = "items"
        await message.reply(T[s["lang"]]["welcome"])
        await ask_question(message, s)
        return

    lang = s["lang"]
    tr = T[lang]

    # ── دکمه قبلی ──
    if s["stage"] == "items" and (text == tr["back"] or text.replace("⬅️", "").strip() in ("قبلی", "Back")):
        if go_back(s):
            await message.reply(tr["back_done"])
        else:
            await message.reply(tr["no_back"])
        await ask_question(message, s)
        return

    # ── انتخاب نوع ──
    if s["stage"] == "items" and s.get("await_type"):
        q = QUESTIONS[s["step"]]
        choices = q_choices(q, lang)
        if text in choices:
            if s["step"] < len(s["types"]):
                s["types"][s["step"]] = text
            else:
                s["types"].append(text)
            s["await_type"] = False
            await message.reply(tr["type_set"].format(t=text), components=back_keyboard(lang))
        else:
            await message.reply(tr["pls_btn_type"])
        return

    # ── بازبینی پایانی ──
    if s["stage"] == "review":
        if text == tr["edit"] or "ویرایش" in text or "Edit" in text:
            s["stage"] = "edit_pick"
            await message.reply(tr["ask_edit_num"])
            return
        if text == tr["confirm"] or "تأیید" in text or "تایید" in text or "Confirm" in text:
            s["stage"] = "profit"
            await message.reply(tr["ask_profit"])
            return
        await message.reply(tr["pls_review_btn"])
        return

    # ── انتخاب شماره برای ویرایش ──
    if s["stage"] == "edit_pick":
        try:
            idx = int(fa_num(text))
        except (ValueError, AttributeError):
            await message.reply(tr["pls_num_idx"])
            return
        if not (1 <= idx <= TOTAL_Q):
            await message.reply(tr["idx_range"].format(n=TOTAL_Q))
            return
        s["edit_target"] = idx - 1
        s["step"] = idx - 1
        s["stage"] = "items"
        q = QUESTIONS[idx - 1]
        await message.reply(tr["editing"].format(i=idx, label=q_label(q, lang)))
        choices = q_choices(q, lang)
        if choices:
            s["await_type"] = True
            await message.reply(tr["choose_type_again"], components=make_keyboard(choices, lang))
        else:
            s["await_type"] = False
            await message.reply(tr["prompt"][q["section"]])
        return

    # ── خواندن عدد ──
    try:
        value = fa_num(text)
    except (ValueError, AttributeError):
        await message.reply(tr["only_num"])
        return

    # ── ثبت مبلغ آیتم ──
    if s["stage"] == "items":
        q = QUESTIONS[s["step"]]
        choices = q_choices(q, lang)
        if not choices:
            if s["step"] >= len(s["types"]):
                s["types"].append("-")

        if s["step"] < len(s["answers"]):
            s["answers"][s["step"]] = value
            editing = (s.get("edit_target") is not None)
        else:
            s["answers"].append(value)
            editing = False

        if editing:
            s["edit_target"] = None
            s["stage"] = "review"
            await message.reply(tr["fixed"])
            await message.reply(build_summary(s), components=review_keyboard(lang))
            return

        s["step"] += 1
        if s["step"] < TOTAL_Q:
            await ask_question(message, s)
        else:
            s["stage"] = "review"
            await message.reply(build_summary(s), components=review_keyboard(lang))
        return

    # ── درصد سود و نتیجه ──
    if s["stage"] == "profit":
        s["profit"] = value
        await send_result(message, s)
        del sessions[chat_id]
        return


async def send_result(message, s):
    lang = s["lang"]
    tr = T[lang]
    total_mavad, total_dastmozd, total_sayer, hoghoogh_va_sayer, tamam_shode = compute(s)
    profit_pct = s["profit"]
    sood = tamam_shode * profit_pct / 100
    forosh = tamam_shode + sood

    selected = []
    for i in range(N_MAVAD):
        t = s["types"][i] if i < len(s["types"]) else "-"
        if t and t != "-":
            selected.append(f"• {q_label(QUESTIONS[i], lang)}: {t}")
    types_summary = ("\n".join(selected)) if selected else "—"

    text = tr["result"].format(
        m=fmt(total_mavad), d=fmt(total_dastmozd), s=fmt(total_sayer),
        hs=fmt(hoghoogh_va_sayer), tc=fmt(tamam_shode),
        p=int(profit_pct), pr=fmt(sood), sell=fmt(forosh), types=types_summary,
    )
    await message.reply(text)


if __name__ == "__main__":
    bot.run()
