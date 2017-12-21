import random

class Bot:
    def __init__(self, name):
        self.name = name
        self.first_round = True

    def get_commands(self, input):
        # If this is the first round, send back name
        if self.first_round:
            self.first_round = False
            return "SimpleBot"
        else:
            # For now, always move the first ship randomly
            return "t 0 1 {}".format(random.randrange(0,359,1))
