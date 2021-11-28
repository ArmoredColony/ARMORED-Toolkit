from . import addon


def msg(*messages, spaces=0):
    if addon.debug():
        print(*[str(element).ljust(spaces, ' ') for element in messages])
