import argparse
import signal
import sys
import zmq

class BotClient():
    def __init__(self):
        "Run the input/output socket back to the bot_wrangler server"
        args = self._parse_args()
        sub_port = args.sub
        pub_port = args.pub
        self.context = zmq.Context()

        self.sub = self.context.socket(zmq.SUB)
        # self.sub.setsockopt(zmq.SUBSCRIBE, '')
        # self.sub.setsockopt(zmq.RCVBUF, 0)
        self.sub.connect(f"tcp://127.0.0.1:{sub_port}")

        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(f"tcp://127.0.0.1:{pub_port}")

        # Set up signal handling
        self.interrupted = False
        # self.released = False
        # self.sig = signal.SIGINT
        # self.signals = (signal.SIGINT, signal.SIGTERM)
        # self.original_handlers = {}
        # for sig in self.signals:
            # self.original_handlers[sig] = signal.getsignal(sig)
            # signal.signal(sig, self._handler)
        # self.original_handler = signal.getsignal(self.sig)
        # signal.signal(self.sig, self._handler)

        while True:
            # if self.interrupted:
                # self.sock.disconnect("tcp://127.0.0.1:{}".format(port))
                # self.context.term()
                # exit(0)


            # 1. Read string from halite exe
            request = sys.stdin.readline().rstrip('\n')
            # 2. Send string to bot wrangler server
            self.pub.send_string(request)
            # 3. Read response from bot wrangler server
            response = self.sub.recv().decode("utf-8")
            # 4. Detect if we're done or not
            if response == "DONE":
                exit(0)
            else:
                # Write response back to halite exe
                sys.stdout.write(response)
                sys.stdout.write('\n')
                sys.stdout.flush()

    def _handler(self, signum, frame):
        # self._release()
        self.interrupted = True

    # def _release(self):
        # if self.released:
            # return False
        # signal.signal(self.sig, self.original_handler)
        # self.released = True
        # return True

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="bot_wrangler client v0")
        parser.add_argument('-p', '--pub', dest='pub', help="Port to wite to for this client", required=True)
        parser.add_argument('-s', '--sub', dest='sub', help="Port to read from for this client", required=True)

        if len(sys.argv) < 2:
            parser.print_help()
        return parser.parse_args()

if __name__ == '__main__':
    BotClient()
