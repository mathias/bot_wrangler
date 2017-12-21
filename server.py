import json
import os
import shlex
import subprocess
import time
import zmq

def parse_game_json(game_output):
    parsed = json.loads(game_output)

    winner = None
    for bot_id in parsed['stats']:
        if parsed['stats'][bot_id]['rank'] == 1:
            winner = bot_id
    return { 'winner': winner }

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

        outs = ""
        send_name = True
        while proc.poll() is None:
            # Bot 1
            # Read string from halite over socket
            input = socket1.recv().decode("utf-8") # Map
            print("Got socket1: {} chars".format(len(input)))

            # Form response to halite over socket
            if send_name:
                socket1.send_string("SimpleBot1")
            else:
                socket1.send_string("") # do nothing, to start

            # Bot 2
            # Read string from halite over socket
            input = socket2.recv().decode("utf-8") # Map
            print("Got socket2: {} chars".format(len(input)))

            # Form response to halite over socket
            if send_name:
                socket2.send_string("SimpleBot2")
            else:
                socket2.send_string("") # do nothing, to start

            send_name = False

            outs += proc.stdout.read()
            # If we reach endgame, stop doing blocking communication over sockets
            if len(outs) > 1:
                break

        while proc.poll() is None:
            outs += proc.stdout.read()

        # TODO mathias: parse errors
        #if errs:
        #    print(f"Errors: {errs}")
        # else:
        parsed_output = parse_game_json(outs)
        print("Winner: {}".format(parsed_output['winner']))
    exit(0)


if __name__ == '__main__':
    main()
