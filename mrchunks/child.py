from supervisor import spawn
from mailbox import Mailbox

try:
    # Use builtin asyncio on Python 3.4+, or Tulip on Python 3.3
    import asyncio
except ImportError:
    # Use Trollius on Python <= 3.2
    import trollius as asyncio


class Child(object):

    def __call__(self, pid, *args):
        self.pid = pid
        loop = asyncio.get_event_loop()
        self.mailbox = Mailbox(self.pid)
        self.mailbox.run(loop)

        asyncio.async(self.initialize(*args))
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))
        loop.run_forever()

    @asyncio.coroutine
    def initialize(self, *args, **kwargs):
        pass

    def send(self, target, message):
        yield asyncio.From(self.mailbox.put(target, message))

    def receive(self):
        message = yield asyncio.From(self.mailbox.get())
        raise asyncio.Return(message)


if __name__ == '__main__':
    class Ping(Child):
        def initialize(self, pong):
            print 'initialize ping'
            yield asyncio.From(self.send(pong, 'ping'))
            pid, message = yield asyncio.From(self.receive())
            print 'Got: %s from: %s' % (message, pid)
            while True:
                yield asyncio.From(asyncio.sleep(0.1))
                yield asyncio.From(self.send(pong, 'ping'))
                pid, message = yield asyncio.From(self.receive())
                print pid, message

    class Pong(Child):
        def initialize(self):
            print 'initialize pong'
            pid, message = yield asyncio.From(self.receive())
            print 'Got: %s from: %s' % (message, pid)
            yield asyncio.From(self.send(pid, 'pong'))
            while True:
                yield asyncio.From(asyncio.sleep(0.1))
                pid, message = yield asyncio.From(self.receive())
                print pid, message
                yield asyncio.From(self.send(pid, 'pong'))

    pid, descriptor = spawn(Pong())
    print pid, descriptor
    pid, descriptor = spawn(Ping(), pid)
    print pid, descriptor
