class iBackend(object):
    def __init__(self):
        pass

    def write(self):
        raise(NotImplementedError)

    def read(self):
        raise(NotImplementedError)

    def path(self):
        raise(NotImplementedError)
