from abc import ABC, abstractmethod


class iBackend(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def write_host(self):
        pass

    @abstractmethod
    def write_state(self):
        pass

    @abstractmethod
    def read_state(self):
        pass

    @abstractmethod
    def read_host(self):
        pass
