import json
import os
import shlex
import subprocess
import time
import zmq

# relative imports
from bot.main import Bot

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
    # ZeroMQ context
    context = zmq.Context()

    socket1 = context.socket(zmq.REP)
    socket1.bind("tcp://127.0.0.1:5555")

    socket2 = context.socket(zmq.REP)
    socket2.bind("tcp://127.0.0.1:5556")

    for r in range(1): # todo mathias: argparse a number of iterations here
        # halite options:
        # -r don't generate replays; remove this if you want replays from all your training
        # -q output JSON -- json is easier to parse winner.
        #    Later, we could calculate a score rather than just winner status from JSON
        executable = os.path.abspath("./halite")
        command = executable + """ -r -q -d "240 160" "python client.py -p 5555" "python client.py -p 5556" """

        proc = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        bot1 = Bot('SimpleBot1')
        bot2 = Bot('SimpleBot2')

        send_name = True
        while proc.poll() is None:
            try:
                # Bot 1
                # Read string from halite over socket
                input = socket1.recv_string(zmq.NOBLOCK)
                #print("Got socket1: {} chars".format(len(input)))

                # Get commands to run
                commands = bot1.get_commands(input)

                # Respond over socket:
                socket1.send_string(commands)
            except zmq.ZMQError:
                continue

            try:
                # Bot 2
                # Read string from halite over socket
                input = socket2.recv_string(zmq.NOBLOCK)
                #print("Got socket2: {} chars".format(len(input)))

                commands = bot2.get_commands(input)
                # Respond over socket:
                socket2.send_string(commands)
            except zmq.ZMQError:
                continue

            send_name = False
        try:
            outs, errs = proc.communicate(input=None, timeout=10)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate(input=None, timeout=10)
        print("Ended with {}".format(proc.returncode))

        # TODO mathias: parse errors
        #if errs:
        #    print(f"Errors: {errs}")
        # else:
        parsed_output = parse_game_json(outs)
        #print("Winner: {}".format(parsed_output['winner']))
        print(parsed_output)

if __name__ == '__main__':
    main()
