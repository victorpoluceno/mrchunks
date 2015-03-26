from collections import namedtuple, defaultdict

from mrchunks import Source, Processor, flow
from mrchunks.group import partition

Word = namedtuple('word count')


class Emitter(Source):
    def __init__(self):
        self.lines = self.text.splitlines()

    def process(self):
        if self.lines:
            self.emit(self.lines.pop())


@flow.subscribe(Source)
class Split(Processor):
    def process(self, pack):
        line, = pack.value
        words = line.split()
        for word in words:
            self.emit(Word(word, 1))


@flow.subscribe(Split, partition('word'))
class Count(Processor):
    def __init__(self):
        self.group = defaultdict(int)

    def process(self, pack):
        word, count = pack.value
        self.group[word] += count


if __name__ == '__main__':
    flow.run()
