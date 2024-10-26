from abc import ABC, abstractmethod


class Service(ABC):

    @abstractmethod
    def draw(self):
        """ Метод для отрисовки фигуры """