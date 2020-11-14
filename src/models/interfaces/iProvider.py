from abc import ABC, abstractmethod


class iInstancesFetch(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_list(self):
        raise(NotImplementedError)
