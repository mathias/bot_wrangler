import argparse
import json
import os
import shlex
import subprocess
import time
import zmq
import numpy as np

from bot.bot import Bot

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

    ep_history = []
    for r in range(iterations):
        round_start_time = time.time()

        running_reward = 0.0

        # Running a new halite executable is the equiv openai gym env.reset():

        # halite options:
        # -r don't generate replays; remove this if you want replays from all your training
        # -q output JSON -- json is easier to parse winner.
        #    Later, we could calculate a score rather than just winner status from JSON
        executable = os.path.abspath("./halite")
        command = executable + """ -r -q "python client.py --sub 5555 --pub 5556" "python client.py --sub 5557 --pub 5558" """

        proc = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        bot1 = Bot('SimpleBot1')
        bot2 = Bot('SimpleBot2')

        while proc.poll() is None:
            try:
                # Bot 1
                # Read string from halite over socket
                received = bot1sub.recv_string(zmq.NOBLOCK)

                if received:
                    # Get commands to run
                    bot1.update_map(received)
                    commands = bot1.step()

                    # Respond over socket:
                    bot1pub.send_string(commands)
            except zmq.ZMQError:
                continue

            try:
                # Bot 2
                # Read string from halite over socket
                received = bot2sub.recv_string(zmq.NOBLOCK)
                #print("Got socket2: {} chars".format(len(input)))

                if received:
                    bot2.update_map(received)
                    commands = bot2.step()

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
        # print(parsed_output)
        if parsed_output['stats']['0']['rank'] == 1:
            print("bot1: Winner!")
            running_reward += 1.0
        else:
            print("bot2: Winner!")


        ep_history.append(running_reward)

        print("Time for round: {} seconds".format(time.time() - round_start_time))
        print("halite process ended with code {}".format(proc.returncode))
        print("")
        # now backprop that reward!
    print("Reward overall was: {}".format(ep_history))

if __name__ == '__main__':
    main()
