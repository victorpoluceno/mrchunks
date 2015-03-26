try:
    # Use builtin asyncio on Python 3.4+, or Tulip on Python 3.3
    import asyncio
except ImportError:
    # Use Trollius on Python <= 3.2
    import trollius as asyncio


def resolve(target):
    address = 'localhost'
    port = int('909%d' % target)
    return address, port


class Incoming(object):
    def __init__(self, queue):
        self._queue = queue

    @asyncio.coroutine
    def listen(self, loop, pid):
        print('Starting incoming...')
        address, port = resolve(pid)
        coro = loop.create_server(lambda: IncomingServer(self._queue),
                                  address, port)
        asyncio.async(coro)
        print ('Serving on: %s:%s' % (address, port))


class IncomingServer(asyncio.Protocol):
    def __init__(self, queue):
        self._queue = queue

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    @asyncio.coroutine
    def produce(self, data):
        yield asyncio.From(self._queue.put(data))

    def data_received(self, data):
        message = data
        asyncio.async(self.produce(data))
        print('Data received: {!r}'.format(message))
        # print('Close the client socket')
        # self.transport.close()


class Outgoing(object):
    def __init__(self, queue):
        self._queue = queue
        self._pool = {}

    @asyncio.coroutine
    def start(self, loop):
        print('Starting outgoing...')
        while True:
            pid, message = yield asyncio.From(self._queue.get())
            print 'Got message from %s' % pid
            if pid not in self._pool:
                address, port = resolve(pid)
                self._pool[pid] = queue = asyncio.Queue()

                print('Creating poll for %s:%s' % (address, port))
                coro = loop.create_connection(
                    lambda: OutgoingClient(queue, loop), address, port)
                asyncio.async(coro)
                print 'Pool for pid %r created!' % pid

            queue = self._pool.get(pid)
            yield asyncio.From(queue.put(message))
            yield asyncio.From(asyncio.sleep(0.1))
            print('Message queued!')


class OutgoingClient(asyncio.Protocol):
    def __init__(self, queue, loop):
        self._queue = queue
        self._loop = loop

    @asyncio.coroutine
    def consume(self):
        while True:
            yield asyncio.From(asyncio.sleep(0.1))
            message = yield asyncio.From(self._queue.get())
            self.transport.write(message)
            print('Data sent: {!r}'.format(message))

    def connection_made(self, transport):
        print('Connection made...')
        self.transport = transport
        asyncio.async(self.consume())

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event lop')
        self._loop.stop()
