import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main' # Устанавливаем режим диалога на "главное меню"
    text = load_message('main') # Загружаем текст для главного меню
    await send_image(update, context, 'main') # Отправляем изображение для главного меню
    await send_text(update, context, text)  # Отправляем текст для главного меню
    await show_main_menu(update, context, {  # Отображаем главное меню с кнопками
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

# Обработчик команды /random
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt("random") # Загружаем промпт для генерации случайного факта
    message = load_message("random") # Загружаем сообщение для случайного факта
    await send_image(update,context, "random")  # Отправляем изображение для случайного факта
    message = await send_text(update, context, message) # Отправляем сообщение для случайного факта
    answer = await chatgpt.send_question(prompt,"") # Генерируем случайный факт с помощью ChatGPT
    await message.edit_text(answer)  # Обновляем сообщение сгенерированным фактом

# Обработчик команды /gpt
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "gpt"  # Устанавливаем режим диалога на "ChatGPT"
    prompt = load_prompt("gpt")  # Загружаем промпт для ChatGPT
    message = load_message("gpt")  # Загружаем сообщение для ChatGPT
    chatgpt.set_prompt(prompt)  # Устанавливаем промпт для ChatGPT
    await send_image(update, context, "gpt")  # Отправляем изображение для ChatGPT
    await send_text(update, context, "Задай вопрос *ChatGPT*.")  # Отправляем сообщение с просьбой задать вопрос

# Обработчик диалога с ChatGPT
async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text  # Получаем текст сообщения пользователя
    message = await send_text(update, context, "Думаю над вопросом...")  # Отправляем сообщение о том, что бот думает
    answer = await chatgpt.add_message(text)  # Генерируем ответ с помощью ChatGPT
    await send_text(update, context, answer)  # Отправляем ответ пользователю

# Обработчик текстовых сообщений
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == "gpt": # Если режим "ChatGPT", обрабатываем диалог с ChatGPT
        await gpt_dialog(update, context)
    elif dialog.mode == "talk":  # Если режим "talk", обрабатываем диалог с известной личностью
        await talk_dialog(update, context)
    elif dialog.mode == "quiz":  # Если режим "quiz", обрабатываем диалог с квизом
        await quiz_answer(update, context)
    elif dialog.mode == "translator":  # Если режим "translator", обрабатываем диалог с переводчиком
        await translator_dialog(update, context)
    elif dialog.mode == "vocabulary":  # Если режим "vocabulary", обрабатываем диалог с тренажером словаря
        await vocabulary_dialog(update, context)
    else:
        await start(update, context)  # Если режим не установлен, возвращаемся в главное меню

# Обработчик команды /talk
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "talk"  # Устанавливаем режим диалога на "talk"
    text = load_message("talk")  # Загружаем сообщение для режима "talk"
    await send_image(update, context, "talk")  # Отправляем изображение для режима "talk"
    await send_text_buttons(update, context, text, {  # Отображаем кнопки с выбором личности
        "talk_cobain": "Курт Кобейн",
        "talk_hawking": "Стивен Хокинг",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_queen": "Королева Елизавета II",
        "talk_tolkien": "Джон Толкиен"
    })


# Обработчик диалога с известной личностью
async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text  # Получаем текст сообщения пользователя
    my_message = await send_text(update, context, "Набираю текст...")  # Отправляем сообщение о том, что бот набирает текст
    answer = await chatgpt.add_message(text)  # Генерируем ответ с помощью ChatGPT
    await my_message.edit_text(answer)  # Обновляем сообщение сгенерированным ответом

# Обработчик нажатия на кнопку выбора личности
async def talk_button(update, context):
    query = update.callback_query.data  # Получаем данные нажатой кнопки
    await update.callback_query.answer()  # Подтверждаем нажатие кнопки

    await send_image(update, context, query)  # Отправляем изображение выбранной личности
    text = load_prompt(query)   # Загружаем промпт для выбранной личности


    prompt = load_prompt(query)  # Загружаем промпт для выбранной личности
    chatgpt.set_prompt(prompt)  # Устанавливаем промпт для выбранной личности



# Обработчик команды /quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "quiz"  # Устанавливаем режим диалога на "quiz"
    context.user_data['quiz_score'] = 0
    text = load_message("quiz")  # Загружаем сообщение для режима "quiz"
    await send_image(update, context, "quiz")  # Отправляем изображение для режима "quiz"
    await send_text_buttons(update, context, text, {  # Отображаем кнопки с выбором темы квиза
        "quiz_prog": "Программирование",
        "quiz_math": "Математика",
        "quiz_biology": "Биология"

    })


# Обработчик нажатия на кнопку выбора темы квиза
async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query.data  # Получаем данные нажатой кнопки
    await update.callback_query.answer()  # Подтверждаем нажатие кнопки

    if query == "quiz_more":
        prompt = context.user_data['quiz_prompt']  # Если выбрана кнопка "еще вопрос", используем сохраненный промпт
    else:
        prompt = load_prompt(query)  # Иначе загружаем промпт для выбранной темы
        context.user_data['quiz_prompt'] = prompt  # Сохраняем промпт в контексте

    # Генерация вопроса
    question = await chatgpt.send_question(prompt, "")  # Генерируем вопрос с помощью ChatGPT
    await send_text(update, context, question)  # Отправляем вопрос пользователю

    # Ожидание ответа пользователя
    context.user_data['quiz_question'] = question  # Сохраняем вопрос в контексте

# Обработчик ответа на вопрос квиза
async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text  # Получаем текст ответа пользователя
    question = context.user_data.get('quiz_question', '')  # Получаем сохраненный вопрос
    prompt = context.user_data.get('quiz_prompt', '')  # Получаем сохраненный промпт

    # Проверка ответа
    result = await chatgpt.send_question(prompt, user_answer)  # Генерируем результат проверки ответа с помощью ChatGPT
    await send_text(update, context, result)  # Отправляем результат пользователю

    # Обновление счета
    if "Правильно!" in result:
        context.user_data['quiz_score'] = context.user_data.get('quiz_score', 0) + 1  # Увеличиваем счет, если ответ правильный

    # Отображение счета
    quiz_score = context.user_data.get('quiz_score', 0)
    await send_text(update, context, f"Счет: {quiz_score}")

    # Предложение задать еще вопрос
    await send_text_buttons(update, context, "Хотите задать еще вопрос?", {  # Отображаем кнопку для запроса нового вопроса
        "quiz_more": "Задать еще вопрос"
    })

# Обработчик команды /translator
async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'translator'   # Устанавливаем режим диалога на "translator"
    text = "Выберите язык перевода:"   # Текст для выбора языка перевода
    await send_text_buttons(update, context, text, { # Отображаем кнопки с выбором языка
        "translator_en": "Английский",
        "translator_es": "Испанский",
        "translator_fr": "Французский",
        "translator_de": "Немецкий",
        "translator_ru": "Русский"
    })

# Обработчик нажатия на кнопку выбора языка перевода
async def translator_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query.data  # Получаем данные нажатой кнопки
    await update.callback_query.answer()  # Подтверждаем нажатие кнопки

    selected_language = query.split('_')[-1]  # Извлекаем выбранный язык
    context.user_data['selected_language'] = selected_language  # Сохраняем выбранный язык в контексте

    await update.callback_query.edit_message_text(text=f"Выбран язык: {selected_language}. Теперь отправьте текст для перевода.")  # Обновляем сообщение с выбранным языком

# Обработчик диалога с переводчиком
async def translator_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'selected_language' in context.user_data:  # Проверяем, выбран ли язык перевода
        text_to_translate = update.message.text  # Получаем текст для перевода
        selected_language = context.user_data['selected_language']  # Получаем выбранный язык

        prompt = f"Translate the following text to {selected_language}: {text_to_translate}"  # Формируем промпт для перевода
        message = await send_text(update, context, "Перевожу текст...")  # Отправляем сообщение о том, что бот переводит текст
        answer = await chatgpt.send_question(prompt, "")  # Генерируем перевод с помощью ChatGPT
        await message.edit_text(f"Перевод: {answer}")   # Обновляем сообщение с переводом
    else:
        await send_text(update, context, "Пожалуйста, сначала выберите язык перевода командой /translator.")  # Если язык не выбран, просим выбрать язык

# Обработчик команды /vocabulary
async def vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'vocabulary'  # Устанавливаем режим диалога на "vocabulary"
    text = "Генерирую новое слово с переводом и примерами использования..."  # Текст для генерации нового слова
    await send_text(update, context, text)  # Отправляем сообщение о генерации нового слова

    # Используем ChatGPT для генерации нового слова с переводом и примерами
    prompt = "Generate a new word in English with its translation in Russian and examples of usage in sentences."  # Промпт для генерации нового слова
    answer = await chatgpt.send_question(prompt, "")  # Генерируем новое слово с помощью ChatGPT

    await send_text(update, context, answer)  # Отправляем сгенерированное слово пользователю


# Инициализация объекта диалога
dialog = Dialog()
dialog.mode = None
# Переменные можно определить, как атрибуты dialog
# Инициализация сервиса ChatGPT
chatgpt = ChatGptService("gpt:AEsXreIXcwEiqqkD3eqScgeFrtd_ekSvJdr_NdzFBAo8OOjyKzxVnawoToLoocydzuE9DANycYJFkblB3Tx4YlskdQhQ_4BrXR3QJe51XzgOOMFi0WErBAGuStCjy4Sq51AcQ3AnJI__P9LZvmzxEsF_oSgh")
# Инициализация приложения Telegram
app = ApplicationBuilder().token(
    "7440331197:AAF5Mqwot5kQRxlZ3cdz1B7Cffv84eeuf2Y").build()

# Регистрация обработчиков команд
app.add_handler(CommandHandler('start', start))  # Обработчик команды /start
app.add_handler(CommandHandler("gpt", gpt))  # Обработчик команды /gpt
app.add_handler(CommandHandler("random", random))  # Обработчик команды /random
app.add_handler(CommandHandler("talk", talk))  # Обработчик команды /talk
app.add_handler(CommandHandler("quiz", quiz))   # Обработчик команды /quiz
app.add_handler(CommandHandler('translator', translator))  # Обработчик команды /translator
app.add_handler(CommandHandler("vocabulary", vocabulary))  # Обработчик команды /vocabulary
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # Обработчик текстовых сообщений
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern="^quiz_.*"))
app.add_handler(CallbackQueryHandler(talk_button, pattern="^talk_.*"))
app.add_handler(CallbackQueryHandler(translator_button, pattern="^translator_.*"))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
