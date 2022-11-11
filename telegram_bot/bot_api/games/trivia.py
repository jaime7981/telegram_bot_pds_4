from bot_api.models import Chat, Stats, Question, Poll, TriviaGame, TriviaGameInstance

import requests

def play_trivia(text, chat, player):
    # Manage Text Parameters
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
        return 'Two parameters not implemented'
    elif len(text) == 3:
        return 'Three parameters not implemented'
    elif len(text) == 1:
        return 'TRIVIA GAME\n\
Objective: Respond the questions\n\
Commands:\n\
 -start or reset: restarts the game\n\
 -info: Returns the actual parameters of the game\n\
 -poll: Test poll\n\
 -closing poll: Test closing poll 60 secs\n\
 -end: Finishes the game'
    else:
        return 'Too many parameters'

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
            'open_period':time,
            'correct_option_id':correct_answer_id}
    request = requests.post(url, json=data)
    return request

def SavePoll(request, chat, question):
    request_json = request.json()
    result = request_json.get('result')

    if result != None:
        poll_id = result.get('poll').get('id')
        new_poll = Poll.objects.create(chat=chat,
                                    question=question,
                                    poll_id=poll_id)
        new_poll.save()
        return new_poll
    return None