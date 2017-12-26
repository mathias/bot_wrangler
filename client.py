import argparse
import signal
import sys
import zmq

class BotClient:
    def __init__(self):
        "Run the input/output socket back to the bot_wrangler server"
        args = self._parse_args()
        self._sub_port = args.sub
        self._pub_port = args.pub

        # Set up signal handling
        self.signals = (signal.SIGINT, signal.SIGTERM)
        self.original_handlers = {}
        for sig in self.signals:
            self.original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self._handler)

        self.context = zmq.Context()

        self.sub = self.context.socket(zmq.SUB)
        self.sub.setsockopt_string(zmq.SUBSCRIBE, '')
        self.sub.setsockopt(zmq.RCVBUF, 0)
        self.sub.setsockopt(zmq.LINGER, 0)
        self.sub.connect(f"tcp://127.0.0.1:{self._sub_port}")

        self.pub = self.context.socket(zmq.PUB)
        self.pub.setsockopt(zmq.LINGER, 0)
        self.pub.bind(f"tcp://127.0.0.1:{self._pub_port}")

        while True:
            # 1. Read string from halite exe
            request = sys.stdin.readline().rstrip('\n')
            # 2. Send string to bot wrangler server
            self.pub.send_string(request)
            # 3. Read response from bot wrangler server
            response = self.sub.recv().decode("utf-8")
            # 4. Detect if we're done or not
            if response == "DONE":
                self._disconnect()
            else:
                # Write response back to halite exe
                sys.stdout.write(response)
                sys.stdout.write('\n')
                sys.stdout.flush()

    def _handler(self, signum, frame):
        self._disconnect()

    def _disconnect(self):
        self.sub.disconnect(f"tcp://127.0.0.1:{self._sub_port}")
        self.pub.unbind(f"tcp://127.0.0.1:{self._pub_port}")
        # self.context.term()
        exit(0)

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="bot_wrangler client v0")
        parser.add_argument('-p', '--pub', dest='pub', help="Port to wite to for this client", required=True)
        parser.add_argument('-s', '--sub', dest='sub', help="Port to read from for this client", required=True)

        if len(sys.argv) < 2:
            parser.print_help()
        return parser.parse_args()

if __name__ == '__main__':
    BotClient()
