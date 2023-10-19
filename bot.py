import telebot

bot = telebot.TeleBot("6425741002:AAEDy6dg14uqGYYV30RxOpzjQ4JhAaApOSc")

users = {}
sessions = {}

def next_move(message, session):
    if sessions[session]["current_turn"] == "1":
        sessions[session]["current_turn"] = session
    else:
        current_turn_index = sessions[session]["user_list"].index(sessions[session]["current_turn"])
        user_list_length = len(sessions[session]["user_list"])
        if current_turn_index + 1 == user_list_length:
            sessions[session]["current_turn"] = sessions[session]["user_list"][0]
        else:
            sessions[session]["current_turn"] = sessions[session]["user_list"][current_turn_index + 1]

    send_all_users("Сейчас ходит " + sessions[session]["current_turn"], session)
    

def send_all_users(message, session_id):
    global users
    global sessions

    for user in sessions[session_id]["user_list"]:
        bot.send_message(user, message)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Напиши /create, чтобы начать новую партию, или /join [id создателя партии], чтобы подключиться к уже существующей")


@bot.message_handler(commands=['create'])
def create_session(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    sessions[chat_id] = {"user_list": [chat_id], "current_turn": "", "sentence": []}
    users[chat_id] = chat_id

    bot.send_message(message.chat.id, "Айди вашей партии: " + chat_id)


@bot.message_handler(commands=['join'])
def join_session(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    session_id = message.text.replace("/join", '').replace(' ', '')
    if session_id not in sessions:
        bot.send_message(chat_id, "Партия " + session_id + " не найдена")
    else:
        users[chat_id] = session_id
        sessions[session_id]["user_list"].append(chat_id)
        send_all_users(message.from_user.username + " подключился к партии", session_id)
        

@bot.message_handler(commands=['start_game'])
def start_session(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    current_session = users[chat_id]
    if chat_id != current_session:
        bot.send_message(chat_id, "Запустить игру может только организатор")
    else:
        sessions[current_session]["current_turn"] = "1"
        bot.send_message(chat_id, "Игра запущена!")
        next_move(message, current_session)


@bot.message_handler(commands=['stop_game'])
def stop_game(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    current_session = users[chat_id]
    send_all_users(str(sessions[current_session]["sentence"]), current_session)
    sessions[current_session]["sentence"] = []

    
@bot.message_handler(content_types=['text'])
def any_input(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    if chat_id not in users:
        send_welcome(message)
        return
    
    current_session = users[chat_id]
    if sessions[current_session]["current_turn"] == []:
        bot.send_message(chat_id, "Организатор еще не запустил игру")
        return
    
    if sessions[current_session]["current_turn"] != chat_id:
        bot.send_message(chat_id, "Сейчас не ваш ход")
        return

    sessions[current_session]["sentence"].append(message.text)
    
    next_move(message, current_session)

bot.polling(none_stop = True)
        
