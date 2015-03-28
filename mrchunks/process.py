from mrchunks import asyncio
from mrchunks.mailbox import Mailbox

from collections import namedtuple
import multiprocessing

Envelop = namedtuple('envelop', 'recipient sender message')


class Spawn(object):

    def __init__(self):
        self._next_pid = 0

    def _get_next_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        return pid

    def __call__(self, start, *args, **kwargs):
        pid = self._get_next_pid()
        process = Process(pid, start)
        descriptor = multiprocessing.Process(
            target=process, args=args, kwargs=kwargs,
            name=pid)
        process.descriptor = descriptor
        descriptor.start()
        return process

spawn = Spawn()


class Process(object):

    def __init__(self, pid, start):
        self.pid = pid
        self.start = start
        self.descriptor = None

    def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        self.mailbox = Mailbox()
        self.mailbox.run(loop, self.pid)

        # TODO replace by call later
        asyncio.async(self.start(self, *args, **kwargs))
        run_forever(loop)

    def is_alive(self):
        return self.descriptor.is_alive()

    def send(self, target, message):
        print('Sending message: {} to: {}'.format(message, target))
        envelop = Envelop(target, self.pid, message)
        yield asyncio.From(self.mailbox.put(envelop))

    def receive(self):
        print('Receiving...')
        envelop = yield asyncio.From(self.mailbox.get())
        raise asyncio.Return(envelop)

    def stop(self):
        # TODO stop asyncio loop here
        self.descriptor.terminate()


def run_forever(loop):
    pending = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_forever()
