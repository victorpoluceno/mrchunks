from mrchunks.process import get_arbiter


# TODO make this a singleton

class Node:
    arbiter = None

    def initialize(self, address, number_of_workers):
        assert not self.arbiter
        self.arbiter = get_arbiter(address, number_of_workers)
