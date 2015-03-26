import logging
logging.basicConfig(level=logging.DEBUG)
import time
import multiprocessing
from collections import namedtuple


ONE_FOR_ONE = 'one_for_one'
RESTART_PERMANENT = 'permanent'
SHUTDOWN_BRUTAL = 'brutal'

child = namedtuple('child', 'id start_function restart shutdown')


class Supervisor(object):

    def __init__(self, restart=ONE_FOR_ONE, max_restart=1, max_timeout=60):
        self._childs_map, self._process_map = {}, {}
        self._restart = restart

    def run(self, childs):
        self._running = True
        for child in childs:
            self._childs_map[child.id] = child
            self._child_start(child.id)

        self._watch()

    def terminate(self):
        for _id, child in self._childs_map.items():
            self._child_stop(_id)

        self._running = False

    def _child_start(self, _id):
        child = self._childs_map[_id]
        pid, process = spawn(child.start_function)
        self._process_map[child.id] = process
        process.start()

    def _child_stop(self, _id):
        child = self._childs_map[_id]
        if child.shutdown == SHUTDOWN_BRUTAL:
            self._brutal_shutdown(_id)
        else:
            raise NotImplementedError

    def _child_restart(self, _id):
        child = self._childs_map[_id]
        if self._restart == ONE_FOR_ONE:
            self._one_for_one_restart(child)
        else:
            raise NotImplementedError

    def _watch(self, check_interval=0.6):
        while self._running:
            for pid, process in self._process_map.items():
                if process.is_alive():
                    continue

                self._restart(pid)

            time.sleep(check_interval)

    def _brutal_shutdown(self, _id):
        del self._childs_map[_id]
        process = self._process_map[_id]
        process.terminate()
        del self._process_map[_id]

    def _one_for_one_restart(self, child):
        process = self._processs_map[child.id]
        if child.restart == RESTART_PERMANENT:
            process.start()
        else:
            raise NotImplementedError


class Spawn(object):
    # TODO this need to be a singleton

    def __init__(self):
        self._next_pid = 0

    def _get_next_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        return pid

    def __call__(self, call, *args, **kwargs):
        # TODO pid + args sucks!
        pid = self._get_next_pid()
        args = [pid] + list(args)
        process = multiprocessing.Process(target=call, args=args,
                                          kwargs=kwargs,
                                          name=pid)
        process.start()
        return pid, process

spawn = Spawn()


if __name__ == '__main__':
    def loop():
        while True:
            pass

    childs = [child('loop', loop, RESTART_PERMANENT, SHUTDOWN_BRUTAL)]
    supervisor = Supervisor()
    try:
        supervisor.run(childs)
    except KeyboardInterrupt:
        supervisor.terminate()
