import glm

class World:
    def __init__(self, dim):
        self.dim = dim
        self.pos = glm.vec3(-dim / 2, -dim / 2, -dim / 2)
        self.voxels = self.gen_empty_voxel_array()

    def is_in_bounds(self, pos):
        return 0 <= pos.x < self.dim and 0 <= pos.y < self.dim and 0 <= pos.z < self.dim

    def reset(self):
        self.voxels = self.gen_empty_voxel_array()

    def gen_empty_voxel_array(self):
        voxels = []
        for x in range(self.dim):
            voxels.append([])
            for y in range(self.dim):
                voxels[x].append([])
                for z in range(self.dim):
                    voxels[x][y].append(None)
        return voxels

    def gen_cube(self, pos, size, block):
        for x in range(int(size.x)):
            for y in range(int(size.y)):
                for z in range(int(size.z)):
                    if self.is_in_bounds(pos + glm.vec3(x, y, z)):
                        self.voxels[int(pos.x) + x][int(pos.y) + y][int(pos.z) + z] = block

    def gen_sphere(self, pos, radius, block):
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                for z in range(-radius, radius + 1):
                    if glm.length(glm.vec3(x, y, z)) <= radius:
                        if self.is_in_bounds(pos + glm.vec3(x, y, z)):
                            self.voxels[int(pos.x) + x][int(pos.y) + y][int(pos.z) + z] = block
