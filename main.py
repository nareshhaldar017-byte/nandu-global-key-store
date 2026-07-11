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
async def buy_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    duration = query.data.replace(
        "buy_",
        ""
    )

    user_id = query.from_user.id

    product = user_orders.get(
        user_id,
        {}
    ).get(
        "product"
    )


    if not product:
        await query.message.reply_text(
            "❌ Product not found. Please restart."
        )
        return


    amount = DURATIONS.get(
        duration
    )


    order_id = str(
        uuid.uuid4()
    )[:8]


    user_orders[user_id] = {
        "product": product,
        "duration": duration,
        "amount": amount,
        "order_id": order_id
    }


    add_order(
        order_id,
        user_id,
        product,
        duration,
        amount,
        "",
        "pending"
    )


    await query.message.reply_photo(
        photo=open(QR_IMAGE, "rb"),
        caption=(
            "💳 Payment Details\n\n"
            f"📦 Product: {product}\n"
            f"⏳ Duration: {duration}\n"
            f"💰 Amount: ₹{amount}\n\n"
            f"UPI: {UPI_ID}\n\n"
            "Payment karne ke baad UTR number bheje."
        )
    )
async def utr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    utr = update.message.text


    order = user_orders.get(user_id)


    if not order:

        await update.message.reply_text(
            "❌ Pehle product purchase kare."
        )
        return


    add_order(
        order["order_id"],
        user_id,
        order["product"],
        order["duration"],
        order["amount"],
        utr
    )


    await update.message.reply_text(
        "✅ Payment details received.\n"
        "⏳ Admin approval ka wait kare."
    )


    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🆕 New Order\n\n"
            f"🆔 Order ID: {order['order_id']}\n"
            f"👤 User ID: {user_id}\n"
            f"📦 Product: {order['product']}\n"
            f"⏳ Duration: {order['duration']}\n"
            f"💰 Amount: ₹{order['amount']}\n"
            f"🔢 UTR: {utr}"
        )
    )
def main():

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            button
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            buy_duration,
            pattern="^buy_"
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            utr_handler
        )
    )


    print("Bot Started")


    app.run_polling()



if __name__ == "__main__":
    main()
