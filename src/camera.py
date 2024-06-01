import glm

class Camera:
    def __init__(self, pos, dir=glm.vec3(0, 0, 1), viewplane_distance=1):
        self.pos = pos
        self.dir = glm.normalize(dir)
        self.viewplane_distance = viewplane_distance