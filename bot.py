import telebot
from config import *
from logic import *
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды: 
/start - запуск бота
/show_city (city_name) - показывает город на карте
/remember_city (city_name) - запомнить этот город на карте
/show_my_cities - показать сохраненные города
/distance (city_name1) (city_name2) - показывает дистанцию между двумя городами
""")


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[1:]
    user_id = message.chat.id
    bot.send_message(user_id, 'Выберите цвет маркера на карте. (red, yellow, blue)')
    bot.register_next_step_handler(message, handle_step_2, city_name=city_name)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    city_name = manager.select_cities(user_id)
    bot.send_message(user_id, 'Выберите цвет маркера на карте. (red, yellow, blue)')
    bot.register_next_step_handler(message, handle_step_2, city_name=city_name)

@bot.message_handler(commands=['distance'])
def handle_distance(message):
    user_id = message.chat.id
    cities = message.text.split()[1:]
    if len(cities) == 2:
        city_name1, city_name2 = cities
        manager.draw_distance(city_name1, city_name2)
        with open('distance_map.png', 'rb') as map:
            bot.send_photo(user_id, map) 
    else:
        bot.send_message(message.chat.id, 'Введите два разных города.')
    


def handle_step_2(message, city_name):
    color = message.text
    user_id = message.chat.id
    manager.create_grapf(color, city_name)
    with open('city.png', 'rb') as map:
        bot.send_photo(user_id, map) 


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
