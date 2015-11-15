from mrchunks.process import get_arbiter


class Node:
    arbiter = None

    def initialize(self, number_of_workers):
        assert not self.arbiter
        self.arbiter = get_arbiter(number_of_workers)
