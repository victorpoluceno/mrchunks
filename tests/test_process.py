import tempfile
import cPickle
import time

from mrchunks import asyncio
from mrchunks.process import spawn


class TestSpawn(object):

    def test_spawn_params(self):
        @asyncio.coroutine
        def target(process, *args, **kwargs):
            filename = args[0]
            f = open(filename, 'w')
            f.write(cPickle.dumps((args, kwargs)))
            f.close()

        filename = tempfile.mkstemp()[1]
        p = spawn(target, filename, a=1)

        import time
        time.sleep(2)
        with open(filename) as f:
            result = cPickle.loads(f.read())
            assert result[0] == (filename,)
            assert result[1] == {'a': 1}

        p.stop()

    def test_pid_order(self):
        @asyncio.coroutine
        def target(process):
            pass

        from mrchunks.process import spawn
        p = spawn(target)
        pid = p.pid
        assert p.pid != 0
        p.stop()

        p = spawn(target)
        assert p.pid == pid + 1
        p.stop()

    def test_spawn_class(self):
        class Target:
            def __call__(self, actor):
                pass

        p = spawn(Target())
        assert p.is_alive()
        p.stop()


class TestProcess(object):

    def test_process(self):
        @asyncio.coroutine
        def target(process, *args, **kwargs):
            pass

        p = spawn(target)
        assert p
        assert p.pid is not None
        assert p.is_alive()
        assert p.descriptor
        p.stop()

    def test_stop(self):
        @asyncio.coroutine
        def target(process, *args, **kwargs):
            pass

        p = spawn(target)
        p.stop()
        time.sleep(2)
        assert not p.is_alive()

    def test_send_receive(self):
        @asyncio.coroutine
        def target(process, *args, **kwargs):
            yield asyncio.From(process.send(process.pid, 'ping'))
            response = yield asyncio.From(process.receive())
            filename = args[0]
            f = open(filename, 'w')
            f.write(cPickle.dumps(response[2]))
            f.close()

        filename = tempfile.mkstemp()[1]
        p = spawn(target, filename)
        time.sleep(5)

        with open(filename) as f:
            result = cPickle.loads(f.read())
            assert result == 'ping'

        p.stop()
