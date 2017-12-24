import random

class Bot():
    def __init__(self, name, subsock, pubsock):
        self.name = name
        self.send_name = True

    def step(self, received):
        """ Called every frame to get commands """
        if self.send_name:
            self.send_name = False
            return "SimpleBot"
        else:
            # For now, always move the first ship randomly
            return "t 0 1 {}".format(random.random_integers(0,359))

    def update_map(self, received):
        """ Called every frame to update internal game state """
        players_count, tokens = self._parse_line(received)
        print("tokens")

    def _parse_line(self, received):
        return received.strip().split()
