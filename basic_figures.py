
class Figure():
    def __init__(self, x, y, fig_type):
        self.x, self.y = x, y
        self.fig_type =  fig_type

    def valid_move(self) ->bool:
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def conflict()->bool:
        return True

    def move(self, x, y):
        if self.valid_move() and self.conflict():
            self.x, self.y = x, y

class Horse(Figure):
    def valid_move(self) -> bool:
        pass



class Bishop(Figure):
    pass

class Tower(Figure):
    pass

class Queen(Figure):
    pass

class King(Figure):
    pass

class Pawn(Figure):
    pass
