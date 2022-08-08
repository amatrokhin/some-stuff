import telebot
from config import curs, TOKEN
from extentions import APIException, CurrencyConverter

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):               #general info
    text = 'Чтобы начать работу введите команду боту в следующем формате:\n' \
           '<инициалы валюты (например USD/usd)>' \
           '<в какую валюту перевести> <количество переводимой валюты>\n' \
           'Увидеть список всех доступных валют: /values'           #I used 3 letter currency name here for conveniece
    bot.reply_to(message, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):             #show all currencies available
    text = 'Доступные валюты: '

    for key, val in curs.items():
        currency = key + ': ' + val
        text = '\n'.join((text, currency, ))

    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):            #conver 1st value into 2nd
    try:
        values = message.text.split(' ')

        if len(values) > 3:
            raise APIException('Слишком много параметров')
        if len(values) < 3:
            raise APIException('Слишком мало параметров')

        base, quote, amount = values
        total_quote = CurrencyConverter.get_price(base, quote, amount)

    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')

    else:
        text = f'Цена {amount} {base.upper()} в {quote.upper()} - {total_quote}'
        bot.send_message(message.chat.id, text)

bot.polling()