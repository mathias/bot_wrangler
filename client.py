import zmq
import sys

context = zmq.Context()

sock = context.socket(zmq.REQ)
sock.connect("tcp://127.0.0.1:5555")

for request in range(10):
    sock.send_string(f"hello from client ##{request}")
    print(sock.recv())
