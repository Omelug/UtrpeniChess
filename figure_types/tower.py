from figures import Figure, rel_delta

class Tower(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        free_path = self.free_gcd_path(to_x, to_y)
        return (delta_x == 0) or (delta_y == 0) and free_path
    def after_move(self):
        return None