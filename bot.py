from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re
import asyncio
import time
import os

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN belum diset di environment variables!")

warnings = {}
last_link_time = {}


# 🔒 CEK ADMIN
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

    duration = 60  # default 60 detik

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
            await update.message.reply_text("⚠️ Format salah! contoh: /mute 10s /mute 5m /mute 1h")
            return

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(can_send_messages=False)
    )

    await update.message.reply_text(f"🔇 User di-mute selama {duration} detik")

    # ⚠️ NOTE: ini tetap sleep (simple version)
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


# 🔍 FILTER LINK (ANTI SPAM)
async def filter_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user_id = message.from_user.id
    chat_id = update.effective_chat.id
    text = message.text

    # skip admin
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status in ["administrator", "creator"]:
        return

    if re.search(r"(https?://|t\.me/|www\.)", text):

        now = time.time()
        last_time = last_link_time.get(user_id, 0)

        # ❌ terlalu cepat kirim link
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
                    f"⚠️ Warning {count}/5\nJangan spam link (limit 1 link / 10 menit)"
                )
        else:
            # boleh kirim
            last_link_time[user_id] = now


# 👋 WELCOME MESSAGE
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            "SELAMAT DATANG DI GRUP\n\n"
            "𝐏𝐄𝐑𝐀𝐓𝐔𝐑𝐀𝐍 :\n\n"
            "1. Share jualan minimal 10 menit sekali\n"
            "2. Jangan spam / toxic / rasis\n"
            "3. Dilarang konten dewasa\n"
            "4. Gunakan group dengan bijak\n"
            "5. Utamakan Rekber Admin Group untuk kemanan"
            "6. Laporan Scammer/Phising ke Admin Group"
            "7. Ceh CH Blacklist Scam Secara Berkala"
        )


# 🚀 MAIN APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_link))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

print("🤖 Bot jalan...")
app.run_polling()
