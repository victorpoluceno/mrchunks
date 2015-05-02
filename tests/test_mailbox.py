from mrchunks.mailbox import Mailbox


class TestMailbox:

    def test_simple(self):
        ping = Mailbox()
        ping.run(0)
        ping.send(1, 'ping')
        pong = Mailbox()
        pong.run(1)
        envelop = pong.receive()
        print envelop
        pong.send(envelop.sender, 'pong')
        print ping.receive()


if __name__ == '__main__':
    t = TestMailbox()
    t.test_simple()
