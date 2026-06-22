import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config (from Railway env vars) ────────────────────────────────────────────
BOT_TOKEN       = os.environ["BOT_TOKEN"]
CATALOGUE_PHOTO = os.environ.get("CATALOGUE_PHOTO", "")   # Telegram file_id or HTTPS URL
SUPPORT         = os.environ.get("SUPPORT", "@yoursupport")
WEBHOOK_URL     = os.environ.get("WEBHOOK_URL", "")        # e.g. https://mybot.up.railway.app
PORT            = int(os.environ.get("PORT", 8080))

# ── Per-option QR codes (set env vars QR_C, QR_D, … on Railway) ───────────────
# Each value can be a Telegram file_id or a public HTTPS image URL.
# If an option's QR var is not set, the bot sends text-only payment instructions.
OPTION_QR = {
    key: os.environ.get(f"QR_{key}", "")
    for key in "BCDEFGHIJKLM"
}

# ── Conversation states ────────────────────────────────────────────────────────
CHOOSE_OPTION, = range(1)

# ── Option definitions ─────────────────────────────────────────────────────────
OPTION_KEYS = list("ACDEFGHIJKLMN")

OPTION_NAMES = {
    "A": "Account Credits",
    "C": "Celibrity / MMS Leaks ₹59",
    "D": "Dressing Room Cam Leaks ₹29",
    "E": "Girlfriend Ke Bachpan Dosti Ke Saath ₹42",
    "F": "Desi Foriegn Combo ₹29",
    "G": "Dark Web Combo ₹45",
    "H": "Girlfriend Boyfriend Leaks ₹59",
    "I": "F0rced R@pe ₹69",
    "J": "Ch!ld P0rn ₹69",
    "K": "Padosi Aunty Ki Acche Bacha ₹55",
    "L": "Mobile Store Service Boy Stolen Collection ₹35",
    "M": "Hotel Receptionist Ladki / Indigo Airhostess ₹39",
    "N": "All Premium Bundles ₹199",
}

OPTION_PRICES = {
    "C": "₹59",
    "D": "₹29",
    "E": "₹42",
    "F": "₹29",
    "G": "₹45",
    "H": "₹59",
    "I": "₹69",
    "J": "₹69",
    "K": "₹55",
    "L": "₹35",
    "M": "₹39",
    "N": "₹199",
}

# ── Helper ─────────────────────────────────────────────────────────────────────

def option_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(OPTION_NAMES.get(k, k), callback_data=f"opt:{k}")]
        for k in OPTION_KEYS
    ]
    return InlineKeyboardMarkup(rows)


async def send_catalogue(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send catalogue photo (or text fallback) with option buttons."""
    markup  = option_keyboard()
    caption = "📋 *Our Service Catalogue*\n\n𝘛𝘩𝘪𝘴 𝘪𝘴 𝘢 𝘱𝘳𝘦𝘮𝘪𝘶𝘮 𝘢𝘥𝘶𝘭𝘵 𝘦𝘯𝘵𝘦𝘳𝘵𝘢𝘪𝘯𝘮𝘦𝘯𝘵 𝘱𝘭𝘢𝘵𝘧𝘰𝘳𝘮 𝘰𝘧𝘧𝘦𝘳𝘪𝘯𝘨 𝘢 𝘥𝘪𝘷𝘦𝘳𝘴𝘦, 𝘤𝘶𝘳𝘢𝘵𝘦𝘥 𝘭𝘪𝘣𝘳𝘢𝘳𝘺 𝘰𝘧 𝘩𝘪𝘨𝘩-𝘲𝘶𝘢𝘭𝘪𝘵𝘺 𝘤𝘰𝘯𝘵𝘦𝘯𝘵\n\nPlease select an option:"
    if CATALOGUE_PHOTO:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=CATALOGUE_PHOTO,
            caption=caption,
            reply_markup=markup,
            parse_mode="Markdown",
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=markup,
            parse_mode="Markdown",
        )


# ── Handlers ───────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — show catalogue immediately, no age gate."""
    await send_catalogue(update.effective_chat.id, context)
    return CHOOSE_OPTION


async def cb_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle A–J option selection."""
    q = update.callback_query
    await q.answer()
    option  = q.data.split(":", 1)[1]   # e.g. "C"
    chat_id = q.from_user.id

    # ── Option A: Account Balance ──────────────────────────────────────────────
    if option == "A":
        await context.bot.send_message(
            chat_id,
            "💰 *Account Balance*\n\n"
            "Your current balance: *₹0.00*\n\n"
            "🎁 _Your account will be credited with *Free ₹50* after the first purchase!_",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # ── Options B–M: Show QR + wait message ───────────────────────────────────
    name  = OPTION_NAMES.get(option, f"Option {option}")
    price = OPTION_PRICES.get(option, "")
    qr    = OPTION_QR.get(option, "")

    payment_text = (
        f"💳 *Payment — {name}*\n\n"
        f"Amount: *{price}*\n\n"
        f"Please scan the QR code below to pay via *Paytm / UPI*.\n\n"
        f"⏳ Once you've paid, please wait — your payment will be "
        f"reviewed and approved manually. You'll be notified once it's confirmed. ✅"
    )

    try:
        await q.delete_message()
    except Exception:
        pass   # message may already be gone

    if qr:
        await context.bot.send_photo(
            chat_id,
            photo=qr,
            caption=payment_text,
            parse_mode="Markdown",
        )
    else:
        await context.bot.send_message(chat_id, payment_text, parse_mode="Markdown")

    return ConversationHandler.END   # no further steps needed


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Session cancelled. Type /start to begin again.")
    return ConversationHandler.END


# ── App entry point ────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            CHOOSE_OPTION: [
                CallbackQueryHandler(cb_option, pattern=r"^opt:"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )

    app.add_handler(conv)

    # ── Webhook (Railway) vs polling (local dev) ───────────────────────────────
    if WEBHOOK_URL:
        logger.info("Starting webhook on port %s …", PORT)
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        )
    else:
        logger.info("WEBHOOK_URL not set — using long polling (local dev mode)")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()