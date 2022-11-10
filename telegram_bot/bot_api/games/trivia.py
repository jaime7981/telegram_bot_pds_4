
from bot_api.models import Chat, Stats, Question, TriviaGame, TriviaGameInstance

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
