from abc import ABC, abstractmethod

class SignalWriter(ABC):
    @abstractmethod
    def write(self, signals):
        pass
