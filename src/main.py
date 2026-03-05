import enum
import math

import pygame
import glm

from world import World
from camera import Camera
from viewplane import Viewplane
from utils import v2totuple


pygame.init()


class Mode(enum.Enum):
    FLIGHT = enum.auto()
    ORBIT = enum.auto()


mode = Mode.ORBIT

render_resolution = glm.vec2(64, 48)
window_size = glm.vec2(800, 600)

world = World(8)
world.gen_floor(True)
world.gen_cube(
    glm.vec3(1, world.get_above_floor_level() - 1, 1), glm.vec3(1, 2, 1), (255, 0, 0)
)

# put a cube in the 4 corners
# white
cube_color = (255, 255, 255)
world.gen_cube(
    glm.vec3(0, world.get_above_floor_level(), 0), glm.vec3(1, 1, 1), cube_color
)
world.gen_cube(
    glm.vec3(0, world.get_above_floor_level(), world.dim - 1),
    glm.vec3(1, 1, 1),
    cube_color,
)
world.gen_cube(
    glm.vec3(world.dim - 1, world.get_above_floor_level(), 0),
    glm.vec3(1, 1, 1),
    cube_color,
)
world.gen_cube(
    glm.vec3(world.dim - 1, world.get_above_floor_level(), world.dim - 1),
    glm.vec3(1, 1, 1),
    cube_color,
)

camera = Camera(glm.vec3(0, 2.4, 0), glm.vec3(0, 0, -1), 3.0)
viewplane = Viewplane(glm.vec2(4, 3), render_resolution.x / render_resolution.y)

NUM_RAY_STEPS = 48
MARCH_STEP_SIZE = 0.25


def step():
    if mode == Mode.ORBIT:
        tm = 1.0
        t = pygame.time.get_ticks() / 1000 * tm
        orbit_radius = 10
        orbit_center = world.get_center()
        cam_height = camera.pos.y
        camera.pos = (
            glm.vec3(math.sin(t) * orbit_radius, 0, math.cos(t) * orbit_radius)
            + orbit_center
        )
        camera.dir = glm.normalize(world.get_center() - camera.pos)
        camera.pos.y = cam_height

    # move the camera
    # forward with w, back with s, rotate with a and d
    keys = pygame.key.get_pressed()
    cam_speed = 0.1
    rotation_speed = 0.1

    # if caps lock is pressed move at 4x speed
    if keys[pygame.K_CAPSLOCK]:
        cam_speed *= 4

    if keys[pygame.K_w]:
        camera.pos += camera.dir * cam_speed
    if keys[pygame.K_s]:
        camera.pos -= camera.dir * cam_speed
    if keys[pygame.K_a]:
        camera.dir = glm.rotate(camera.dir, -rotation_speed, glm.vec3(0, 1, 0))
    if keys[pygame.K_d]:
        camera.dir = glm.rotate(camera.dir, rotation_speed, glm.vec3(0, 1, 0))
    # space for up, and shift for down
    if keys[pygame.K_SPACE]:
        camera.pos -= glm.vec3(0, cam_speed, 0)
    if keys[pygame.K_LSHIFT]:
        camera.pos += glm.vec3(0, cam_speed, 0)

    # reset pos on r press
    if keys[pygame.K_r]:
        camera.reset()

    # t and g to move the viewplane closer and further
    if keys[pygame.K_t]:
        camera.viewplane_distance -= 0.1
    if keys[pygame.K_g]:
        camera.viewplane_distance += 0.1

    # look via the mouse
    mouse_delta = glm.vec2(pygame.mouse.get_rel())
    mouse_speed = 0.001
    if mode == Mode.FLIGHT and pygame.mouse.get_pressed()[0]:
        camera.dir = glm.rotate(
            camera.dir, -mouse_delta.x * mouse_speed, glm.vec3(0, 1, 0)
        )
        camera.dir = glm.rotate(
            camera.dir,
            -mouse_delta.y * mouse_speed,
            glm.cross(camera.dir, glm.vec3(0, 1, 0)),
        )


def draw_world(surface):
    width = int(render_resolution.x)
    height = int(render_resolution.y)
    dim = world.dim
    voxels = world.voxels
    world_pos = world.pos
    step_size = MARCH_STEP_SIZE
    num_steps = NUM_RAY_STEPS
    max_march_distance = num_steps * step_size
    inv_max_march_distance = 1.0 / max_march_distance if max_march_distance > 0 else 0.0

    cam = camera.pos
    cam_x = cam.x
    cam_y = cam.y
    cam_z = cam.z
    world_x = world_pos.x
    world_y = world_pos.y
    world_z = world_pos.z

    targets = viewplane.get_targets(camera, render_resolution)
    pixels = pygame.PixelArray(surface)
    black = surface.map_rgb((0, 0, 0))

    try:
        for y in range(height):
            for x in range(width):
                target = next(targets)
                ray = glm.normalize(target - cam)
                ray_x = ray.x
                ray_y = ray.y
                ray_z = ray.z

                pos_x = cam_x
                pos_y = cam_y
                pos_z = cam_z
                hit_voxel = None
                dist_to_hit = max_march_distance

                for _ in range(num_steps):
                    pos_x += ray_x * step_size
                    pos_y += ray_y * step_size
                    pos_z += ray_z * step_size

                    local_x = pos_x - world_x
                    local_y = pos_y - world_y
                    local_z = pos_z - world_z
                    if 0 <= local_x < dim and 0 <= local_y < dim and 0 <= local_z < dim:
                        voxel = voxels[int(local_x)][int(local_y)][int(local_z)]
                        if voxel is not None:
                            hit_voxel = voxel
                            dx = pos_x - cam_x
                            dy = pos_y - cam_y
                            dz = pos_z - cam_z
                            dist_to_hit = math.sqrt(dx * dx + dy * dy + dz * dz)
                            break

                if hit_voxel is None:
                    pixels[x, y] = black
                    continue

                if hit_voxel is True:
                    r, g, b = 255, 255, 255
                else:
                    r, g, b = hit_voxel

                brightness = 1.0 - (dist_to_hit * inv_max_march_distance)
                if brightness <= 0:
                    pixels[x, y] = black
                else:
                    pixels[x, y] = surface.map_rgb(
                        (int(r * brightness), int(g * brightness), int(b * brightness))
                    )
    finally:
        del pixels


def draw_map(surface):
    # Minimap parameters
    map_offset = glm.vec2(world.get_center().x, world.get_center().z)
    map_offset += glm.vec2(5, 5)
    map_scale = 4

    # Draw the camera
    cam_pos = glm.vec2(camera.pos.x, camera.pos.z) * map_scale + map_offset * map_scale
    pygame.draw.circle(surface, (0, 255, 0), (int(cam_pos.x), int(cam_pos.y)), 2)

    # Draw the camera direction
    cam_dir = glm.normalize(camera.dir)
    cam_dir = glm.vec2(cam_dir.x, cam_dir.z)
    end = cam_pos + cam_dir * 10
    pygame.draw.line(surface, (0, 255, 0), cam_pos, end)

    # Draw the viewplane
    top_left = viewplane.top_left_corner_from_perspective_of(camera)
    right = viewplane.get_right_from_perspective_of(camera)
    bottom_right = top_left + right * viewplane.size.x
    tl_flat = glm.vec2(top_left.x, top_left.z) * map_scale + map_offset * map_scale
    br_flat = (
        glm.vec2(bottom_right.x, bottom_right.z) * map_scale + map_offset * map_scale
    )
    pygame.draw.line(surface, (255, 0, 0), tl_flat, br_flat)

    # Draw the world boundaries
    world_size = glm.vec2(world.dim, world.dim) * map_scale
    world_pos = glm.vec2(world.pos.x, world.pos.z) * map_scale + map_offset * map_scale
    pygame.draw.rect(surface, (0, 0, 255), (*world_pos, *world_size), 1)

    # Draw white dot on the center of each object in the world
    for obj in world.genned_objects:
        obj_pos = glm.vec2(obj.pos.x, obj.pos.z) * map_scale + map_offset * map_scale
        pygame.draw.circle(
            surface, (255, 255, 255), (int(obj_pos.x), int(obj_pos.y)), 2
        )


def draw_ui(surface, map_surface, font, fps):
    # draw crosshair in full-resolution UI space
    cx = int(window_size.x // 2)
    cy = int(window_size.y // 2)
    pygame.draw.line(surface, (0, 255, 0), (cx - 7, cy), (cx + 7, cy), 1)
    pygame.draw.line(surface, (0, 255, 0), (cx, cy - 7), (cx, cy + 7), 1)

    # draw text stats in full-resolution UI space
    lines = [
        f"FPS: {fps:.1f}",
        f"Mode: {mode.name}",
        f"Cam: ({camera.pos.x:.2f}, {camera.pos.y:.2f}, {camera.pos.z:.2f})",
        f"Dir: ({camera.dir.x:.2f}, {camera.dir.y:.2f}, {camera.dir.z:.2f})",
        f"Ray steps: {NUM_RAY_STEPS}, step: {MARCH_STEP_SIZE:.2f}",
    ]
    text_x = 10
    text_y = 10
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        shadow_surface = font.render(line, True, (0, 0, 0))
        surface.blit(shadow_surface, (text_x + 1, text_y + 1))
        surface.blit(text_surface, (text_x, text_y))
        text_y += text_surface.get_height() + 4

    map_margin = 8
    map_pos = (
        int(window_size.x - map_surface.get_width() - map_margin),
        int(window_size.y - map_surface.get_height() - map_margin),
    )
    surface.blit(map_surface, map_pos)


def main():
    global mode
    # first person view
    window = pygame.display.set_mode(v2totuple(window_size), pygame.HWSURFACE)
    render_surface = pygame.Surface(v2totuple(render_resolution), pygame.HWSURFACE)

    # full-res UI resources
    map_fraction = 4
    map_resolution = glm.vec2(
        int(window_size.x / map_fraction), int(window_size.y / map_fraction)
    )
    map_render_surface = pygame.Surface(v2totuple(map_resolution), pygame.SRCALPHA)
    stats_font = pygame.font.SysFont("Consolas", 18)
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick()
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)
            ):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                mode = Mode.ORBIT if mode == Mode.FLIGHT else Mode.FLIGHT

        render_surface.fill((0, 0, 0))
        step()
        draw_world(render_surface)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        window.blit(stretched_surface, (0, 0))

        map_render_surface.fill((0, 0, 0, 160))
        draw_map(map_render_surface)
        draw_ui(window, map_render_surface, stats_font, fps)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
