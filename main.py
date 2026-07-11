import uuid

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID, QR_IMAGE, UPI_ID

from database import (
    create_tables,
    add_user,
    add_order,
    get_order,
    update_order_status,
)

from products import PRODUCTS, DURATIONS 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Products",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url="https://t.me/YOUR_USERNAME"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url="https://t.me/YOUR_CHANNEL"
            )
        ]
    ]

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "🔥 Welcome to Nandu Global Key Store\n\n"
        "Choose an option below.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Product List
    if data == "products":
        buttons = []

        for product in PRODUCTS:
            buttons.append([
                InlineKeyboardButton(
                    product["name"],
                    callback_data=f"product_{product['id']}"
                )
            ])

        await query.edit_message_text(
            "🛍 Select Product:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Duration List
    elif data.startswith("product_"):
        product_id = data.replace("product_", "")

        context.user_data["product"] = product_id

        buttons = []

        for duration, price in DURATIONS.items():
            buttons.append([
                InlineKeyboardButton(
                    f"{duration} - ₹{price}",
                    callback_data=f"buy_{duration}"
                )
            ])

        await query.edit_message_text(
            f"⏳ Select Duration for {product_id}:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )













































































































































































































































































































































































































































     
