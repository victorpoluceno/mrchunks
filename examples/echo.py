import sys
sys.path.append('.')

from mrchunks.node import Node


def run_child(process):
    while True:
        envelop = process.receive()
        process.send(envelop.sender, envelop.message)


if __name__ == '__main__':
    node = Node()
    node.initialize(address=('localhost', 9090), number_of_workers=2)
    childs = [node.arbiter.spawn(run_child) for _ in range(20)]
    node.arbiter.run()
