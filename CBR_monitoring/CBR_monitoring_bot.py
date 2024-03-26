import logging
import sqlite3
import csv
import os
import re

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler

# Устанавливаем соединение с базой данных (если ее нет, то она будет создана)
conn = sqlite3.connect('debtor_bot.db')
cursor = conn.cursor()

# Создаем таблицу пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE
    )
''')

# Создаем таблицу должников
cursor.execute('''
    CREATE TABLE IF NOT EXISTS debtors (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        debtor_name_legal TEXT,
        debtor_inn_legal TEXT,
        debtor_name_individual TEXT,
        debtor_inn_individual TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Применяем изменения к базе данных
conn.commit()

# Уровни разговора
START, ENTER_EMAIL, INDIVIDUAL_OR_GROUP, INDIVIDUAL_NAME, INDIVIDUAL_INN, GROUP_UPLOAD = range(6)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция начала работы с ботом
def start(update, context):
    update.message.reply_text("Добро пожаловать в бот для мониторинга должников Банка России! "
                              "Для начала вам необходимо указать свой рабочий адрес электронный почты, "
                              "на который вам будут приходить результаты мониторинга")
    return ENTER_EMAIL

# Функция для ввода адреса электронной почты
def enter_email(update, context):
    email = update.message.text

    # Проверка формата email
    if not validate_email(email):
        update.message.reply_text("Неверный формат email. Попробуйте еще раз.")
        return ENTER_EMAIL

    # Проверка на наличие email в базе данных
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        update.message.reply_text("Этот адрес электронной почты уже зарегистрирован. Пожалуйста, введите другой адрес.")
        return ENTER_EMAIL

    # Добавление пользователя в базу данных
    cursor.execute("INSERT INTO users (email) VALUES (?)", (email,))
    conn.commit()

    # Главное меню
    reply_keyboard = [['Индивидуальный', 'Групповой']]
    update.message.reply_text(
        "Адрес электронной почты успешно зарегистрирован.\nВыберите способ загрузки данных о должниках:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return INDIVIDUAL_OR_GROUP

# Валидация формата email
def validate_email(email):
    # Шаблон для проверки формата email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Функция выбора способа загрузки данных о должниках
def individual_or_group(update, context):
    choice = update.message.text

    if choice == 'Индивидуальный':
        update.message.reply_text("Введите наименование (ФИО) должника:")
        return INDIVIDUAL_NAME
    elif choice == 'Групповой':
        update.message.reply_text("Загрузите csv файл с данными о должниках.")
        return GROUP_UPLOAD
    else:
        update.message.reply_text("Пожалуйста, выберите способ загрузки данных: Индивидуальный или Групповой.")
        return INDIVIDUAL_OR_GROUP

# Функция для обработки ввода наименования (ФИО) должника
def enter_name(update, context):
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text("Введите ИНН должника:")
    return INDIVIDUAL_INN


# Функция для обработки ввода ИНН должника
def enter_inn(update, context):
    inn = update.message.text

    # Проверка корректности ИНН
    if not validate_inn(inn):
        update.message.reply_text("Некорректный ИНН. Пожалуйста, введите правильный ИНН.")
        return INDIVIDUAL_INN

    # Запись данных в базу данных
    user_id = get_user_id(update.message.from_user.id)
    name = context.user_data['name']
    cursor.execute("INSERT INTO debtors (user_id, name, inn) VALUES (?, ?, ?)", (user_id, name, inn))
    conn.commit()

    # Предложение добавить еще одного должника или вернуться в главное меню
    reply_keyboard = [['Добавить еще одного должника', 'Главное меню']]
    update.message.reply_text(
        "Данные о должнике успешно добавлены.\nЧто вы хотите сделать дальше?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END
def validate_inn(inn, update=None):
# Проверяем, что ИНН состоит из 10 или 12 цифр и является числом
    if not (inn.isdigit() and (len(inn) == 10 or len(inn) == 12)):
        return False
        # Дополнительная проверка на корректность контрольных цифр для ИНН в России
    if len(inn) == 10:
        coefficients_10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        control_sum = sum(int(inn[i]) * coefficients_10[i] for i in range(9)) % 11 % 10
        return int(inn[9]) == control_sum
    elif len(inn) == 12:
        coefficients_12_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        coefficients_12_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        control_sum_1 = sum(int(inn[i]) * coefficients_12_1[i] for i in range(10)) % 11 % 10
        control_sum_2 = sum(int(inn[i]) * coefficients_12_2[i] for i in range(11)) % 11 % 10
        return int(inn[10]) == control_sum_1 and int(inn[11]) == control_sum_2

# Функция для загрузки групповых данных о должниках
def group_upload(update, context):
    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)
    file.download('debtor_data.csv')

    # Чтение данных из CSV файла и их запись в базу данных
    with open('debtor_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name, inn = row
            if validate_inn(inn):
                user_id = get_user_id(update.message.from_user.id)
                cursor.execute("INSERT INTO debtors (user_id, name, inn) VALUES (?, ?, ?)", (user_id, name, inn))
        conn.commit()

        # Удаление временного CSV файла
    os.remove('debtor_data.csv')

    update.message.reply_text("Данные о должниках успешно загружены.")
    return ConversationHandler.END


# Функция для получения ID пользователя из базы данных или создания новой записи
def get_user_id(telegram_id):
    cursor.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    user_id = cursor.fetchone()
    if not user_id:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
        user_id = cursor.fetchone()
    return user_id[0]


# Функция валидации ИНН
def validate_inn(inn):
    # Здесь может быть более сложная проверка ИНН
    return len(inn) in [10, 12] and inn.isdigit()


# Функция для обработки команды "Главное меню"
def main_menu(update, context):
    reply_keyboard = [['Редактирование записей', 'Удаление записей'],
                      ['Мониторинг ЕГРЮЛ', 'Мониторинг ЕФРСБ', 'Мониторинг kad.arbitr'],
                      ['Запуск всех скриптов', 'Выгрузка всех записей в CSV']]
    update.message.reply_text(
        "Главное меню",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END


# Функция main() для запуска бота
def main():
    # Создаем экземпляр бота, передавая ему токен
    bot = Bot(token='7104961986:AAGjmddHZwvRykFr4IfRCOWiK9U9XeOKrg4')

    # Добавим обработчики команд и создадим экземпляр ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_email)],
            INDIVIDUAL_OR_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, individual_or_group)],
            INDIVIDUAL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            INDIVIDUAL_INN: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_inn)],
            GROUP_UPLOAD: [MessageHandler(filters.Document.DOC, group_upload)]
        },
        fallbacks=[CommandHandler('main_menu', main_menu)]
    )

    # Создаем экземпляр обновления, передавая бота
    updater = Updater(bot=bot, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчик
    dispatcher.add_handler(conv_handler)

    # Добавляем обработчики команд для главного меню
    dispatcher.add_handler(CommandHandler('main_menu', main_menu))

    # Запуск бота
    updater.start_polling()
    updater.idle()


# Запуск функции main() при запуске скрипта
if __name__ == '__main__':
    main()


