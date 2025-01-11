from pyrogram import Client, filters
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time
import re

# Ваш API ID и API hash, полученные с my.telegram.org
api_id = "28307530"  # Замените на ваш API ID
api_hash = "1b5a6938325b67dc9d40cd3310d15064"  # Замените на ваш API hash

# Ваш номер телефона
phone_number = "+998915196670"  # Замените на ваш номер телефона

# Ваш Telegram ID (например, 123456789)
my_user_id = 366194347  # Замените на ваш ID

# Инициализация клиента Pyrogram
app = Client("my_user", api_id=api_id, api_hash=api_hash, phone_number=phone_number)

# Список доступных команд
commands_list = """
/weather <город> - Получить погоду в городе
/random_meme - Получить случайный мем
/get_members - Получить список всех участников
/random <num> - Получить случайных участников
/list - Список команд
/pasta <text> - Написать текст по одной букве
/emodzi - chekay bratishka
"""
# Проверка ID пользователя
def is_authorized(user_id):
    return user_id == my_user_id

# Команда для получения погоды по городу
@app.on_message(filters.command("weather"))
async def get_weather(client, message):
    if not is_authorized(message.from_user.id):
        return

    try:
        city = message.text.split(" ", 1)[1]  # Получаем город после команды
        api_key = "ec0fbd1cf7ba5f1eee7ed1a19010480f"  # Замените на свой ключ API OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:  # Проверка на ошибки от OpenWeatherMap
            await message.reply(f"Не удалось найти город '{city}'. Попробуйте еще раз.")
            return

        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        await message.reply(f"Погода в {city}: {weather}, {temp}°C")
    except IndexError:
        await message.reply("Пожалуйста, укажите город, например: /weather Москва")

# Функция для отправки случайного мемa
@app.on_message(filters.command("random_meme"))
async def send_random_meme(client, message):
    try:
        # Получаем случайный мем из Tenor API
        api_key = "LIVDSRZULELA"  # Замените на свой ключ API
        url = f"https://api.tenor.com/v1/search?q=random&key={api_key}&limit=10"  # Запросим 10 мемов
        response = requests.get(url)
        data = response.json()
        
        if not data['results']:  # Если нет результатов
            await message.reply("Не удалось получить мемы.")
            return
        
        # Выбираем случайный мем из результатов
        meme_url = random.choice(data['results'])['media'][0]['gif']['url']
        await message.reply(meme_url)
    except Exception as e:
        await message.reply(f"Произошла ошибка при получении мема: {e}")


# Функция для получения списка участников
@app.on_message(filters.command("get_members"))
async def get_all_members(client, message):
    if not is_authorized(message.from_user.id):
        return

    chat_id = message.chat.id
    members = []
    
    # Получаем участников чата
    async for member in app.get_chat_members(chat_id):
        username = member.user.username
        first_name = member.user.first_name
        user_id = member.user.id  # ID пользователя
        
        # Проверяем, что username или first_name не являются None
        if username:
            members.append(f"@{username}")
        elif first_name:
            members.append(f"{first_name} (ID: {user_id})")
        else:
            members.append(f"Без имени (ID: {user_id})")

    # Разбиваем текст на несколько частей, если он слишком длинный
    max_message_length = 4096  # Максимальная длина сообщения
    members_text = "\n".join(members)
    for i in range(0, len(members_text), max_message_length):
        await message.reply(members_text[i:i+max_message_length])

# Функция для случайного вывода участников
@app.on_message(filters.command("random"))
async def random_members(client, message):
    if not is_authorized(message.from_user.id):
        return

    # Извлекаем число из команды /random <num>
    try:
        num = int(message.text.split()[1])  # Получаем число после команды
    except (IndexError, ValueError):
        await message.reply("Пожалуйста, укажите количество участников (например, /random 5).")
        return

    chat_id = message.chat.id
    members = []
    
    # Получаем всех участников чата
    async for member in app.get_chat_members(chat_id):  
        username = member.user.username
        first_name = member.user.first_name
        user_id = member.user.id  # ID пользователя
        
        # Исключаем бота и @Refat_web_dev
        if username == "Refat_web_dev" or member.user.is_bot:
            continue
        
        # Проверяем, что username или first_name не являются None
        if username:
            members.append(f"@{username}")
        elif first_name:
            members.append(f"{first_name} (ID: {user_id})")
        else:
            members.append(f"Без имени (ID: {user_id})")
    
    # Если участников меньше, чем запрашиваемое количество, показываем всех
    if num > len(members):
        num = len(members)
    
    # Выбираем случайных участников
    random_members = random.sample(members, num)
    random_members_text = "\n".join(random_members)

    await message.reply(random_members_text)

# Функция для вывода списка команд
@app.on_message(filters.command("list"))
async def list_commands(client, message):
    if not is_authorized(message.from_user.id):
        return

    await message.reply(commands_list)

@app.on_message(filters.command("pasta"))
async def pasta(client, message):
    if not is_authorized(message.from_user.id):
        return

    try:
        # Разбираем команду на части
        command_parts = message.text.split(" ", 1)
        
        if len(command_parts) < 2:
            await message.reply("Пожалуйста, укажите текст для пасты, например: /pasta Hello")
            return
        
        # Разбираем параметры (если они есть)
        loop_count = 1  # По умолчанию без повтора
        text = command_parts[1]
        
        # Проверяем на наличие loop
        loop_match = re.match(r"loop\((\d+)\)\s*(.*)", text)
        if loop_match:
            loop_count = int(loop_match.group(1))  # Количество повторений
            text = loop_match.group(2)  # Текст после loop

        current_text = ""  # Начальный текст
        words = text.split(" ")  # Разделяем текст на слова
        
        for _ in range(loop_count):  # Выполняем цикл столько раз, сколько указано в loop
            for word in words:
                for i in range(1, len(word) + 1):
                    new_text = current_text + word[:i]
                    if new_text != message.text:
                        await message.edit(text=new_text)  # Редактируем сообщение
                    time.sleep(0.5)  # Задержка между буквами
                current_text += word + " "  # Добавляем слово с пробелом
                time.sleep(0.5)  # Задержка перед следующим словом
            current_text = ""  # Очищаем текст после одного цикла

    except IndexError:
        await message.reply("Пожалуйста, укажите текст, например: /pasta Hello")

# Список эмодзи Telegram
emojis_list = [
    "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😇", "😈", "😉", "😊", "😋", "😌", "😍", "😎", "😏", "😐", "😑", 
    "😒", "😓", "😔", "😕", "😖", "😗", "😘", "😙", "😚", "😛", "😜", "😝", "😞", "😟", "😠", "😡", "😢", "😭", "😤", 
    "😥", "😦", "😧", "😨", "😩", "😪", "😫", "😬", "😭", "😮", "😯", "😰", "😱", "😲", "😳", "😴", "😵", "😶", "😷", 
    "😸", "😹", "😺", "😻", "😼", "😽", "🙀", "🙁", "🙂", "🙃", "🤗", "🤔", "🤐", "🤨", "🤩", "🤪", "🤫", "🤬", "🤯"
]

@app.on_message(filters.command("emodzi"))
async def emodzi(client, message):
    if not is_authorized(message.from_user.id):
        return

    try:
        # Поочередное отображение всех эмодзи из списка
        for emoji in emojis_list:
            await message.edit(text=emoji)  # Редактируем сообщение, показывая эмодзи
            time.sleep(0.5)  # Задержка между эмодзи

    except Exception as e:
        await message.reply("Произошла ошибка при выполнении команды.")

# Запуск клиента
app.run()
