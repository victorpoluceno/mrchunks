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


if __name__ == '__main__':
    t = TestProcess()
    t.test_simple()
