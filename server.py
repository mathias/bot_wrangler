import argparse
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

    bot1pub = context.socket(zmq.PUB)
    bot1pub.bind("tcp://127.0.0.1:5555")

    bot1sub = context.socket(zmq.SUB)
    # bot1sub.setsockopt(zmq.SUBSCRIBE, '')
    # bot1sub.setsockopt(zmq.RCVBUF, 0)
    bot1sub.connect("tcp://127.0.0.1:5556")

    bot2pub = context.socket(zmq.PUB)
    bot2pub.bind("tcp://127.0.0.1:5557")

    bot2sub = context.socket(zmq.SUB)
    # bot2sub.setsockopt(zmq.SUBSCRIBE, '')
    # bot2sub.setsockopt(zmq.RCVBUF, 0)
    bot2sub.connect("tcp://127.0.0.1:5558")


    parser = argparse.ArgumentParser(description="bot_wrangler server v0")
    parser.add_argument('-i', '--iter', dest='iterations', help="How many iterations to run", default=1)
    args = parser.parse_args()
    iterations = int(args.iterations)

    for r in range(iterations):
        round_start_time = time.time()
        # halite options:
        # -r don't generate replays; remove this if you want replays from all your training
        # -q output JSON -- json is easier to parse winner.
        #    Later, we could calculate a score rather than just winner status from JSON
        executable = os.path.abspath("./halite")
        command = executable + """ -r -q -d "240 160" "python client.py --sub 5555 --pub 5556" "python client.py --sub 5557 --pub 5558" """

        proc = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        bot1 = Bot('SimpleBot1')
        bot2 = Bot('SimpleBot2')

        send_name = True
        while proc.poll() is None:
            try:
                # Bot 1
                # Read string from halite over socket
                input = bot1sub.recv_string(zmq.NOBLOCK)
                #print("Got socket1: {} chars".format(len(input)))

                # Get commands to run
                commands = bot1.get_commands(input)

                # Respond over socket:
                bot1pub.send_string(commands)
            except zmq.ZMQError:
                continue

            try:
                # Bot 2
                # Read string from halite over socket
                input = bot2sub.recv_string(zmq.NOBLOCK)
                #print("Got socket2: {} chars".format(len(input)))

                commands = bot2.get_commands(input)
                # Respond over socket:
                bot2pub.send_string(commands)
            except zmq.ZMQError:
                continue

            send_name = False
        try:
            outs, errs = proc.communicate(input=None, timeout=10)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate(input=None, timeout=10)

        bot1pub.send_string("DONE")
        bot2pub.send_string("DONE")

        print("Time to run one round: {} seconds".format(time.time() - round_start_time))
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
