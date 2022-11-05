
def play_number(text):
    # Manage Text Parameters
    if len(text) == 2:
        parameter = text[1]
        number = int(parameter) if parameter.isdigit() else None

        if number == None:
            return str(number)
        else:
            if parameter == 'start':
                return 'Setting random number between 1 and 100'
            elif parameter == 'restart':
                return 'Restarting game'