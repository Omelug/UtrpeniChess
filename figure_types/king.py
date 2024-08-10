from figures import Figure, rel_delta

class King(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) <= 1) and (abs(delta_y) <= 1)
    def after_move(self):
        return None