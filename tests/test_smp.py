import time

from mrchunks.smp import Engine, switch


class TestSMP:
    def test_simple(self):
        def target(t):
            print 'RUNNING %r' % t

        engine = Engine(4)
        engine.apply(target, 0)
        engine.apply(target, 1)
        engine.apply(target, 2)
        engine.apply(target, 3)

        try:
            engine.run(forever=False)
            time.sleep(1)
        except KeyboardInterrupt:
            engine.stop()

    def test_loop(self):
        def target(t):
            print 'RUNNING LOOP %r' % t
            while True:
                time.sleep(1)
                switch()

        engine = Engine(4)
        engine.apply(target, 0)
        engine.apply(target, 1)
        engine.apply(target, 2)
        engine.apply(target, 3)

        try:
            engine.run(forever=False)
            time.sleep(10)
        except KeyboardInterrupt:
            engine.stop()


if __name__ == '__main__':
    t = TestSMP()
    t.test_simple()
    t.test_loop()
