import copy
import math
import glm

class Viewplane:
    def __init__(self, size, target_aspect_ratio):
        self.size = size
        self.validate_aspect_ratio(target_aspect_ratio)

    def top_left_corner_from_perspective_of(self, camera):
        half_size = self.size / 2
        center = camera.pos + camera.dir * camera.viewplane_distance
        right = glm.normalize(glm.cross(glm.vec3(0, 1, 0), camera.dir))
        up = glm.normalize(glm.cross(camera.dir, right))
        return center - right * half_size.x # + up * half_size.y / 2.0
    
    def get_right_from_perspective_of(self, camera):
        return glm.normalize(glm.cross(glm.vec3(0, 1, 0), camera.dir))

    def get_down_from_perspective_of(self, camera):
        right = self.get_right_from_perspective_of(camera)
        return -glm.normalize(glm.cross(right, camera.dir))


    def validate_aspect_ratio(self, ratio):
        aspect_ratio = self.size.x / self.size.y
        if not math.isclose(aspect_ratio, ratio, rel_tol=1e-2):
            raise ValueError(f"Aspect ratio {aspect_ratio} does not match {ratio}")

    def get_targets(self, camera, resolution):
        tl = self.top_left_corner_from_perspective_of(camera)
        right = self.get_right_from_perspective_of(camera)
        down = self.get_down_from_perspective_of(camera)
        pixel_size = self.size / resolution
        half_pixel = pixel_size / 2
        t = tl + right * half_pixel.x + down * half_pixel.y
        for y in range(int(resolution.y)):
            row_start = copy.copy(t)
            for x in range(int(resolution.x)):
                yield t
                t += right * pixel_size.x
            t = row_start + down * pixel_size.y
