from figures import Figure, rel_delta

class Tower(Figure):

    def move(self, to_x:int, to_y:int, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return (delta_x == 0 or delta_y == 0) and self.free_gcd_path(to_x, to_y)

    def after_move(self, **kwarg):
        return None