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
    QR_IMAGE,
    UPI_ID,
    ADMIN_ID
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


user_data = {}


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
        ]
    ]

    await update.message.reply_text(
        "🔥 Welcome to Nandu Global Key Store 🔥\n\n"
        "Premium Digital Store",
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

        user_data[query.from_user.id] = {
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
            "⏳ Select Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("buy_"):

        duration = data.replace(
            "buy_",
            ""
        )

        user = query.from_user.id

        if user not in user_data:
            await query.answer(
                "Please select product again.",
                show_alert=True
            )
            return


        user_data[user]["duration"] = duration
        user_data[user]["amount"] = DURATIONS[duration]


        await query.message.reply_photo(
            photo=open(QR_IMAGE, "rb"),
            caption=(
                "💎 Nandu Global Key Store\n\n"
                f"📦 Product: {user_data[user]['product']}\n"
                f"⏳ Duration: {duration}\n"
                f"💰 Amount: ₹{DURATIONS[duration]}\n\n"
                f"💳 UPI ID: {UPI_ID}\n\n"
                "✅ Payment karne ke baad apna UTR number bheje."
            )
        )



async def utr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    if user not in user_data:
        return


    utr = update.message.text.strip()

    order_id = str(uuid.uuid4())[:8]


    order = user_data[user]


    add_order(
        order_id,
        user,
        order["product"],
        order["duration"],
        order["amount"],
        utr
    )


    await update.message.reply_text(
        "✅ Payment details received.\n\n"
        f"🆔 Order ID: {order_id}\n"
        "⏳ Status: Pending Approval"
    )


    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🆕 New Order\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"👤 User ID: {user}\n"
            f"📦 Product: {order['product']}\n"
            f"⏳ Duration: {order['duration']}\n"async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data.split("_")

    action = data[0]
    order_id = data[1]
    user_id = int(data[2])


    if action == "approve":

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Payment Approved!\n\n"
                "Your order is confirmed."
            )
        )

        await query.edit_message_text(
            f"✅ Order {order_id} Approved"
        )


    elif action == "reject":

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Payment Rejected.\n\n"
                "Please contact admin."
            )
        )

        await query.edit_message_text(
            f"❌ Order {order_id} Rejected"
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
            admin_button,
            pattern="^(approve|reject)_"
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            utr_handler
        )
    )


    print("Bot Started...")


    app.run_polling()



if __name__ == "__main__":
    main()
            f"💰 Amount: ₹{order['amount']}\n"
            f"🔢 UTR: {utr}"
        )
    )
    
