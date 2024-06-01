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

world = World(16)
world_center = glm.vec3(world.dim / 2, world.dim / 2, world.dim / 2)
world.gen_cube(glm.vec3(0, 0, 0), glm.vec3(4, 4, 4), True)
camera = Camera(glm.vec3(0, 0, -10), glm.vec3(0, 0, 1), 5.0)
viewplane = Viewplane(glm.vec2(4, 3), render_resolution.x / render_resolution.y)

camera.dir = glm.vec3(0, 0, -1)
camera.pos = glm.vec3(0, 0, -0)

NUM_RAY_STEPS = 20
MARCH_STEP_SIZE = 1.0

def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution

def step():
    # tm = 1.0
    # t = pygame.time.get_ticks() / 1000 * tm
    # orbit_radius = 5
    # camera.dir = glm.vec3(math.sin(t), 0, math.cos(t))
    # camera.pos = glm.vec3(math.sin(t) * orbit_radius, 0, math.cos(t) * orbit_radius)

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
        camera.pos += glm.vec3(0, cam_speed, 0)
    if keys[pygame.K_LSHIFT]:
        camera.pos -= glm.vec3(0, cam_speed, 0)

    # reset pos on r press
    if keys[pygame.K_r]:
        camera.pos = glm.vec3(0, 0, -10)
        camera.dir = glm.vec3(0, 0, 1)
        

    # print the cam pos
    print(f"Camera pos: {camera.pos}, dir: {camera.dir}")

def draw(surface):
    x = 0
    y = 0
    for target in viewplane.get_targets(camera, render_resolution):
        ray = target - camera.pos
        ray = glm.normalize(ray)
        hit = False
        pos = copy.copy(camera.pos)
        for i in range(NUM_RAY_STEPS):
            pos += ray * MARCH_STEP_SIZE
            pos_in_world_space = pos - world.pos
            wp = glm.floor(pos_in_world_space)
            if world.is_in_bounds(wp):
                if world.voxels[int(wp.x)][int(wp.y)][int(wp.z)]:
                    hit = True
                    break
        color = (0, 0, 0)
        if hit:
            color = (255, 255, 255)
        pygame.draw.rect(surface, color, (x, y, 1, 1))

        x += 1
        if x >= (int(render_resolution.x)-1):
            x = 0
            y += 1
    
    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 2)

def draw_map(surface):
    # draw a green circle at the cam pos, obviously ignore y
    cam_pos = glm.vec2(camera.pos.x, camera.pos.z)

    pygame.draw.circle(surface, (0, 255, 0), (int(cam_pos.x), int(cam_pos.y)), 2)

    # draw a line going out from the camera in the direction 
    # of the camera dir
    cam_dir = glm.normalize(camera.dir)
    cam_dir = glm.vec2(cam_dir.x, cam_dir.z)
    end = cam_pos + cam_dir * 10
    pygame.draw.line(surface, (0, 255, 0), cam_pos, end)

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
        window.blit(stretched_surface, (0, 0))

        map_render_surface.fill((0, 0, 0))
        draw_map(map_render_surface)

        # put the map in the bottom right corner
        map_stretched_surface = pygame.transform.scale(map_render_surface, (int(window_size.x / 3), int(window_size.y / 3)))
        window.blit(map_stretched_surface, (window_size.x - map_stretched_surface.get_width(), window_size.y - map_stretched_surface.get_height()))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
