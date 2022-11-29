from bot_api.models import Chat, Stats, Question, Poll, TriviaGame, TriviaGameInstance, Player

import requests, logging

logger = logging.getLogger('django')

def play_trivia(text, chat, player):
    # Manage Text Parameters
    newGameIfNotExists(chat)
    newTriviaGameInstance(chat, player)
        
    if len(text) == 2:
        if text[1] == 'poll':
            question_from_api = getRandomQuestion()
            questions = parseAndSaveQuestions(question_from_api)
            if questions != None and len(questions) > 0:
                question = questions[0]
                request = sendPoll(chat.chat_id, question)
                SavePoll(request, chat, question)
                return 'Answer!'
        elif text[1] == 'closing_poll':
            question_from_api = getRandomQuestion()
            questions = parseAndSaveQuestions(question_from_api)
            if questions != None and len(questions) > 0:
                question = questions[0]
                request = sendClosingPoll(chat.chat_id, question)
                SavePoll(request, chat, question)
                return 'Answer!'
        elif text[1] == 'start':
            StartOrResetGame(chat)
            return "Answer!"
        elif text[1] == 'info':
            message = GameInfo(chat=chat)
            return message
        return 'Two parameters not implemented'
    elif len(text) == 3:
        if text[1] == 'set_question_nr':
            message = UpdateGameParams(chat, text[2], text[1])
            return message
        elif text[1] == 'set_game_mode':
            message = UpdateGameParams(chat, text[2], text[1])
            return message
        return 'Three parameters not implemented'
    elif len(text) == 1:
        return 'TRIVIA GAME\n\
Objective: Respond the questions\n\
Commands:\n\
 -start or reset: restarts the game\n\
 -info: Returns the actual parameters of the game\n\
 -poll: Test poll\n\
 -closing_poll: Test closing poll 60 secs\n\
 -set_question_nr: Sets number of questions to play\n\
 -set_game_mode: first or time\n\
 -end: Finishes the game'
    else:
        return 'Too many parameters'

def checkPlayerAnswer(poll, option_id, user_id):
    if option_id is not None and user_id is not None:
        player = Player.objects.filter(user_id=user_id)[0]
        newTriviaGameInstance(poll.chat, player)
        games = TriviaGame.objects.filter(chat=poll.chat.chat_id)[0]
        if CheckIfGameEndedOrClosed(poll):
            if poll.correct_option == option_id[0] and poll.closed == False: #Si le achunto
                #ASIGNAR PUNTOS AL GANADOR
                player = Player.objects.filter(user_id=user_id)[0]
                sendMessage(poll.chat.chat_id,f"The player {player.user_name} got the correct answer! and got +1 point")
                
                #ACTULIAZAR DATOS
                poll.closed = True
                poll.save(update_fields=['closed'])
                
                instance = TriviaGameInstance.objects.filter(chat=poll.chat.chat_id,player=player)[0]
                instance.points = str(int(instance.points) + 1)
                instance.save(update_fields=['points'])
                
                games = TriviaGame.objects.filter(id=instance.trivia.id)[0]
                games.answered_questions += 1
                games.save(update_fields=['answered_questions'])
                
                if CheckIfGameEndedOrClosed(poll):
                    NextTrivia(poll)
                else:
                    sendMessage(poll.chat.chat_id,f"There are no more Quizes")
                    endGame(poll.chat)
                
            else: #NO le achunto
                poll.vote_numbers = poll.vote_numbers + 1
                poll.save(update_fields=['vote_numbers'])
                intances = TriviaGameInstance.objects.filter(chat=poll.chat.chat_id)
                
                if int(poll.vote_numbers) == int(len(intances)):
                    sendMessage(poll.chat.chat_id,"No more available players to answer")
                    games = TriviaGame.objects.filter(chat=poll.chat.chat_id)[0]
                    games.answered_questions = str(int(games.answered_questions) + 1)
                    games.save(update_fields=['answered_questions'])
                    
                    poll.closed = True
                    poll.save(update_fields=['closed'])
                    
                    if CheckIfGameEndedOrClosed(poll) == False:
                        sendMessage(poll.chat.chat_id,f"There are no more Quizes")
                        endGame(poll.chat)
                    else:
                        NextTrivia(poll)
                    
                
        else:
            sendMessage(poll.chat.chat_id,f"This Game is already blocked, start a new game or reset")
    else:
        return None

def newGameIfNotExists(chat):
    new_triviaGame = TriviaGame.objects.filter(chat=chat.chat_id)
    text = f"cantidad {len(new_triviaGame)}"
    logger.info(text)
    if int(len(new_triviaGame)) < 1:
        new_game = TriviaGame.objects.create(game_state="W",game_mode="F",question=None,chat=chat.chat_id)
        new_game.save()

def newTriviaGameInstance(chat, player):
    
    text = f"id chat {chat.chat_id}"
    logger.info(text)
    
    trivia_intance = TriviaGameInstance.objects.filter(chat=chat.chat_id).filter(player=player)
    text = f"largo {len(trivia_intance)}"
    logger.info(text)
    prueba = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    text = f"largo t {len(prueba)}"
    logger.info(text)
    if int(len(trivia_intance)) < 1:
        new_triviaGame = TriviaGame.objects.filter(chat=chat.chat_id)[0]
        new_instance = TriviaGameInstance.objects.create(player=player,chat=chat.chat_id,trivia=new_triviaGame)
        new_instance.save()
    

def PollWinOrResponseLimit(request_json, poll: Poll):
    chat = poll.chat
    chat_id = chat.chat_id
    #sendMessage(chat_id, text='Recieved response')

def getRandomQuestion(limit=1):
    base_url = 'https://the-trivia-api.com/api/questions'
    url_dificulty = 'difficulty=medium'
    url = f'{base_url}?limit={limit}&region=CL'

    counter = 0
    while True:
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.json()
        elif counter >= 5:
            return None
        else:
            counter += 1

def CheckIfGameEndedOrClosed(poll):
    game = TriviaGame.objects.filter(chat=poll.chat.chat_id)[0]
    if game.game_state == "B" or int(game.num_of_questions) <= game.answered_questions:
        game.game_state = "B"
        game.save(update_fields=['game_state'])
        return False
    else:
        return True

def NextTrivia(poll):
    sendMessage(poll.chat.chat_id,f"Next trivia!!")
    triviaGame = TriviaGame.objects.filter(chat=poll.chat.chat_id)[0]
    question_from_api = getRandomQuestion()
    questions = parseAndSaveQuestions(question_from_api)
    if questions != None and len(questions) > 0:
        question = questions[0]
        texto = f"Game {int(triviaGame.answered_questions)+1} out of {triviaGame.num_of_questions}"
        sendMessage(poll.chat.chat_id,texto)
        if triviaGame.game_mode == "F":
            request = sendPoll(poll.chat.chat_id, question)
        else:
            request = sendClosingPoll(poll.chat.chat_id, question)
        poll = SavePoll(request, poll.chat, question)
        AssingPoll(poll.chat,poll)

def StartOrResetGame(chat):
    question_from_api = getRandomQuestion()
    questions = parseAndSaveQuestions(question_from_api)
    if questions != None and len(questions) > 0:
        question = questions[0]
        sendMessage(chat.chat_id,"The quiz has begun! Time to answer")
        triviaGame = TriviaGame.objects.filter(chat=chat.chat_id)[0]
        triviaGame.answered_questions = 0
        triviaGame.game_state = "W"
        triviaGame.save(update_fields=['answered_questions','game_state'])
        
        texto = f"Game {int(triviaGame.answered_questions)+1} out of {triviaGame.num_of_questions}"
        sendMessage(chat.chat_id,texto)
        if triviaGame.game_mode == "F":
            request = sendPoll(chat.chat_id, question)
        else:
            request = sendClosingPoll(chat.chat_id, question)
        poll = SavePoll(request, chat, question)
        AssingPoll(chat,poll)

def parseAndSaveQuestions(json_response):
    if json_response != None:
        questions = []
        for question in json_response:
            print(question.get('question'))
            print(question.get('correctAnswer'))
            print(type(question.get('incorrectAnswers')))
            for incorrect in question.get('incorrectAnswers'):
                print(incorrect)
            incorrect_answers = question.get('incorrectAnswers')
            if len(incorrect_answers) == 3:
                new_question = Question.objects.create(question=question.get('question'),
                                                   correct=question.get('correctAnswer'),
                                                   ans1=incorrect_answers[0],
                                                   ans2=incorrect_answers[1],
                                                   ans3=incorrect_answers[2])
                new_question.save()
                questions.append(new_question)
        return questions
    return None

def UpdateGameParams(chat, value, command):
    instance = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        games = TriviaGame.objects.filter(id=instance[0].trivia.id)
        game = games[0]
        if command == "set_question_nr":
            if is_integer(value) and int(value) >= 1:
                game.num_of_questions = value
                game.save(update_fields=['num_of_questions'])
                return f"Number of games successfully updated to {value}"
            else:
                return "Number of games could not be changed"
        elif command == "set_game_mode":
            if value.upper() == "FIRST" or value == "F":
                game.game_mode = "F"
                game.save(update_fields=['game_mode'])
                return "Game mode was successfully updated to First"
            elif value.upper() == "TIME" or value == "T":
                game.game_mode = "T"
                game.save(update_fields=['game_mode'])
                return "Game mode was successfully updated to Time"

def GameInfo(chat):
    instance = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        game = TriviaGame.objects.filter(id=instance[0].trivia.id)
        if game[0].game_mode == "F":
            gameMode = "First"
        else:
            gameMode = "Time" 
        texto = F"Game mode: {gameMode}\n\
Number of questions: {game[0].num_of_questions}"
        return texto
    else:
        return "No game was found"

def sendPoll(chat_id, question):
    url = f'https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/sendPoll'

    answer_list = [question.ans1, 
                   question.ans2,
                   question.ans3,
                   question.correct]
    answer_list.sort()

    correct_answer_id = 0
    for id, answer in enumerate(answer_list):
        if answer == question.correct:
            correct_answer_id = id
            break

    question_text = question.question

    data = {'chat_id':int(chat_id),
            'question':question_text,
            'options':answer_list,
            'type':'quiz',
            'is_anonymous':False,
            'correct_option_id':correct_answer_id}
    request = requests.post(url, json=data)
    return request

def sendClosingPoll(chat_id, question, time=60):
    url = f'https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/sendPoll'

    answer_list = [question.ans1, 
                   question.ans2,
                   question.ans3,
                   question.correct]
    answer_list.sort()

    correct_answer_id = 0
    for id, answer in enumerate(answer_list):
        if answer == question.correct:
            correct_answer_id = id
            break

    question_text = question.question

    data = {'chat_id':int(chat_id),
            'question':question_text,
            'options':answer_list,
            'type':'quiz',
            'is_anonymous':False,
            'open_period':time,
            'correct_option_id':correct_answer_id}
    request = requests.post(url, json=data)
    return request

def sendMessage(chat_id, text='bot response'):
    url = f'https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/sendMessage'
    data = {'chat_id':int(chat_id),
            'text':text}
    request = requests.post(url, json=data)
    return request   

def SavePoll(request, chat, question):
    request_json = request.json()
    result = request_json.get('result')

    if result != None:
        poll_id = result.get('poll').get('id')
        correct_option = result.get('poll').get('correct_option_id')
        new_poll = Poll.objects.create(chat=chat,
                                    question=question,
                                    poll_id=poll_id,
                                    correct_option=correct_option)
        new_poll.save()
        return new_poll
    return None

def AssingPoll(chat, poll):
    instance = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        games = TriviaGame.objects.filter(id=instance[0].trivia.id)[0]
        games.poll = poll
        games.save(update_fields=['poll'])
    pass

def endGame(chat):
    winner_id = ""
    biggest_points = 0
    instance = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    
    for player in instance:
        if player.points > biggest_points:
            biggest_points = player.points
            winner_id = player.player.user_id
    
    #Se agregan los puntos
    for addPoints in instance:
        player_stats = Stats.objects.filter(player=addPoints.player, chat_id=chat.chat_id)
        if int(len(player_stats)) >=1:
            player_stat = player_stats[0]
            if winner_id == player_stat.player.user_id:
                player_stat.won = player_stat.won + 1
                player_stat.save(update_fields=['won'])
                sendMessage(chat.chat_id,f"The player {player_stat.player.user_name} won the game!")
            elif biggest_points == 0:
                sendMessage(chat.chat_id,f"There were no winners")
            player_stat.played = player_stat.played + 1
            player_stat.lost = player_stat.played - player_stat.won
            player_stat.save(update_fields=['played', 'lost'])
    #Se reinicia los puntos de las instancias
    instance = TriviaGameInstance.objects.filter(chat=chat.chat_id)
    
    for player in instance:
        player.points = 0
        player.save(update_fields=['points'])
        
    
    
    
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()