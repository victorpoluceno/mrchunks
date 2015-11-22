import zmq

from mrchunks.concurrent import Engine, switch
from mrchunks.mailbox import Mailbox
from mrchunks.serializer import decode, encode


class Server:

    def __init__(self):
        self._context = zmq.Context()

    def __call__(self, *args, **kwargs):
        self.listen(kwargs['address'])
        while True:
            envelop = self.get()
            self.send(envelop)

    def get(self):
        while True:
            socks = dict(self._poller.poll(100))
            if socks:
                if socks.get(self._socket) != zmq.POLLIN:
                    switch()
                    continue

                data = self._socket.recv()
                # FIXME may be we need to ack after sendo ipc socket
                self._socket.send(b"OK+")
                break
            else:
                switch()

        return decode(data)

    def send(self, envelop):
        sender, recipient, message = envelop
        _, _, p = recipient
        socket = self._context.socket(zmq.REQ)
        socket.connect("ipc:///tmp/%d" % (p,))
        socket.send(encode(envelop), zmq.NOBLOCK)

    def listen(self, address):
        self._socket = self._context.socket(zmq.REP)
        address, port = address
        self._socket.bind("tcp://*:%s" % (port,))
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)


class Arbiter:

    def __init__(self, address, number_of_workers=1):
        self._next_pid = 0
        self._address = address
        self._engine = Engine(number_of_workers)
        self._listen()

    def _get_next_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        return self._address + (pid,)

    def _listen(self):
        server = Server()
        self._engine.apply(server, address=self._address)

    def spawn(self, start, *args, **kwargs):
        pid = self._get_next_pid()
        process = Process(pid, start)
        self._engine.apply(process, *args, **kwargs)
        return pid

    def run(self, forever=True):
        self._engine.run(forever)


def get_arbiter(*args, **kwargs):
    return Arbiter(*args, **kwargs)


class Process(object):

    def __init__(self, pid, start):
        self.pid = pid
        self._start = start

    def __call__(self, *args, **kwargs):
        self._mailbox = Mailbox()
        self._mailbox.run(self.pid)
        self._start(self, *args, **kwargs)

    def send(self, recipient, message):
        print('Sending message: {} from: {} to: {}'.format(message, self.pid,
                                                           recipient))
        self._mailbox.send(recipient, message)

    def receive(self):
        print('Receiving...')
        envelop = self._mailbox.receive()
        return envelop
