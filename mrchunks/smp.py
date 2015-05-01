import random
import time
from collections import deque
from functools import partial
from multiprocessing import Process, Queue, cpu_count
from Queue import Empty

import dill
from greenlet import greenlet


class Engine:

    def __init__(self, number_of_workers=cpu_count()):
        self._workers = []
        self._prepare(number_of_workers)

    def _prepare(self, number_of_workers):
        for _ in range(number_of_workers):
            worker = Worker()
            self._workers.append(worker)

    def apply(self, target, *args, **kwargs):
        worker = random.choice(self._workers)
        worker.schedule(target, *args, **kwargs)

    def run(self, forever=True):
        for worker in self._workers:
            worker.start()

        if forever:
            while True:
                time.sleep(0.1)

    def stop(self):
        for worker in self._workers:
            worker.stop()


class Worker:

    def __init__(self):
        self._queue = Queue()

    def schedule(self, f, *args, **kwargs):
        pack = dill.dumps((f, args, kwargs))
        self._queue.put(pack)

    def start(self):
        self._process = Process(target=self)
        self._process.daemon = True
        self._process.start()

    def stop(self):
        self._process.terminate()

    def __call__(self):
        scheduler = Scheduler()
        while True:
            try:
                pack = self._queue.get(block=False)
            except Empty:
                break

            f, args, kwargs = dill.loads(pack)
            scheduler.add(f, args, kwargs)

        scheduler.loop()


class Scheduler:

    def __init__(self):
        self._stack = deque()

    def add(self, f, args, kwargs):
        g = greenlet(partial(f, *args, **kwargs))
        self._stack.append(g)

    def switch(self):
        if len(self._stack) == 0:
            return

        task = self._stack.popleft()
        task.switch()
        if not task.dead:
            self._stack.append(task)

    def loop(self):
        while True:
            self.switch()


def switch():
    greenlet.getcurrent().parent.switch()
