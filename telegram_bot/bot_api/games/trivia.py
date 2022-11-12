from bot_api.models import Chat, Stats, Question, Poll, TriviaGame, TriviaGameInstance

import requests, logging

logger = logging.getLogger('django')

def play_trivia(text, chat, player):
    # Manage Text Parameters
    trivia_intance = TriviaGameInstance.objects.filter(chat=chat)
    if len(trivia_intance) < 1:
        #Create new instance and trivia
        new_game = TriviaGame.objects.create(game_state="W",game_mode="F",question=None)
        new_game.save()
        new_instance = TriviaGameInstance.objects.create(player=player,chat=chat,trivia=new_game)
        new_instance.save()
        
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
            pass
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



def PollWinOrResponseLimit(request_json, poll: Poll):
    chat = poll.chat
    chat_id = chat.chat_id
    sendMessage(chat_id, text='Recieved response')

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
    instance = TriviaGameInstance.objects.filter(chat=chat)
    print(instance)
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
            if value == "First" or value == "F":
                game.game_mode = value
                game.save(update_fields=['game_mode'])
                return "Game mode was successfully updated to First"
            elif value == "Time" or value == "T":
                game.game_mode = value
                game.save(update_fields=['game_mode'])
                return "Game mode was successfully updated to Time"

def GameInfo(chat):
    instance = TriviaGameInstance.objects.filter(chat=chat)
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

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()