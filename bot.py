import telebotfrom telebot.types import InlineKeyboardMarkup, InlineKeyboardButtonbot = telebot.TeleBot("6618058650:AAH0pUKlWVoPsfLkH5bAvVAexwhpYLfhOK8")users = {}rooms = {}questions = ["Кто?", "С кем?", "Когда?", "Где?", "Что делали?", "И что делали? (начните ответ с \"и\")", "\"Им мешал(о)...\"", "\"Их увидел(а)...\"", "\"Он спросил...\"", "\"Ему ответили: ...\"", "\"Дело закончилось...\""]bot.set_my_commands(    commands=[        telebot.types.BotCommand("/start", "Главное меню"),        telebot.types.BotCommand("/create", "Создать комнату"),        telebot.types.BotCommand("/join", "Подключиться к уже существующей комнате"),        telebot.types.BotCommand("/leave", "Покинуть комнату. Комната удаляется, если вы организатор"),        telebot.types.BotCommand("/stop_game", "Закончить предложение")    ],)def check_if_not_connected(chat_id):    global users    if chat_id not in users:        bot.send_message(chat_id, "Вы еще не подключились к комнате")        return True    else:        return Falsedef next_move(message, room):    if rooms[room]["user_index"] == -10:        rooms[room]["user_index"] = 0        rooms[room]["question_index"] = 0    else:        if rooms[room]["user_index"] + 1 == len(rooms[room]["user_list"]):            rooms[room]["user_index"] = 0        else:            rooms[room]["user_index"] += 1        question_list_length = len(rooms[room]["question_list"])         if rooms[room]["question_index"] + 1 == question_list_length:            stop_game(message)        else:            rooms[room]["question_index"] += 1    question = rooms[room]["question_list"][rooms[room]["question_index"]]    next_user_chat = bot.get_chat(rooms[room]["user_list"][rooms[room]["user_index"]])    next_user_name = next_user_chat.first_name    if next_user_chat.last_name != None:         next_user_name += " " + next_user_chat.last_name    markup = InlineKeyboardMarkup()    markup.add(InlineKeyboardButton("Пропустить ход", callback_data="skip"))    for user in rooms[room]["user_list"]:        if user != room and user != rooms[room]["user_list"][rooms[room]["user_index"]]:            markup = InlineKeyboardMarkup()                    text = question + "\nОтвечает " + next_user_name        if user == rooms[room]["user_list"][rooms[room]["user_index"]]:            text += " <b>(Вы)</b>"        bot.send_message(user, text, parse_mode='HTML', reply_markup=markup)        def send_all_users(message, room_id):    global users    global rooms    for user in rooms[room_id]["user_list"]:        bot.send_message(user, message)@bot.callback_query_handler(func=lambda call: True)def callback_query(call):    if call.data == "create":        users[str(call.message.chat.id)] = "from_main_menu"        create_room(call.message)        bot.answer_callback_query(call.id)    elif call.data == "join":        users[str(call.message.chat.id)] = "from_main_menu"        ask_number(call.message)        bot.answer_callback_query(call.id)    elif call.data == "start":        start_room(call)    elif call.data == "skip":        user = str(call.message.chat.id)        current_room = users[user]        if user != rooms[current_room]["user_list"][rooms[current_room]["user_index"]] and user != current_room:            bot.answer_callback_query(call.id, "Сейчас не ваш ход")            return        rooms[current_room]["question_index"] -= 1        next_move(call.message, current_room)        bot.answer_callback_query(call.id)    elif call.data == "set_questions":         user = str(call.message.chat.id)        print(users)        current_room = users[user]        question_list = ""        for question in rooms[current_room]["question_list"]:            question_list += '\n' + question        question_list = question_list[1:]        text = "Стандартный список:\n`" + question_list + "`\n\nОтправьте одним сообщением новый список вопросов, начиная каждый из них с новой строки\\."                rooms[current_room]["question_list"] = call.message.id                markup = InlineKeyboardMarkup()        markup.add(InlineKeyboardButton("<< Назад", callback_data="return_main_menu"))                bot.edit_message_text(chat_id=call.message.chat.id,                                message_id=call.message.id,                                text=text, reply_markup=markup, parse_mode='MarkdownV2')    elif call.data == "return_main_menu":        user = str(call.message.chat.id)        current_room = users[user]        create_room(call.message)        rooms[current_room]["question_list"] = questions        bot.answer_callback_query(call.id)@bot.message_handler(commands=['start'])def main_menu(message):    markup = InlineKeyboardMarkup()    markup.add(InlineKeyboardButton("Создать", callback_data="create"), InlineKeyboardButton("Подключиться", callback_data="join"))    bot.send_message(message.chat.id, "Добро пожаловать в бота Чепуха!\n"\        "Здесь можно поиграть во всем известную игру по сети вместе с друзьями.\n"\        "Ниже вы можете создать новую комнату или подключиться к уже существующей.", reply_markup=markup)@bot.message_handler(commands=['create'])def create_room(message):    global users    global rooms    global questions    print(users)    chat_id = str(message.chat.id)    from_main_menu = False    if users[chat_id] == "from_main_menu":        from_main_menu = True        users.pop(chat_id)    if rooms != {} and chat_id in users and not isinstance(rooms[users[chat_id]]["question_list"], int):        if users[chat_id] == chat_id:            markup = InlineKeyboardMarkup()            markup.add(InlineKeyboardButton("Начать игру", callback_data="start"), InlineKeyboardButton("Настроить вопросы", callback_data="set_questions"))            bot.send_message(message.chat.id, "Комната уже создана\\.\nНомер комнаты: `" + chat_id + "`\\.",        parse_mode='MarkdownV2', reply_markup=markup)        else:             bot.send_message(chat_id, "Вы уже подключены к комнате " + users[chat_id])        return            if chat_id not in users:        rooms[chat_id] = {"user_list": [chat_id], "user_index": None, "question_list": questions, "question_index": None,  "sentence": []}        users[chat_id] = chat_id        markup = InlineKeyboardMarkup()    markup.add(InlineKeyboardButton("Начать игру", callback_data="start"), InlineKeyboardButton("Настроить вопросы", callback_data="set_questions"))    text = "Комната создана\\.\nОтправьте номер комнаты друзьям: `" + chat_id + "` \\(нажмите, чтобы скопировать\\)\\."    if isinstance(rooms[users[chat_id]]["question_list"], int) or from_main_menu:        bot.edit_message_text(chat_id=message.chat.id,                                message_id=message.id, text=text,                                parse_mode='MarkdownV2', reply_markup=markup)    else:        bot.send_message(message.chat.id, text, parse_mode='MarkdownV2', reply_markup=markup)def join_room(message):    chat_id = str(message.chat.id)    room_id = message.text.replace("/join", '').replace(' ', '')        if room_id not in rooms:        bot.send_message(chat_id, "Комната " + room_id + " не найдена")        main_menu(message)    else:        users[chat_id] = room_id        rooms[room_id]["user_list"].append(chat_id)        send_all_users(message.from_user.full_name + " подключился к комнате", room_id)@bot.message_handler(commands=['join'])def ask_number(message):    global users    global rooms    chat_id = str(message.chat.id)    from_main_menu = False    if users[chat_id] == "from_main_menu":        from_main_menu = True        users.pop(chat_id)        if users != {} and chat_id in users:            bot.send_message(chat_id, "Вы уже подключены к комнате " + users[chat_id])            return        users[chat_id] = "joining"    if from_main_menu:        bot.edit_message_text(chat_id=chat_id,                                message_id=message.id, text="Введите номер комнаты:")    else:        bot.send_message(chat_id, "Введите номер комнаты:")@bot.message_handler(commands=['leave'])def leave(message):    global users    global rooms        chat_id = str(message.chat.id)    if check_if_not_connected(chat_id): return    current_room = users[chat_id]    if chat_id == current_room:        send_all_users("Организатор покинул комнату. Комната удалена.", current_room)        for x in rooms[current_room]["user_list"]:            users.pop(x)        rooms.pop(current_room)    else:        users.pop(chat_id)        rooms[current_room]["user_list"].remove(chat_id)            send_all_users(message.from_user.full_name + " покинул комнату", current_room)        bot.send_message(chat_id, "Вы покинули комнату")    main_menu(message)def start_room(call):    global users    global rooms        message = call.message    chat_id = str(message.chat.id)    if check_if_not_connected(chat_id): return    current_room = users[chat_id]    if rooms[current_room]["user_index"] == -10:        bot.answer_callback_query(call.id, "Игра уже запущена")    elif chat_id != current_room:        bot.answer_callback_query(call.id, "Запустить игру может только организатор")    else:        rooms[current_room]["user_index"] = -10        for user in rooms[current_room]["user_list"]:            bot.send_message(user, "Игра запущена\\.\n*Внимание\\! На вопросы в ковычках нужно отвечать полно, начиная ответ с того, что прописано в вопросе\\.*\nНапример\\:\n\\Вопрос\\: _\"Им мешал\\.\\.\"_\n\\Ответ\\: ~_Местные бомжи_~ _Им мешали местные бомжи_", parse_mode='MarkdownV2')        next_move(message, current_room)    bot.edit_message_reply_markup(call.from_user.id, message.message_id, reply_markup=InlineKeyboardMarkup())@bot.message_handler(commands=['stop_game'])def stop_game(message):    global users    global rooms    chat_id = str(message.chat.id)    if check_if_not_connected(chat_id): return    current_room = users[chat_id]    sentence = ""        for element in rooms[current_room]["sentence"]:        if sentence != "": sentence += ' '        sentence += element        users_string = ""    for element in rooms[current_room]["user_list"]:        if users_string != "":            users_string += ", "        next_user_chat = bot.get_chat(element)        next_user_name = next_user_chat.first_name        if next_user_chat.last_name != None:             next_user_name += " " + next_user_chat.last_name        users_string += next_user_name    for user in rooms[current_room]["user_list"]:        bot.send_message(user, "<b>Результат: " + sentence + "</b>\n\nВ партии участвовали: " + users_string + "\n#чепухаистория", parse_mode='HTML')    rooms[current_room]["sentence"] = []    rooms[current_room]["question_index"] = 0    if message.text == "/stop_game":        rooms[current_room]["question_index"] = -1        next_move(message, current_room)@bot.message_handler(content_types=['text'])def any_input(message):    global users    global rooms    chat_id = str(message.chat.id)    if chat_id not in users:        main_menu(message)        return    if users[chat_id] == "joining":        users.pop(chat_id)        join_room(message)        return        current_room = users[chat_id]    if isinstance(rooms[current_room]["question_list"], int):        rooms[current_room]["question_list"] = message.text.splitlines()        bot.send_message(chat_id, "Список вопросов обновлен")        create_room(message)        return        if rooms[current_room]["user_index"] == None:        bot.send_message(chat_id, "Организатор еще не запустил игру")        return    if rooms[current_room]["user_list"][rooms[current_room]["user_index"]] != chat_id:        bot.send_message(chat_id, "Сейчас не ваш ход")        return    rooms[current_room]["sentence"].append(message.text)        next_move(message, current_room)bot.polling(none_stop = True)        