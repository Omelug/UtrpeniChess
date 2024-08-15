from figures import Figure, rel_delta

class Bishop(Figure):

    def move(self, to_x:int, to_y:int, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return  abs(delta_x) == abs(delta_y) and self.free_gcd_path(to_x, to_y)

    def after_move(self, **kwarg):
        return None