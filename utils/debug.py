from . import addon

def msg(*messages, space=0):
    if addon.debug():
        message = [str(message).ljust(space, ' ') for message in messages]
        print(*message)
