from figures import Figure, rel_delta

class Queen(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        print(f"{delta_x=} {delta_y=}")
        free_path = self.free_gcd_path(to_x, to_y)
        return (abs(delta_x) == abs(delta_y)) or (delta_x == 0) or (delta_y == 0) and free_path
    def after_move(self):
        return None