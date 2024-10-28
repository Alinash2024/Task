import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'translator': 'Переводчик 🌐',
        'vocabulary': 'Тренажер словаря 📚'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })


async def random(update, context):
    prompt = load_prompt("random")
    message = load_message("random")
    await send_image(update,context, "random")
    message = await send_text(update, context, message)
    answer = await chatgpt.send_question(prompt,"")
    await message.edit_text(answer)

async def gpt(update, context):
    dialog.mode = "gpt"
    prompt = load_prompt("gpt")
    message = load_message("gpt")
    chatgpt.set_prompt(prompt)
    await send_image(update, context, "gpt")
    await send_text(update, context, "Задай вопрос *ChatGPT*.")


async def gpt_dialog(update, context):
    text = update.message.text
    message = await send_text(update, context, "Думаю над вопросом...")
    answer = await chatgpt.add_message(text)
    await send_text(update, context, answer)

async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "talk":
        await talk_dialog(update, context)
    elif dialog.mode == "quiz":
        await quiz_dialog(update, context)
    elif dialog.mode == "translator":
        await translator_dialog(update, context)
    elif dialog.mode == "vocabulary":
        await vocabulary_trainer_dialog(update, context)
    else:
        await start(update, context)


async def talk(update, context):
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_hawking": "Стивен Хокинг",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_queen": "Королева Елизавета II",
        "talk_tolkien": "Джон Толкиен"
    })

async def talk_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Набираю текст...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_image(update, context, query)
    text = load_prompt(query)
    await send_text(update, context, text)

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def quiz(update, context):
    dialog.mode = "quiz"
    text = load_message("quiz")
    await send_image(update, context, "quiz")
    await send_text_buttons(update, context, text, {
        "quiz_prog": "Программирование",
        "quiz_math": "Математика",
        "quiz_biology": "Биология"
    })

async def quiz_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Проверяю ответ...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def quiz_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    if query == "quiz_more":
        prompt = context.user_data['quiz_prompt']
    else:
        prompt = load_prompt(query)
        context.user_data['quiz_prompt'] = prompt

    # Генерация вопроса
    question = await chatgpt.send_question(prompt, "")
    await send_text(update, context, question)

    # Ожидание ответа пользователя
    context.user_data['quiz_question'] = question


async def quiz_answer(update, context):
    user_answer = update.message.text
    question = context.user_data['quiz_question']
    prompt = context.user_data['quiz_prompt']

    # Проверка ответа
    result = await chatgpt.send_question(prompt, user_answer)
    await send_text(update, context, result)

    # Обновление счета
    if "Правильно!" in result:
        context.user_data['quiz_score'] = context.user_data.get('quiz_score', 0) + 1

    # Отображение счета
    score_message = f"Счет: {context.user_data.get('quiz_score', 0)}"
    await send_text(update, context, score_message)

    # Предложение задать еще вопрос
    await send_text_buttons(update, context, "Хотите задать еще вопрос?", {
        "quiz_more": "Задать еще вопрос"
    })

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'translator'
    text = "Выберите язык перевода:"
    await send_text_buttons(update, context, text, {
        "translator_en": "Английский",
        "translator_es": "Испанский",
        "translator_fr": "Французский",
        "translator_de": "Немецкий",
        "translator_ru": "Русский"
    })

async def translator_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query.data
    await update.callback_query.answer()

    selected_language = query.split('_')[-1]
    context.user_data['selected_language'] = selected_language

    await update.callback_query.edit_message_text(text=f"Выбран язык: {selected_language}. Теперь отправьте текст для перевода.")

async def translator_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'selected_language' in context.user_data:
        text_to_translate = update.message.text
        selected_language = context.user_data['selected_language']

        prompt = f"Translate the following text to {selected_language}: {text_to_translate}"
        message = await send_text(update, context, "Перевожу текст...")
        answer = await chatgpt.send_question(prompt, "")
        await message.edit_text(f"Перевод: {answer}")
    else:
        await send_text(update, context, "Пожалуйста, сначала выберите язык перевода командой /translator.")

async def vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'vocabulary'
    text = "Генерирую новое слово с переводом и примерами использования..."
    await send_text(update, context, text)

    # Используем ChatGPT для генерации нового слова с переводом и примерами
    prompt = "Generate a new word in English with its translation in Russian and examples of usage in sentences."
    answer = await chatgpt.send_question(prompt, "")

    await send_text(update, context, answer)



dialog = Dialog()
dialog.mode = None
# Переменные можно определить, как атрибуты dialog

chatgpt = ChatGptService("gpt:AEsXreIXcwEiqqkD3eqScgeFrtd_ekSvJdr_NdzFBAo8OOjyKzxVnawoToLoocydzuE9DANycYJFkblB3Tx4YlskdQhQ_4BrXR3QJe51XzgOOMFi0WErBAGuStCjy4Sq51AcQ3AnJI__P9LZvmzxEsF_oSgh")
app = ApplicationBuilder().token(
    "7440331197:AAF5Mqwot5kQRxlZ3cdz1B7Cffv84eeuf2Y").build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler('translator', translator))
app.add_handler(CommandHandler("vocabulary", vocabulary))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern="^quiz_.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
app.add_handler(CallbackQueryHandler(translator_button, pattern="^translator_.*"))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
