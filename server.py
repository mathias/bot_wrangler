import os
import shlex
import subprocess
import time
import zmq

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

        # print(subprocess.check_output(command_to_run, shell=True).decode())
        p = subprocess.Popen(shlex.split(command))

        send_name = True
        while p.poll() is None:
            # Bot 1
            # Read string from halite over socket
            input = socket1.recv().decode("utf-8") # Map

            # Form response to halite over socket
            if send_name:
                socket1.send_string("SimpleBot1")
            else:
                socket1.send_string("") # do nothing, to start

            # Bot 2
            # Read string from halite over socket
            input = socket2.recv().decode("utf-8") # Map

            # Form response to halite over socket
            if send_name:
                socket2.send_string("SimpleBot2")
            else:
                socket2.send_string("") # do nothing, to start

            send_name = False

        try:
            outs, errs = proc.communicate(timeout=20)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        print(outs)
        # note: the errs seem to be the same output if error encountered:
        #if errs:
        #    print(f"Errors: {errs}")
    exit(0)


if __name__ == '__main__':
    main()
