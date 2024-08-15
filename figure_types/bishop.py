from figures import Figure, rel_delta

class Bishop(Figure):

    def move(self, to_x:int, to_y:int, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        valid_path = abs(delta_x) == abs(delta_y)
        free_path = self.free_gcd_path(to_x, to_y)
        return valid_path and free_path

    def after_move(self, **kwarg):
        return None