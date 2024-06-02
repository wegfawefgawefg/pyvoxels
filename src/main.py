import copy
import math
import pygame
import glm
from world import World
from camera import Camera
from viewplane import Viewplane

pygame.init()

render_resolution = glm.vec2(64, 48)
window_size = render_resolution * 12

world = World(2)
world.gen_cube(glm.vec3(0, 0, 0), glm.vec3(2, 2, 2), True)
camera = Camera(glm.vec3(0, 0, 0), glm.vec3(0, 0, -1), 4.69)
viewplane = Viewplane(glm.vec2(4, 3), render_resolution.x / render_resolution.y)

NUM_RAY_STEPS = 40
MARCH_STEP_SIZE = 0.5

def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution

def step():
    tm = 1.0
    t = pygame.time.get_ticks() / 1000 * tm
    orbit_radius = 10
    camera.dir = -glm.vec3(math.sin(t), 0, math.cos(t))
    cam_height = camera.pos.y
    camera.pos = glm.vec3(math.sin(t) * orbit_radius, 0, math.cos(t) * orbit_radius)
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
        camera.dir = glm.rotate(camera.dir, rotation_speed, glm.vec3(0, 1, 0))
    if keys[pygame.K_d]:
        camera.dir = glm.rotate(camera.dir, -rotation_speed, glm.vec3(0, 1, 0))
    # space for up, and shift for down
    if keys[pygame.K_SPACE]:
        camera.pos += glm.vec3(0, cam_speed, 0)
    if keys[pygame.K_LSHIFT]:
        camera.pos -= glm.vec3(0, cam_speed, 0)

    # reset pos on r press
    if keys[pygame.K_r]:
        camera.reset()
        
    # t and g to move the viewplane closer and further
    if keys[pygame.K_t]:
        camera.viewplane_distance -= 0.1
    if keys[pygame.K_g]:
        camera.viewplane_distance += 0.1

    # print the cam pos
    print(f"Camera pos: {camera.pos}, dir: {camera.dir}, vpd: {camera.viewplane_distance}")

def draw(surface):
    x = 0
    y = 0
    for target in viewplane.get_targets(camera, render_resolution):
        ray = target - camera.pos
        ray = glm.normalize(ray)
        hit = False
        dist_to_hit = NUM_RAY_STEPS * MARCH_STEP_SIZE
        pos = copy.copy(camera.pos)
        for i in range(NUM_RAY_STEPS):
            pos += ray * MARCH_STEP_SIZE
            pos_in_world_space = pos - world.pos
            wp = glm.floor(pos_in_world_space)
            if world.is_in_bounds(wp):
                if world.voxels[int(wp.x)][int(wp.y)][int(wp.z)]:
                    hit = True
                    dist_to_hit = glm.length(pos - camera.pos)
                    break
        color = (0, 0, 0)
        if hit:
            color = (255, 255, 255)
            brightness = 1 - dist_to_hit / (NUM_RAY_STEPS * MARCH_STEP_SIZE)
            color = tuple(int(c * brightness) for c in color)
        pygame.draw.rect(surface, color, (x, y, 1, 1))

        x += 1
        if x >= int(render_resolution.x):
            x = 0
            y += 1
    
    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 2)


def draw_map(surface):
    # Minimap parameters
    map_offset = glm.vec2(10, 10)
    map_scale = 8

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
    br_flat = glm.vec2(bottom_right.x, bottom_right.z) * map_scale + map_offset * map_scale
    pygame.draw.line(surface, (255, 0, 0), tl_flat, br_flat)

    # Draw the world boundaries
    world_size = glm.vec2(world.dim, world.dim) * map_scale
    world_pos = glm.vec2(world.pos.x, world.pos.z) * map_scale + map_offset * map_scale
    pygame.draw.rect(surface, (0, 0, 255), (*world_pos, *world_size), 1)

    # Draw white dot on the center of each object in the world
    for obj in world.genned_objects:
        obj_pos = glm.vec2(obj.pos.x, obj.pos.z) * map_scale + map_offset * map_scale
        pygame.draw.circle(surface, (255, 255, 255), (int(obj_pos.x), int(obj_pos.y)), 2)

def main():
    # first person view
    window = pygame.display.set_mode(window_size.to_tuple())
    render_surface = pygame.Surface(render_resolution.to_tuple())

    # map view
    map_resolution = glm.vec2(200, 200)
    map_render_surface = pygame.Surface(map_resolution.to_tuple())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                running = False

        render_surface.fill((0, 0, 0))
        step()
        draw(render_surface)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        y_flip_surface = pygame.transform.flip(stretched_surface, False, True)
        window.blit(y_flip_surface, (0, 0))

        map_render_surface.fill((0, 0, 0))
        draw_map(map_render_surface)

        # put the map in the bottom right corner
        map_stretched_surface = pygame.transform.scale(map_render_surface, (int(window_size.x / 3), int(window_size.y / 3)))
        window.blit(map_stretched_surface, (window_size.x - map_stretched_surface.get_width(), window_size.y - map_stretched_surface.get_height()))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
