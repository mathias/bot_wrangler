class Bot():
    def __init__(self, name, subsock, pubsock):
        self.name = name
        # self.first_round = True
        self.subsock = subsock
        self.pubsock = pubsock
        # self.player_id = self.subsock.recv_string()
        # self.width, self.height = [int(x) for x in self.subsock.recv_string().strip().split()]

        self.send_name = False
        # Do map parsing here:
        # self.initial_data = self._parse_line(self.subsock.recv_string())
        # TODO mathias: calculate voronai regions
        # TODO mathias: calculate delauney lines
        self.send_name = True
        # self.pubsock.send_string(self.name)

    def step(self, received):
        """ Called every frame """
        if self.send_name:
            self.send_name = False
            return "SimpleBot"
        else:
            # For now, always move the first ship randomly
            return "t 0 1 {}".format(np.random.random_integers(0,359))

    def _parse_line(self, received):
        None
        # tokens = received.strip().split()
        # players_count, tokens = Player._parse(tokens)
