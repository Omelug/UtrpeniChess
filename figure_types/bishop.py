from figures import Figure, rel_delta

class Bishop(Figure):
    def move(self, to_x, to_y, target=None, realize=True):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        valid_by_type = abs(delta_x) == abs(delta_y)
        free_path = self.free_gcd_path(to_x, to_y)
        return valid_by_type and free_path
    def after_move(self, **kwarg):
        return None