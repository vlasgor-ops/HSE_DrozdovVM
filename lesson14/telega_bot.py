import logging
from telegram import Updater, CommandHandler, MessageHandler
from telegram.ext.dispatcher import Filters

# Настройки бота @HSE_DrozdovVM_bot
TOKEN = '6123644283:AAERshzHEX8P19iIDqgWyWTQnIapR6MeOew'
MENU = [
    [KeyboardButton('Раздел 1')],
    [KeyboardButton('Раздел 2')],
    [KeyboardButton('Раздел 3')]
]

# Настройки логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция обработки команды /start
def start(update, context):
    reply_markup = ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    update.message.reply_text('Добро пожаловать! Выберите раздел:', reply_markup=reply_markup)

# Функции обработки выбора раздела
def section1(update, context):
    update.message.reply_text('Раздел 1: Lorem Ipsum')

def section2(update, context):
    update.message.reply_text('Раздел 2: Lorem Ipsum')

def section3(update, context):
    update.message.reply_text('Раздел 3: Lorem Ipsum')

# Функция обработки неизвестных команд
def unknown(update, context):
    update.message.reply_text('Извините, я не понимаю эту команду.')

# Основная функция, запускающая бота
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))

    # Обработчики разделов
    dp.add_handler(MessageHandler(Filters.regex('^Раздел 1$'), section1))
    dp.add_handler(MessageHandler(Filters.regex('^Раздел 2$'), section2))
    dp.add_handler(MessageHandler(Filters.regex('^Раздел 3$'), section3))

    # Обработчик неизвестных команд
    dp.add_handler(MessageHandler(Filters.text, unknown))

    # Запуск бота
    updater.start_polling()
    logger.info("Бот запущен.")
    updater.idle()

if __name__ == '__main__':
    main()
