import copy
import glm

class Camera:
    def __init__(self, pos, dir=glm.vec3(0, 0, 1), viewplane_distance=1):
        self.pos = pos
        self.dir = glm.normalize(dir)
        self.original_pos = copy.copy(pos)
        self.original_dir = copy.copy(dir)
        self.viewplane_distance = viewplane_distance

    def reset(self):
        self.pos = copy.copy(self.original_pos)
        self.dir = copy.copy(self.original_dir)