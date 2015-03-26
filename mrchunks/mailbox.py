import msgpack

from protocol import Incoming, Outgoing

try:
    # Use builtin asyncio on Python 3.4+, or Tulip on Python 3.3
    import asyncio
except ImportError:
    # Use Trollius on Python <= 3.2
    import trollius as asyncio


class Mailbox(object):

    def __init__(self, pid):
        self.pid = pid
        self._incoming_queue = asyncio.Queue()
        self._outgoing_queue = asyncio.Queue()

        self._outgoing = Outgoing(self._outgoing_queue)
        self._incoming = Incoming(self._incoming_queue)

    def run(self, loop):
        asyncio.async(self._incoming.listen(loop, self.pid))
        asyncio.async(self._outgoing.start(loop))

    def get(self):
        payload = yield asyncio.From(self._incoming_queue.get())
        raise asyncio.Return(msgpack.unpackb(payload))

    def put(self, target, message):
        print('Sending %r ' % message)
        payload = msgpack.packb((self.pid, message))
        yield asyncio.From(self._outgoing_queue.put((target, payload)))
