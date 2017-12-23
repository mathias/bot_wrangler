import argparse
import json
import os
import shlex
import subprocess
import time
import zmq
import numpy as np

class Bot():
    def __init__(self, name, subsock, pubsock):
        self.name = name
        # self.first_round = True
        self.subsock = subsock
        self.pubsock = pubsock
        self.player_id = self.subsock.recv_string()
        self.width, self.height = [int(x) for x in self.subsock.recv_string().strip().split()]

        self.send_name = False
        # Do map parsing here:
        self.initial_data = self._parse_line(self.subsock.recv_string())
        # TODO mathias: calculate voronai regions
        # TODO mathias: calculate delauney lines
        self.send_name = True
        self.pubsock.send_string(self.name)

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

def parse_game_json(game_output):
    parsed = json.loads(game_output)

    winner = None
    for bot_id in parsed['stats']:
        if parsed['stats'][bot_id]['rank'] == 1:
            winner = bot_id
    # TODO mathias: data for computing reward here
    #return { 'winner': winner }
    return parsed

def main():
    setup_start_time = time.time()
    # ZeroMQ context
    context = zmq.Context()

    bot1pub = context.socket(zmq.PUB)
    bot1pub.bind("tcp://127.0.0.1:5555")

    bot1sub = context.socket(zmq.SUB)
    bot1sub.connect("tcp://127.0.0.1:5556")

    bot2pub = context.socket(zmq.PUB)
    bot2pub.bind("tcp://127.0.0.1:5557")

    bot2sub = context.socket(zmq.SUB)
    bot2sub.connect("tcp://127.0.0.1:5558")

    parser = argparse.ArgumentParser(description="bot_wrangler server v0")
    parser.add_argument('-i', '--iter', dest='iterations', help="How many iterations to run", default=1)
    args = parser.parse_args()
    iterations = int(args.iterations)

    print("Setup took: {} seconds".format(time.time() - setup_start_time))

    for r in range(iterations):
        round_start_time = time.time()

        running_reward = 0
        ep_history = []

        # Running a new halite executable is the equiv openai gym env.reset():

        # halite options:
        # -r don't generate replays; remove this if you want replays from all your training
        # -q output JSON -- json is easier to parse winner.
        #    Later, we could calculate a score rather than just winner status from JSON
        executable = os.path.abspath("./halite")
        command = executable + """ -r -q "python client.py --sub 5555 --pub 5556" "python client.py --sub 5557 --pub 5558" """

        proc = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        bot1 = Bot('SimpleBot1', bot1sub, bot1pub)
        bot2 = Bot('SimpleBot2', bot2sub, bot1pub)

        while proc.poll() is None:
            try:
                # Bot 1
                # Read string from halite over socket
                received = bot1sub.recv_string(zmq.NOBLOCK)
                #print("Got socket1: {} chars".format(len(input)))

                # Get commands to run
                commands = bot1.step(received)

                # Respond over socket:
                bot1pub.send_string(commands)
            except zmq.ZMQError:
                continue

            try:
                # Bot 2
                # Read string from halite over socket
                received = bot2sub.recv_string(zmq.NOBLOCK)
                #print("Got socket2: {} chars".format(len(input)))

                commands = bot2.step(received)
                # Respond over socket:
                bot2pub.send_string(commands)

            except zmq.ZMQError:
                continue

        try:
            outs, errs = proc.communicate(input=None, timeout=10)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate(input=None, timeout=10)
        # TODO mathias: parse errors
        #if errs:
        #    print(f"Errors: {errs}")
        # else:

        bot1pub.send_string("DONE")
        bot2pub.send_string("DONE")

        parsed_output = parse_game_json(outs)
        if parsed_output['winner'][0]:
            print("Winner!")
            running_reward += 1.0

        print("Time to run one round: {} seconds".format(time.time() - round_start_time))
        print("Ended with {}".format(proc.returncode))

if __name__ == '__main__':
    main()
