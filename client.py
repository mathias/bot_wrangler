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
        # 1. Read string from halite exe
        request = sys.stdin.readline().rstrip('\n')
        # 2. Send string to bot wrangler server
        sock.send_string(request)
        # 3. Read response from bot wrangler server
        response = sock.recv().decode("utf-8")
        # 4. Write response back to halite exe
        sys.stdout.write(response)
        sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == '__main__':
    main()
