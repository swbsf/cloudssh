class iBackend(object):
    def __init__(self):
        pass

    def write_host(self):
        raise(NotImplementedError)

    def write_state(self):
        raise(NotImplementedError)

    def read_state(self):
        raise(NotImplementedError)

    def read_host(self):
        raise(NotImplementedError)

    def path(self):
        raise(NotImplementedError)
