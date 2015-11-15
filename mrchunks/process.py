from mrchunks.concurrent import Engine
from mrchunks.mailbox import Mailbox


class Arbiter:

    def __init__(self, number_of_workers):
        self._engine = Engine(number_of_workers)
        self._next_pid = 0

    def _get_next_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        return pid

    def spawn(self, start, *args, **kwargs):
        pid = self._get_next_pid()
        process = Process(pid, start)
        self._engine.apply(process, *args, **kwargs)
        return pid

    def run(self, forever=True):
        self._engine.run(forever)


def get_arbiter(number_of_workers=1):
    return Arbiter(number_of_workers)


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
