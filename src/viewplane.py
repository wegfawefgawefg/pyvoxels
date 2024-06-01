import glm

class Viewplane:
    def __init__(self, size, target_aspect_ratio):
        self.size = size
        self.validate_aspect_ratio(target_aspect_ratio)

    def top_left_corner_from_perspective_of(self, camera):
        half_size = self.size / 2
        center = camera.pos + camera.dir * camera.viewplane_distance
        left = glm.cross(camera.dir, glm.vec3(0, 1, 0))
        up = glm.cross(left, camera.dir)
        return center - left * half_size.x - up * half_size.y
    
    def get_right_from_perspective_of(self, camera):
        left = glm.cross(camera.dir, glm.vec3(0, 1, 0))
        right = -left
        return right

    def get_down_from_perspective_of(self, camera):
        up = glm.cross(glm.cross(camera.dir, glm.vec3(0, 1, 0)), camera.dir)
        down = -up
        return down

    def validate_aspect_ratio(self, ratio):
        aspect_ratio = self.size.x / self.size.y
        if aspect_ratio != ratio:
            raise ValueError(f"Aspect ratio {aspect_ratio} does not match {ratio}")

    def get_targets(self, camera, resolution):
        # get the top left corner
        # get the pixel dimensions
        # yield the targets

        tl = self.top_left_corner_from_perspective_of(camera)
        right = self.get_right_from_perspective_of(camera)
        down = self.get_down_from_perspective_of(camera)
        pixel_size = self.size / resolution
        half_pixel = pixel_size / 2
        t = tl + right * half_pixel.x + down * half_pixel.y
        for y in range(int(resolution.y)):
            for x in range(int(resolution.x)):
                yield t
                t += right * pixel_size.x
                t += down * pixel_size.y
