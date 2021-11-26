from . import addon

def msg(*messages, space=0):
    if addon.debug():
        print(*[str(element).ljust(space, ' ') for element in messages])
