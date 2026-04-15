from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re
import asyncio
import time

TOKEN = "8626079007:AAF82ef6HmROrECCsnvA1XCH0xIbAQMO6Js"

warnings = {}
last_link_time = {}

# 🔒 Cek admin
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]

# 🚫 BAN
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Kamu bukan admin!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply user yang mau di-ban!")
        return

    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("🚫 User berhasil di-ban!")

# 🔓 UNBAN
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Kamu bukan admin!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply user yang mau di-unban!")
        return

    user_id = update.message.reply_to_message.from_user.id
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("✅ User berhasil di-unban!")

# 🔇 MUTE
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Kamu bukan admin!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply user yang mau di-mute!")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    duration = 60

    if context.args:
        try:
            time_input = context.args[0]

            if time_input.endswith("s"):
                duration = int(time_input[:-1])
            elif time_input.endswith("m"):
                duration = int(time_input[:-1]) * 60
            elif time_input.endswith("h"):
                duration = int(time_input[:-1]) * 3600
            else:
                duration = int(time_input)
        except:
            await update.message.reply_text("⚠️ Format salah! Contoh: /mute 10s /mute 5m /mute 1h")
            return

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(can_send_messages=False)
    )

    await update.message.reply_text(f"🔇 User di-mute selama {duration} detik")

    await asyncio.sleep(duration)

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(can_send_messages=True)
    )

    await context.bot.send_message(chat_id, "🔊 User sudah di-unmute")

# 🔊 UNMUTE
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Kamu bukan admin!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply user yang mau di-unmute!")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(can_send_messages=True)
    )

    await update.message.reply_text("🔊 User berhasil di-unmute!")

# 🔍 FILTER LINK (1 LINK / 10 MENIT)
async def filter_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    user_id = message.from_user.id
    chat_id = update.effective_chat.id

    # 🔒 Skip admin
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status in ["administrator", "creator"]:
        return

    text = message.text

    if re.search(r"(https?://|t\.me/|www\.)", text):

        now = time.time()
        last_time = last_link_time.get(user_id, 0)

        # ⛔ jika kirim sebelum 10 menit
        if now - last_time < 600:
            try:
                await message.delete()
            except:
                pass

            warnings[user_id] = warnings.get(user_id, 0) + 1
            count = warnings[user_id]

            if count >= 5:
                await context.bot.ban_chat_member(chat_id, user_id)
                await context.bot.send_message(chat_id, "🚫 User di-ban (spam link)")
                warnings[user_id] = 0
            else:
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ Warning {count}/5 jangan spam kirim link, max 1 link dalam 10 menit"
                )
        else:
            # ✅ boleh kirim
            last_link_time[user_id] = now

# 👋 WELCOME MESSAGE
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
"""SELAMAT DATANG DI GRUP

𝐏𝐄𝐑𝐀𝐓𝐔𝐑𝐀𝐍 :

𝟏. 𝐒𝐇𝐀𝐑𝐄 𝐉𝐔𝐀𝐋𝐀𝐍 𝐌𝐈𝐍𝐈𝐌𝐀𝐋 10 MENIT 𝐒𝐄𝐊𝐀𝐋𝐈
𝟐. 𝐉𝐀𝐍𝐆𝐀𝐍 𝐒𝐏𝐀𝐌 / 𝐉𝐀𝐍𝐆𝐀𝐍 𝐓𝐎𝐗𝐈𝐂 / 𝐑𝐀𝐒𝐈𝐒
𝟑. 𝐉𝐀𝐍𝐆𝐀𝐍 𝐁𝐎𝐊𝐄𝐏 ( 𝐅𝐀𝐓𝐀𝐋 )
𝟒. 𝐃𝐈𝐋𝐀𝐑𝐀𝐍𝐆 𝐁𝐄𝐑𝐉𝐔𝐀𝐋𝐀𝐍 𝐃𝐈 𝐋𝐔𝐀𝐑 𝐉𝐔𝐃𝐔𝐋 𝐆𝐑𝐎𝐔𝐏
𝟓. 𝐔𝐓𝐀𝐌𝐀𝐊𝐀𝐍 𝐑𝐄𝐊𝐁𝐄𝐑 𝐀𝐃𝐌𝐈𝐍 𝐆𝐑𝐎𝐔𝐏 𝐔𝐍𝐓𝐔𝐊 𝐊𝐄𝐀𝐌𝐀𝐍𝐀𝐍
𝟔. 𝐋𝐀𝐏𝐎𝐑𝐀𝐍 𝐒𝐂𝐀𝐌𝐌𝐄𝐑/𝐏𝐇𝐈𝐒𝐈𝐍𝐆 𝐊𝐄 𝐀𝐃𝐌𝐈𝐍 𝐆𝐑𝐎𝐔𝐏
𝟕. 𝐂𝐄𝐊 𝐂𝐇 𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓 𝐒𝐂𝐀𝐌 𝐒𝐄𝐂𝐀𝐑𝐀 𝐁𝐄𝐑𝐊𝐀𝐋𝐀"""
        )

# 🚀 MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_link))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

print("Bot jalan...")
app.run_polling()