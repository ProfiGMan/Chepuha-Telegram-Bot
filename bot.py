import telebot

bot = telebot.TeleBot("6457207433:AAH6-0_V-ZfGp_-0hRO7P9nvKxVY46xCez0")

users = {}
sessions = {}
questions = ["Кто?", "С кем?", "Когда?", "Где?", "Что делали?", "И что делали?", "Что им мешало?", "Кто их видел?", "Что спросил?", "Ему ответили: ...", "Дело закончилось..."]

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
        
        question_list_length = len(questions)
        #len(session[session]["question_list"])
        if sessions[session]["current_question"] + 1 == question_list_length:
            stop_game(message)
        else:
            sessions[session]["current_question"] += 1

    current_question = sessions[session]["question_list"][sessions[session]["current_question"]]
    send_all_users(current_question + "\nОтвечает " + sessions[session]["current_turn"], session)
    

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
    global questions

    chat_id = str(message.chat.id)
    sessions[chat_id] = {"user_list": [chat_id], "current_turn": "", "question_list": [], "current_question": 0,  "sentence": []}
    users[chat_id] = chat_id

    bot.send_message(message.chat.id, "Айди вашей партии: " + chat_id)


@bot.message_handler(commands=['join'])
def join_session(message):
    global users
    global sessions

    chat_id = str(message.chat.id)
    session_id = message.text.replace("/join", '').replace(' ', '')
    session_id = "923476979"
    if session_id not in sessions:
        bot.send_message(chat_id, "Партия " + session_id + " не найдена")
    else:
        users[chat_id] = session_id
        sessions[session_id]["user_list"].append(chat_id)
        send_all_users("Кто-то подключился к партии", session_id)
        

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
    sentence = ""
    
    for element in sessions[current_session]["sentence"]:
    	if sentence != "": sentence += ' '
    	sentence += element
    
    send_all_users("Результат: " + sentence, current_session)
    sessions[current_session]["sentence"] = []
    sessions[current_session]["current_question"] = 0
    

@bot.message_handler(commands=['leave'])
def leave(message):
    global users
    global sessions
    
    chat_id = str(message.chat.id)
    current_session = users[chat_id]
    if chat_id == current_session:
        send_all_users("Организатор покинул партию. Партия удалена.", current_session)
        for x in sessions[current_session]["user_list"]:
            users.pop(x)
        sessions.pop(current_session)
    else:
        users.pop(chat_id)
        print(sessions[current_session]["user_list"])
        print(message.chat.id)
        sessions[current_session]["user_list"].remove(chat_id)
    
        send_all_users(message.from_user.first_name + " покинул партию", current_session)
        bot.send_message(chat_id, "Вы покинули партию")
    


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
        
