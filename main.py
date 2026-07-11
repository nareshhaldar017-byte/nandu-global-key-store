from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from config import (
    BOT_TOKEN,
    ADMIN_ID,
    QR_IMAGE,
    UPI_ID,
    CHANNEL_URL,
    ADMIN_USERNAME
)

from database import (
    create_tables,
    add_user,
    add_order
)

from products import (
    PRODUCTS,
    DURATIONS
)

import uuid


user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )


    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Products",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url=f"https://t.me/{ADMIN_USERNAME}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_URL
            )
        ]
    ]


    await update.message.reply_text(
        "🔥 Welcome to Nandu Global Key Store 🔥\n\n"
        "💎 Premium Digital Store\n"
        "Choose your option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data


    if data == "products":

        buttons = []

        for product in PRODUCTS:

            buttons.append(
                [
                    InlineKeyboardButton(
                        product["name"],
                        callback_data=f"product_{product['id']}"
                    )
                ]
            )


        await query.edit_message_text(
            "🛒 Select Product:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    elif data.startswith("product_"):

        product_id = data.replace(
            "product_",
            ""
        )

        user_orders[query.from_user.id] = {
            "product": product_id
        }


        buttons = []

        for duration, price in DURATIONS.items():

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"{duration} - ₹{price}",
                        callback_data=f"buy_{duration}"
                    )
                ]
            )


        await query.edit_message_text(
            f"📦 Product Selected\n\n"
            f"{product_id}\n\n"
            "⏳ Select Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
