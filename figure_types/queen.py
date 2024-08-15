from figures import Figure, rel_delta

class Queen(Figure):
    def move(self, to_x:int, to_y:int, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        print(to_x, to_y)
        free_path = self.free_gcd_path(to_x, to_y)
        print(free_path)
        return ((abs(delta_x) == abs(delta_y)) or (delta_x == 0) or (delta_y == 0)) and free_path

    def after_move(self, **kwarg):
        return None