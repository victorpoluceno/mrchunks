from mrchunks import asyncio
from mrchunks.supervisor import spawn
from mrchunks.process import Process


class Ping(Process):
    @asyncio.coroutine
    def initialize(self, pong):
        print('Initializing ping')
        yield asyncio.From(self.send(pong, 'ping'))
        _, sender, message = yield asyncio.From(self.receive())
        print('Got: {} from: {}'.format(message, sender))


class Pong(Process):
    @asyncio.coroutine
    def initialize(self):
        print('Initializing pong')
        _, sender, message = yield asyncio.From(self.receive())
        print('Got: {} from: {}'.format(message, sender))
        yield asyncio.From(self.send(sender, 'pong'))


if __name__ == '__main__':
    pong_pid, _ = spawn(Pong())
    spawn(Ping(), pong_pid)
