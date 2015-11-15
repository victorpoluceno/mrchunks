import sys
sys.path.append('.')

from mrchunks.concurrent import switch
from mrchunks.node import Node


def run_dispatcher(process, childs):
    print('Dispatching...')
    for pid in childs:
        process.send(pid, 35)

    print('Waiting results...')
    while True:
        print 'Got result: ', process.receive()
        switch()


def run_child(process):
    def fib(n):
        if n == 1:
            return 1
        elif n == 0:
            return 0
        else:
            return fib(n - 1) + fib(n - 2)

    envelop = process.receive()
    result = fib(envelop.message)
    process.send(envelop.sender, result)


if __name__ == '__main__':
    node = Node()
    node.initialize(number_of_workers=2)

    print('Initializing childs...')

    childs = []
    for i in range(20):
        childs.append(node.arbiter.spawn(run_child))

    print('Initializing dispatcher...')
    node.arbiter.spawn(run_dispatcher, childs)
    node.arbiter.run()
