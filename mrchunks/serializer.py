import msgpack


def encode(payload):
    return msgpack.packb(payload)


def decode(payload):
    return msgpack.unpackb(payload)
