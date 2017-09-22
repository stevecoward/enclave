# todo: dynamic module loading
from implant.interact import *


def load_module(action):
    if 'generic' in action:
        return GenericImplant()
