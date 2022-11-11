from bot_api.models import Chat, Stats, Question, TriviaGame, TriviaGameInstance

import requests

def play_trivia(text, chat, player):
    # Manage Text Parameters
    if len(text) == 2:
        return 'Two parameters not implemented'
    elif len(text) == 3:
        return 'Three parameters not implemented'
    elif len(text) == 1:
        return 'TRIVIA GAME\n\
Objective: Respond the questions\n\
Commands:\n\
 -start or reset: restarts the game\n\
 -info: Returns the actual parameters of the game\n\
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
