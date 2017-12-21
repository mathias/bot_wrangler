import zmq
import sys
import argparse


def _parse_args():
    parser = argparse.ArgumentParser(description="bot_wrangler client v0")
    parser.add_argument('-p', '--port', dest='port', help="Port to read/write from for this client", required=True)

    if len(sys.argv) < 2:
        parser.print_help()
    return parser.parse_args()

def main():
    "Run the input/output socket back to the bot_wrangler server"
    args = _parse_args()
    port = args.port
    context = zmq.Context()

    sock = context.socket(zmq.REQ)
    sock.connect("tcp://127.0.0.1:{}".format(port))

    while True:
        sock.send_string(f"hello from client")
        print(sock.recv())

main()
