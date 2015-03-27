from mrchunks import asyncio
from mrchunks.mailbox import Mailbox

from collections import namedtuple

Envelop = namedtuple('envelop', 'recipient sender message')


class Process(object):

    def __call__(self, pid, *args):
        self.pid = pid
        loop = asyncio.get_event_loop()
        self.mailbox = Mailbox()
        self.mailbox.run(loop, pid)

        asyncio.async(self.initialize(*args))
        run_forever(loop)

    @asyncio.coroutine
    def initialize(self, *args, **kwargs):
        pass

    def send(self, target, message):
        print('Sending message: {} to: {}'.format(message, target))
        envelop = Envelop(target, self.pid, message)
        yield asyncio.From(self.mailbox.put(envelop))

    def receive(self):
        print('Receiving...')
        envelop = yield asyncio.From(self.mailbox.get())
        raise asyncio.Return(envelop)


def run_forever(loop):
    pending = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_forever()
