import random
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from gtts import gTTS
import os

TOKEN = "8141970105:AAFS5aHK_QY0_i9yaoGZljAK9TnUvWYo8Z0"

WORDS = [
    {"word": "apple", "translation": "яблоко", "example": "I like to eat an apple every day."},
    {"word": "book", "translation": "книга", "example": "This book is very interesting."},
    {"word": "computer", "translation": "компьютер", "example": "I use a computer for studying."}
]

QUIZ, CHAT = range(2)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Создание клавиатуры
main_keyboard = ReplyKeyboardMarkup([
    ["📖 Слово дня", "❓ Викторина"],
    ["🔊 Произношение", "💬 Чат на английском"],
    ["🎲 Рандомное число", "⚙ Настройки"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для изучения английского. Выберите действие:", reply_markup=main_keyboard)

async def send_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word_data = random.choice(WORDS)
    text = f"🔹 Слово дня: *{word_data['word']}*\nПеревод: _{word_data['translation']}_\nПример: {word_data['example']}"
    
    tts = gTTS(word_data["word"], lang="en")
    tts.save("word.mp3")
    
    await update.message.reply_text(text, parse_mode="Markdown")
    with open("word.mp3", "rb") as voice_file:
        await update.message.reply_voice(voice=voice_file)
    os.remove("word.mp3")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word_data = random.choice(WORDS)
    context.user_data['quiz_word'] = word_data
    await update.message.reply_text(f"Как переводится слово: {word_data['word']}? Напишите ответ.")
    return QUIZ

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.lower()
    correct_answer = context.user_data['quiz_word']['translation'].lower()
    if user_answer == correct_answer:
        await update.message.reply_text("Правильно! 🎉")
    else:
        await update.message.reply_text(f"Неправильно. Правильный ответ: {correct_answer}")
    return ConversationHandler.END

async def pronunciation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split(" ", 1)
    if len(text) == 1:
        await update.message.reply_text("Введите слово после команды.")
        return
    word = text[1]
    tts = gTTS(word, lang="en")
    tts.save("pronounce.mp3")
    with open("pronounce.mp3", "rb") as voice_file:
        await update.message.reply_voice(voice=voice_file)
    os.remove("pronounce.mp3")

async def language_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начинаем чат на английском! Напишите что-нибудь.")
    return CHAT

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Интересно! Расскажи больше.")
    return CHAT

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здесь будут настройки бота (в будущем).")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Доступные команды:
📖 Слово дня - Получить новое слово дня
❓ Викторина - Проверить знания
🔊 Произношение - Озвучить слово
💬 Чат на английском - Общение на английском
🎲 Рандомное число - Получить случайное число
⚙ Настройки - Настроить бота"""
    await update.message.reply_text(help_text, reply_markup=main_keyboard)

async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    await update.message.reply_text(f"🎲 Тебе выпало число: {number}")

# ✅ Обработчик текстовых кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📖 Слово дня":
        await send_word(update, context)
    elif text == "❓ Викторина":
        await quiz(update, context)
    elif text == "🔊 Произношение":
        await update.message.reply_text("Введите слово после команды /pronunciation слово")
    elif text == "💬 Чат на английском":
        await language_practice(update, context)
    elif text == "🎲 Рандомное число":
        await random_number(update, context)
    elif text == "⚙ Настройки":
        await settings(update, context)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wordoftheday", send_word))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("pronunciation", pronunciation))
    app.add_handler(CommandHandler("languagepractice", language_practice))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("random", random_number))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz)],
        states={
            QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)

    # ✅ Добавляем обработчик кнопок
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
