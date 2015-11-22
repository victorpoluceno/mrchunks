import sys
sys.path.append('.')
import random
import time

from mrchunks.node import Node


def run_dispatcher(process, childs, nmessages):
    print('Dispatching...')
    start = time.time()
    for _ in range(nmessages):
        pid = random.choice(childs)
        process.send(('localhost', 9090, pid), '42')
        process.receive()

    end = time.time()
    print(nmessages / (end - start), 'message/sec')


if __name__ == '__main__':
    node = Node()
    node.initialize(address=('localhost', 9091), number_of_workers=2)
    node.arbiter.spawn(run_dispatcher, range(0, 20), 10)
    node.arbiter.run()
