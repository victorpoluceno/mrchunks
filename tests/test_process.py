import time

from mrchunks.process import get_arbiter


class TestProcess:

    def test_simple(self):
        def target(process):
            print 'RUNNING PROCESS: %r' % process

        arbiter = get_arbiter()
        arbiter.spawn(target)
        arbiter.run(forever=False)
        time.sleep(1)

    def test_mailbox(self):
        def ping(process, pong_pid):
            process.send(pong_pid, 'ping')
            print process.receive()

        def pong(process):
            envelop = process.receive()
            print envelop
            process.send(envelop.sender, 'pong')

        arbiter = get_arbiter(number_of_workers=1)
        pong_pid = arbiter.spawn(pong)
        arbiter.spawn(ping, pong_pid)
        arbiter.run(forever=False)
        time.sleep(10)


if __name__ == '__main__':
    t = TestProcess()
    #t.test_simple()
    t.test_mailbox()
