import time

from mrchunks.group import shuffle


class Flow(object):
    def run(self):
        for source, destination in self.river:
            source(destination()).run()

    def subscribe(self, f):
        def decorate(klass, flowet, group=shuffle):
            self.river.append((klass, group(flowet)))


flow = Flow()


class Component:

    def __init__(self, destination):
        self.destination = destination

    def emit(self, pack):
        if self.destination:
            self.destination.incomming.append(pack)


class Source(Component):

    def run(self, sleep=0.2):
        while True:
            time.sleep(sleep)
            self.process()


class Processor(Component):

    def receive(self):
        return self.incomming.pop()

    def run(self, sleep=0.2):
        while True:
            time.sleep(sleep)
            self.process(self.receive())
