import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ПЕРЕМЕННЫЕ ДЛЯ ХРАНЕНИЯ ДАННЫХ

# Уравнения для разных уровней
basic_eq = [
    {'equation': 'x² - 5x + 6 = 0', 'answer': '2, 3', 'steps': 5},
    {'equation': 'x² + 4x + 3 = 0', 'answer': '-1, -3', 'steps': 5}
]
medium_eq = [
    {'equation': '2x² - 7x + 3 = 0', 'answer': '0.5, 3'},
    {'equation': 'x² - 6x + 9 = x - 3', 'answer': '3, 4'},
    {'equation': 'x² - 20x - 69 = 0', 'answer': '-3, 23'},
    {'equation': '(11 + x)(14 + x) = 304', 'answer': '-30, 5'}
]
pro_eq = [
    {'equation': 'x⁴ - 3x² - 4 = 0', 'answer': '-2, 2'},
    {'equation': ' \n 2x - 1    7x - 1\n─────── = ───────\n x - 1     2x + 2', 'answer': '3'},
    {'equation': '(x−2)² + 2x = 7(x−2)', 'answer': '3, 6'}
]

# Варианты ответов для среднего уровня
answers_medium = {
    0: ["-1, 0", "0.5, 3", "-2, 2"],
    1: ["3, 4", "-8, 4", "-6, 5"],
    2: ["3, 23", "-3, 23", "5, 23"],
    3: ["-26", "5, 20", "-30, 5"]
}

# Статистика пользователей (хранится в памяти)
user_stats = {}

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

# Получить статистику пользователя
def get_user_statistics(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {
            'total': 0,
            'correct': 0,
            'incorrect': 0
        }
    return user_stats[user_id]

# Сохранить результат решения
def save_statistics(user_id, is_correct):
    stats = get_user_statistics(user_id)
    stats['total'] += 1
    if is_correct:
        stats['correct'] += 1
    else:
        stats['incorrect'] += 1

# Создать главное меню с кнопками
def create_main_menu():
    buttons = [
        [KeyboardButton("Теория")],
        [KeyboardButton("Тренажер")],
        [KeyboardButton("Статистика")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ОСНОВНЫЕ КОМАНДЫ БОТА

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user_statistics(user_id)  # Создаем запись в статистике

    text = "👋 Привет! Я бот для тренировки навыков решения квадратных уравнений.\n\nВыберите действие:"
    await update.message.reply_text(text, reply_markup=create_main_menu())

# Обработка нажатий кнопок главного меню
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_text = update.message.text

    if button_text == "Теория":
        await show_theory(update, context)
    elif button_text == "Тренажер":
        await show_practice(update, context)
    elif button_text == "Статистика":
        await show_statistics(update, context)

# Показать раздел теории
async def show_theory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📚 *Квадратные уравнения*

Квадратные уравнения — это уравнения вида ax² + bx + c = 0, где коэффициенты a, b, c — это некоторые числа, причём a ≠ 0.

Решить квадратное уравнение — это значит найти все его корни или установить, что корней нет.

👇 *Состав справочника:*
    """

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Формулы", callback_data='theory_formulas')],
        [InlineKeyboardButton("Алгоритм с дискриминантом", callback_data='theory_algorithm')],
        [InlineKeyboardButton("Алгоритм с теоремой Виета", callback_data='theory_viet')]
    ])

    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=buttons)

# Показать меню выбора уровня
async def show_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Базовый", callback_data='level_basic')],
        [InlineKeyboardButton("📖 Средний", callback_data='level_medium')],
        [InlineKeyboardButton("🎯 Профи", callback_data='level_pro')]
    ])

    await update.message.reply_text("*Выберите уровень решения уравнений:*", parse_mode='Markdown',
                                    reply_markup=buttons)

# Показать статистику пользователя
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats = get_user_statistics(user.id)

    text = f"""
📊 *Статистика пользователя*

Всего решено: {stats['total']}
✅ Верно: {stats['correct']}
❌ Неверно: {stats['incorrect']}
    """

    await update.message.reply_text(text, parse_mode='Markdown')

# ФУНКЦИИ ДЛЯ ПРАКТИКИ

# Показать уравнение для решения
async def show_equation(query, level, eq_index, context):
    # Выбираем уравнение в зависимости от уровня
    if level == 'basic':
        eq_data = basic_eq[eq_index]
    elif level == 'medium':
        eq_data = medium_eq[eq_index]
    else:
        eq_data = pro_eq[eq_index]

    equation = eq_data['equation']
    answer = eq_data['answer']

    # Сохраняем данные для проверки
    context.user_data['current_level'] = level
    context.user_data['current_eq'] = eq_index
    context.user_data['correct_answer'] = answer

    # Создаем интерфейс для разных уровней
    if level == 'basic':
        text = f"*Базовый уровень*\n\n✏️ `{equation}`\n\nНажмите на шаг решения:"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Шаг 1: Коэффициенты уравнения", callback_data=f'step_1_{eq_index}')],
            [InlineKeyboardButton("Шаг 2: Дискриминант", callback_data=f'step_2_{eq_index}')],
            [InlineKeyboardButton("Шаг 3: Корни уравнения", callback_data=f'step_3_{eq_index}')],
            [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')],
            [InlineKeyboardButton("➡️ Следующий пример", callback_data='next_eq')]
        ])

    elif level == 'medium':
        text = f"*Средний уровень*\n\n✏️ `{equation}`\n\nВыберите правильный ответ:"

        # Создаем кнопки с вариантами ответов
        options = answers_medium[eq_index]
        button_rows = []
        for i, option in enumerate(options):
            button_rows.append([InlineKeyboardButton(option, callback_data=f'medium_{eq_index}_{i}')])

        button_rows.append([
            InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu'),
            InlineKeyboardButton("➡️ Следующее", callback_data='next_eq')
        ])
        buttons = InlineKeyboardMarkup(button_rows)

    else:  # pro уровень
        text = f"*Уровень профи*\n\n✏️ `{equation}`\n\n*Напишите корни в чат через запятую в порядке возрастания:*\n"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')],
            [InlineKeyboardButton("➡️ Следующий пример", callback_data='next_eq')]
        ])
    await query.message.reply_text(text, parse_mode='Markdown', reply_markup=buttons)

# Показать шаг решения для базового уровня
async def handle_step_button(query, context, step_num, eq_index):
    eq_data = basic_eq[eq_index]
    if step_num == '1':
        # Шаг 1: Kоэффициенты
        text = "*Шаг 1: Найдем коэффициенты данного уравнения*\n\n"
        if eq_data['equation'] == 'x² - 5x + 6 = 0':
            text += "a = 1, b = -5, c = 6"
        elif eq_data['equation'] == 'x² + 4x + 3 = 0':
            text += "a = 1, b = 4, c = 3"

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("➡️ Далее: Дискриминант", callback_data=f'step_2_{eq_index}')]])

    elif step_num == '2':
        # Шаг 2: дискриминант
        text = "*Шаг 2: Дискриминант равен*\n\n"
        if eq_data['equation'] == 'x² - 5x + 6 = 0':
            text += "D = b² - 4ac = (-5)² - 4×1×6 = 25 - 24 = 1\n\n"
            text += "D>0, значит у данного уравнения два корня."
        elif eq_data['equation'] == 'x² + 4x + 3 = 0':
            text += "D = b² - 4ac = 4² - 4×1×3 = 16 - 12 = 4\n\n"
            text += "D>0, значит у данного уравнения два корня."

        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Далее: Корни", callback_data=f'step_3_{eq_index}')]])

    elif step_num == '3':
        # Шаг 3: корни
        text = "*Шаг 3: Вычисляем корни*\n\n"
        text += "               -b ± √D\n"
        text += "x₁,₂ =   ─────\n"
        text += "                  2a\n\n"
        if eq_data['equation'] == 'x² - 5x + 6 = 0':
            text += "x₁ = (-b - √D) / 2a \n\n"
            text += "           5 - 1\n"
            text += "x₁ = ──── = 2\n"
            text += "            2×1\n\n"
            text += "x₂  = (-b + √D) / 2a\n\n"
            text += "           5 + 1\n"
            text += "x₂ = ──── = 3\n"
            text += "            2×1\n\n"
            text += f"Oтвет: `{eq_data['answer']}`"
        elif eq_data['equation'] == 'x² + 4x + 3 = 0':
            text += "x₁ = (-b - √D) / 2a\n\n"
            text += "         -4 - √4\n"
            text += "x₁ = ──── = -3\n"
            text += "            2×1\n\n"
            text += "x₂  = (-b + √D) / 2a \n\n"
            text += "         -4 + √4\n"
            text += "x₂ = ──── = -1\n"
            text += "            2×1\n\n"
            text += f"Oтвет: `{eq_data['answer']}`"

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В меню", callback_data='back_to_menu')],
            [InlineKeyboardButton("➡️ Следующий пример", callback_data='next_eq')]
        ])

    await query.message.reply_text(text, parse_mode='Markdown', reply_markup=buttons)

# Проверить ответ для профи уровня
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text.strip()
    user_id = update.effective_user.id
    # Проверяем, находимся ли мы в режиме практики
    if 'current_level' not in context.user_data:
        return

    level = context.user_data.get('current_level', '')
    correct_answer = context.user_data.get('correct_answer', '')

    if not level or not correct_answer:
        return  # не в режиме практики

    if level == 'pro':
        # Для профи уровня
        user_clean = user_text.lower().replace(' ', '')
        correct_clean = correct_answer.lower().replace(' ', '')

        if user_clean == correct_clean:
            save_statistics(user_id, True)
            await update.message.reply_text("✅ Верно!")
        else:
            save_statistics(user_id, False)
            await update.message.reply_text(f"❌ Неверно. Правильный ответ: {correct_answer}")

# ОБРАБОТЧИК INLINE-КНОПОК
# Обработка нажатий inline-кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # ТЕОРИЯ
    if query.data == 'theory_formulas':
        formulas = """
*Основные формулы*

*Дискриминант:*
`D = b² - 4ac`

*Зависимость корней:*
• D > 0 → 2 разных корня
• D = 0 → 1 корень
• D < 0 → нет действительных корней

*Формула корней:*
`x₁,₂ = (-b ± √D) / 2a`

*Теорема Виета* (для a = 1):
`x² + px + q = 0`
`x₁ + x₂ = -p`
`x₁ × x₂ = q`
        """
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к теории", callback_data='back_to_theory')]])
        await query.edit_message_text(formulas, parse_mode='Markdown', reply_markup=buttons)

    elif query.data == 'theory_algorithm':
        # Пробуем отправить картинку с алгоритмом
        image_path = os.path.join('src', 'алгоритм.png')
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await query.message.reply_photo(photo, caption="*Алгоритм решения через дискриминант*",
                                                    parse_mode='Markdown')
            except:
                await query.message.reply_text("*Алгоритм решения через дискриминант*", parse_mode='Markdown')
        else:
            await query.message.reply_text("*Алгоритм решения через дискриминант*", parse_mode='Markdown')

        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к теории", callback_data='back_to_theory')]])
        await query.message.reply_text("Вернуться к теории:", reply_markup=buttons)

    elif query.data == 'theory_viet':
        # Пробуем отправить картинку с теоремой Виета
        image_path = os.path.join('src', 'виетта.png')
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await query.message.reply_photo(photo, caption="*Алгоритм решения через теорему Виета*",
                                                    parse_mode='Markdown')
            except:
                await query.message.reply_text("*Алгоритм решения через теорему Виета*", parse_mode='Markdown')
        else:
            await query.message.reply_text("*Алгоритм решения через теорему Виета*", parse_mode='Markdown')

        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к теории", callback_data='back_to_theory')]])
        await query.message.reply_text("Вернуться к теории:", reply_markup=buttons)

    elif query.data == 'back_to_theory':
        text = "📚 *Квадратные уравнения*\n\n👇 *Состав справочника:*"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Формулы", callback_data='theory_formulas')],
            [InlineKeyboardButton("Алгоритм с дискриминантом", callback_data='theory_algorithm')],
            [InlineKeyboardButton("Алгоритм с теоремой Виета", callback_data='theory_viet')]
        ])
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=buttons)

    # ПРАКТИКА
    elif query.data.startswith('level_'):
        # Выбор уровня
        level = query.data.split('_')[1]
        context.user_data['current_level'] = level
        context.user_data['current_eq'] = 0
        await show_equation(query, level, 0, context)

    elif query.data.startswith('step_'):
        # Шаги для базового уровня
        parts = query.data.split('_')
        step_num = parts[1]
        eq_index = int(parts[2]) if len(parts) > 2 else context.user_data.get('current_eq', 0)
        await handle_step_button(query, context, step_num, eq_index)

    elif query.data.startswith('medium_'):
        # Варианты ответов для среднего уровня
        parts = query.data.split('_')
        eq_index = int(parts[1])
        option_index = int(parts[2])
        user_id = query.from_user.id
        correct_answer = medium_eq[eq_index]['answer']
        user_choice = answers_medium[eq_index][option_index]

        if user_choice == correct_answer:
            # Обновляем статистику для правильного ответа
            save_statistics(user_id, True)
            # Если ответ правильный - отправляем сообщение
            await query.message.reply_text(
                f"✅ *Верно!*\n\nОтвет: `{correct_answer}`",
                parse_mode='Markdown'
            )
        else:
            # Обновляем статистику для неправильного ответа
            save_statistics(user_id, False)
            # Если ответ неправильный - отправляем сообщение и картинку с решением
            await query.message.reply_text(
                f"❌ *Неверно!*\n",
                parse_mode='Markdown'
            )

            # Пробуем отправить картинку с решением
            image_file = f"ответ{eq_index + 1}.png"
            image_path = os.path.join('src', image_file)
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as photo:
                        await query.message.reply_photo(
                            photo=photo,
                            caption=f"📝 *Решение уравнения*\n\nПравильный ответ: `{correct_answer}`",
                            parse_mode='Markdown'
                        )
                except:
                    await query.message.reply_text(f"📝 *Решение уравнения*\n\nПравильный ответ: `{correct_answer}`",
                                                   parse_mode='Markdown')
            else:
                await query.message.reply_text(f"📝 *Решение уравнения*\n\nПравильный ответ: `{correct_answer}`",
                                               parse_mode='Markdown')

    elif query.data == 'next_eq':
        # Следующее уравнение
        level = context.user_data.get('current_level', '')
        if not level:
            return

        eq_index = context.user_data.get('current_eq', 0) + 1

        # Проверяем, есть ли еще уравнения
        if level == 'basic' and eq_index < len(basic_eq):
            context.user_data['current_eq'] = eq_index
            await show_equation(query, level, eq_index, context)
        elif level == 'medium' and eq_index < len(medium_eq):
            context.user_data['current_eq'] = eq_index
            await show_equation(query, level, eq_index, context)
        elif level == 'pro' and eq_index < len(pro_eq):
            context.user_data['current_eq'] = eq_index
            await show_equation(query, level, eq_index, context)
        else:
            # Уравнения закончились
            await query.message.reply_text(
                "🎉 *Все уравнения решены!*",
                parse_mode='Markdown'
            )
            # Возвращаемся к выбору уровня
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Базовый", callback_data='level_basic')],
                [InlineKeyboardButton("📖 Средний", callback_data='level_medium')],
                [InlineKeyboardButton("🎯 Профи", callback_data='level_pro')]
            ])
            await query.message.reply_text("*Выберите уровень решения уравнений:*", parse_mode='Markdown', reply_markup=buttons)

    elif query.data == 'back_to_menu':
        # Возврат в меню выбора уровня
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Базовый", callback_data='level_basic')],
            [InlineKeyboardButton("📖 Средний", callback_data='level_medium')],
            [InlineKeyboardButton("🎯 Профи", callback_data='level_pro')]
        ])

        await query.message.reply_text(
            "*Выберите уровень решения уравнений:*",
            parse_mode='Markdown',
            reply_markup=buttons
        )

# ГЛАВНАЯ ФУНКЦИЯ
# Запуск бота
def main():
    with open('.env') as f:
        TOKEN = f.read().split('=')[1].strip()

    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("theory", show_theory))
    app.add_handler(CommandHandler("practice", show_practice))
    app.add_handler(CommandHandler("stats", show_statistics))

    # Добавляем обработчик кнопок меню
    app.add_handler(MessageHandler(filters.Text(["Теория", "Тренажер", "Статистика"]), handle_menu_buttons))

    # Добавляем обработчик inline-кнопок
    app.add_handler(CallbackQueryHandler(button_callback))

    # Добавляем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    # Запускаем бота
    print("Бот запускается...")
    app.run_polling()

if __name__ == "__main__":
    main()