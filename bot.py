import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("6457207433:AAH6-0_V-ZfGp_-0hRO7P9nvKxVY46xCez0")

users = {}
sessions = {}
questions = ["Кто?", "С кем?", "Когда?", "Где?", "Что делали?", "И что делали?", "Что им мешало?", "Кто их видел?", "Что спросил?", "Ему ответили: ...", "Дело закончилось..."]

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("/start", "Получить базовую информацию"),
        telebot.types.BotCommand("/create", "Создать комнату"),
        telebot.types.BotCommand("/join", "Подключиться к уже существующей комнате"),
        telebot.types.BotCommand("/leave", "Покинуть комнату. Комната удаляется, если вы организатор"),
        telebot.types.BotCommand("/stop_game", "Закончить предложение")
    ],
)


def check_if_not_connected(chat_id):
    global users

    if chat_id not in users:
        bot.send_message(chat_id, "Вы еще не подключились к комнате")
        return True
    else:
        return False


def next_move(message, session):
    if sessions[session]["current_turn"] == "1":
        sessions[session]["current_turn"] = session
        sessions[session]["current_question"] = 0;
        sessions[session]["question_list"] = questions
    else:
        current_turn_index = sessions[session]["user_list"].index(sessions[session]["current_turn"])
        user_list_length = len(sessions[session]["user_list"])
        if current_turn_index + 1 == user_list_length:
            sessions[session]["current_turn"] = sessions[session]["user_list"][0]
        else:
            sessions[session]["current_turn"] = sessions[session]["user_list"][current_turn_index + 1]
        
        question_list_length = len(sessions[session]["question_list"]) 
        if sessions[session]["current_question"] + 1 == question_list_length:
            stop_game(message)
        else:
            sessions[session]["current_question"] += 1

    current_question = sessions[session]["question_list"][sessions[session]["current_question"]]
    next_user_chat = bot.get_chat(sessions[session]["current_turn"])
    next_user_name = next_user_chat.first_name
    if next_user_chat.last_name != None: 
        next_user_name += " " + next_user_chat.last_name

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Пропустить ход", callback_data="skip"))
    for user in sessions[session]["user_list"]:
        if user != session and user != sessions[session]["current_turn"]:
            markup = InlineKeyboardMarkup()
            
        text = current_question + "\nОтвечает " + next_user_name
        if user == sessions[session]["current_turn"]:
            text += " *\\(Вы\\)*"
        bot.send_message(user, text, parse_mode='MarkdownV2', reply_markup=markup)
        

def send_all_users(message, session_id):
    global users
    global sessions

    for user in sessions[session_id]["user_list"]:
        bot.send_message(user, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "create":
        create_session(call.message)
        bot.answer_callback_query(call.id)
    elif call.data == "join":
    	ask_number(call.message)
    	bot.answer_callback_query(call.id)
    elif call.data == "start":
    	start_session(call)
    elif call.data == "skip":
        user = str(call.message.chat.id)
        current_session = users[user]
        if user != sessions[current_session]["current_turn"] and user != current_session:
            bot.answer_callback_query(call.id, "Сейчас не ваш ход")
            return
        sessions[current_session]["current_question"] -= 1
        next_move(call.message, current_session)
        bot.answer_callback_query(call.id)
    	


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Создать", callback_data="create"), InlineKeyboardButton("Подключиться", callback_data="join"))
    bot.send_message(message.chat.id, "Добро пожаловать в бота Чепуха!\n"\
        "Здесь можно поиграть во всем известную игру по сети вместе с друзьями.\n"\
        "Ниже вы можете создать новую комнату или подключиться к уже существующей.", reply_markup=markup)


@bot.message_handler(commands=['create'])
def create_session(message):
    global users
    global sessions
    global questions

    chat_id = str(message.chat.id)

    if sessions != {} and chat_id in users:
        if users[chat_id] == chat_id:
            bot.send_message(message.chat.id, "Комната уже создана\\.\nНомер комнаты: `" + chat_id + "`\\.",
        parse_mode='MarkdownV2')
        else: 
            bot.send_message(chat_id, "Вы уже подключены к комнате " + users[chat_id])
        return

    sessions[chat_id] = {"user_list": [chat_id], "current_turn": "", "question_list": [], "current_question": 0,  "sentence": []}
    users[chat_id] = chat_id
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать игру", callback_data="start"))
    bot.send_message(message.chat.id, "Комната создана\\.\nОтправьте номер комнаты друзьям: `" + chat_id + "`\\.",
        parse_mode='MarkdownV2', reply_markup=markup)

def join_session(message):
    chat_id = str(message.chat.id)
    session_id = message.text.replace("/join", '').replace(' ', '')
    
    if session_id not in sessions:
        bot.send_message(chat_id, "Комната " + session_id + " не найдена")
    else:
        users[chat_id] = session_id
        sessions[session_id]["user_list"].append(chat_id)
        send_all_users(message.from_user.full_name + " подключился к комнате", session_id)


@bot.message_handler(commands=['join'])
def ask_number(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    
    if users != {} and chat_id in users:
            bot.send_message(chat_id, "Вы уже подключены к комнате " + users[chat_id])
            return
    users[chat_id] = "joining"
    bot.send_message(chat_id, "Введите номер комнаты:")


@bot.message_handler(commands=['leave'])
def leave(message):
    global users
    global sessions
    
    chat_id = str(message.chat.id)

    if check_if_not_connected(chat_id): return

    current_session = users[chat_id]

    if chat_id == current_session:
        send_all_users("Организатор покинул комнату. Комната удалена.", current_session)
        for x in sessions[current_session]["user_list"]:
            users.pop(x)
        sessions.pop(current_session)
    else:
        users.pop(chat_id)
        sessions[current_session]["user_list"].remove(chat_id)
    
        send_all_users(message.from_user.full_name + " покинул комнату", current_session)
        bot.send_message(chat_id, "Вы покинули комнату")

    send_welcome(message)


def start_session(call):
    global users
    global sessions

    message = call.message
    chat_id = str(message.chat.id)

    if check_if_not_connected(chat_id): return

    current_session = users[chat_id]
    if sessions[current_session]["current_turn"] == "1":
        bot.answer_callback_query(call.id, "Игра уже запущена")
    elif chat_id != current_session:
        bot.answer_callback_query(call.id, "Запустить игру может только организатор")
    else:
        sessions[current_session]["current_turn"] = "1"
        bot.answer_callback_query(call.id, "Игра запущена")
        next_move(message, current_session)
    bot.edit_message_reply_markup(call.from_user.id, message.message_id, reply_markup=InlineKeyboardMarkup())


@bot.message_handler(commands=['stop_game'])
def stop_game(message):
    global users
    global sessions

    chat_id = str(message.chat.id)

    if check_if_not_connected(chat_id): return

    current_session = users[chat_id]
    sentence = ""
    
    for element in sessions[current_session]["sentence"]:
    	if sentence != "": sentence += ' '
    	sentence += element
    
    send_all_users("Результат: " + sentence, current_session)
    sessions[current_session]["sentence"] = []
    sessions[current_session]["current_question"] = 0
    

@bot.message_handler(content_types=['text'])
def any_input(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    if chat_id not in users:
        send_welcome(message)
        return
    if users[chat_id] == "joining":
        users.pop(chat_id)
        join_session(message)
        return
    
    current_session = users[chat_id]
    if sessions[current_session]["current_turn"] == "":
        bot.send_message(chat_id, "Организатор еще не запустил игру")
        return

    if sessions[current_session]["current_turn"] != chat_id:
        bot.send_message(chat_id, "Сейчас не ваш ход")
        return

    sessions[current_session]["sentence"].append(message.text)
    
    next_move(message, current_session)

bot.polling(none_stop = True)
        
