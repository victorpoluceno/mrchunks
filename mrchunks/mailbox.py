from collections import namedtuple

import zmq

from mrchunks.concurrent import switch
from mrchunks.serializer import encode, decode


Envelop = namedtuple('envelop', 'sender recipient message')


def resolve(target):
    address = 'localhost'
    port = int('909%d' % target)
    return address, port


class Mailbox(object):

    def __init__(self):
        self._outgoing = Outgoing()
        self._incoming = Incoming()

    def run(self, pid):
        self._pid = pid
        self._incoming.listen(pid)

    def receive(self):
        return Envelop(*self._incoming.get())

    def send(self, to, message):
        envelop = Envelop(self._pid, to, message)
        self._outgoing.put(envelop)


class Incoming(object):

    def __init__(self):
        self._context = zmq.Context()

    def get(self):
        while True:
            socks = dict(self._poller.poll(100))
            if socks:
                if socks.get(self._socket) != zmq.POLLIN:
                    switch()
                    continue

                data = self._socket.recv()
                self._socket.send(b"OK+")
                break
            else:
                switch()

        return decode(data)

    def listen(self, pid):
        self._socket = self._context.socket(zmq.REP)
        address, port = resolve(pid)
        self._socket.bind("tcp://*:%s" % (port,))
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)


class Outgoing(object):

    def __init__(self):
        self._context = zmq.Context()

    def put(self, evenlop):
        sender, recipient, message = evenlop
        address, port = resolve(recipient)
        socket = self._context.socket(zmq.REQ)
        socket.connect("tcp://%s:%s" % (address, port))
        socket.send(encode(evenlop), zmq.NOBLOCK)
