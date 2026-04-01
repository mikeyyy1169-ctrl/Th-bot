import os
import sqlite3
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

genai.configure(api_key=os.getenv("AIzaSyDkJ3BtvmA8qmH9vNhfA-w7Bbpy8lyTftE"))
model = genai.GenerativeModel("gemini-1.5-flash")

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS chats (user_id INTEGER, role TEXT, message TEXT)")
conn.commit()

SYSTEM_PROMPT = "You are a powerful ChatGPT-like AI. Give clear, smart, helpful responses."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 AI BOT LIVE!")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("DELETE FROM chats WHERE user_id=?", (update.effective_user.id,))
    conn.commit()
    await update.message.reply_text("🧠 Memory cleared!")

def get_memory(user_id):
    cursor.execute("SELECT role, message FROM chats WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()[::-1]
    return "\n".join([f"{r}: {m}" for r, m in rows])

def save_memory(user_id, role, msg):
    cursor.execute("INSERT INTO chats VALUES (?, ?, ?)", (user_id, role, msg))
    conn.commit()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    save_memory(user_id, "user", text)
    memory = get_memory(user_id)

    try:
        response = model.generate_content(SYSTEM_PROMPT + "\n" + memory)
        reply = response.text
        save_memory(user_id, "bot", reply)
    except Exception as e:
        reply = f"Error: {str(e)}"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(os.getenv("7831631456:AAFhfaP8wHVm_QkWfhif2-mFi4r-3XHKLnI")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 BOT RUNNING...")
app.run_polling()
