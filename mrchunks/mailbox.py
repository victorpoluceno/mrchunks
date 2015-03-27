from mrchunks import asyncio
from mrchunks.serializer import encode, decode


class Mailbox(object):

    def __init__(self):
        self._outgoing = Outgoing()
        self._incoming = Incoming()

    def run(self, loop, pid):
        asyncio.async(self._incoming.listen(loop, pid))
        self._outgoing.start(loop)

    def get(self):
        envelop = yield asyncio.From(self._incoming.get())
        raise asyncio.Return(envelop)

    def put(self, envelop):
        yield asyncio.From(self._outgoing.put(envelop))


def resolve(target):
    address = 'localhost'
    port = int('909%d' % target)
    return address, port


class Incoming(object):
    def __init__(self):
        self._queue = asyncio.Queue()

    def get(self):
        payload = yield asyncio.From(self._queue.get())
        raise asyncio.Return(payload)

    @asyncio.coroutine
    def listen(self, loop, pid):
        print('Starting incoming...')
        address, port = resolve(pid)
        coro = loop.create_server(lambda: IncomingServer(self._queue),
                                  address, port)
        asyncio.async(coro)
        print('Serving on: {}:{}'.format(address, port))


class IncomingServer(asyncio.Protocol):
    def __init__(self, queue):
        self._queue = queue

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    @asyncio.coroutine
    def produce(self, data):
        yield asyncio.From(self._queue.put(decode(data)))

    def data_received(self, data):
        asyncio.async(self.produce(data))
        print('Data received: {!r}'.format(data))


class Outgoing(object):
    def __init__(self):
        self._pool = {}

    def put(self, evenlop):
        recipient, sender, message = evenlop
        print('Got message to: {!r}'.format(recipient))
        yield asyncio.From(self.map(evenlop))

    def add_peer(self, to):
        address, port = resolve(to)
        print('Creating poll for {!r}:{!r}'.format(address, port))
        self._pool[to] = queue = asyncio.Queue()
        coro = self.loop.create_connection(
            lambda: OutgoingClient(queue, self.loop), address, port)
        asyncio.async(coro)
        print('Pool for: {!r} created!'.format(to))

    def map(self, evenlop):
        if evenlop.recipient not in self._pool:
            yield asyncio.From(self.add_peer(evenlop.recipient))

        queue = self._pool.get(evenlop.recipient)
        yield asyncio.From(queue.put(encode(evenlop)))

    def start(self, loop):
        print('Starting outgoing...')
        self.loop = loop


class OutgoingClient(asyncio.Protocol):
    def __init__(self, queue, loop):
        self._queue = queue
        self._loop = loop

    @asyncio.coroutine
    def consume(self):
        while True:
            yield asyncio.From(asyncio.sleep(0.1))
            data = yield asyncio.From(self._queue.get())
            self.transport.write(data)
            print('Data sent: {!r}'.format(data))

    def connection_made(self, transport):
        print('Connection made...')
        self.transport = transport
        asyncio.async(self.consume())

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event lop')
        self._loop.stop()
