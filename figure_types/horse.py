from figures import Figure, rel_delta

class Horse(Figure):
    def move(self, to_x:int, to_y:int, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) == 1 and abs(delta_y) == 2) or (abs(delta_x) == 2 and abs(delta_y) == 1)
    def after_move(self, **kwargs):
        return None