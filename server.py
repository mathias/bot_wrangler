import zmq
import time
import subprocess

# ZeroMQ context
context = zmq.Context()

socket1 = context.socket(zmq.REP)
socket1.bind("tcp://127.0.0.1:5555")

# socket2 = context.socket(zmq.PUB)
# socket2.bind("tcp://127.0.0.1:5556")

id = 0

while True:
    # command_to_run = """./halite -d "240 160" "echo foo2" "echo foo1" -r -q"""
    # print(subprocess.check_output(command_to_run, shell=True).decode())
    print(socket1.recv())

    id += 1

    message = f"Hello #{id}"
    socket1.send_string(message)

# for iteration in range(2):
    # command_to_run = """./halite -d "240 160" "echo foo2" "echo foo1" -r -q"""
    # print(subprocess.check_output(command_to_run, shell=True).decode())

