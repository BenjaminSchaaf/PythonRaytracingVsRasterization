#!/usr/bin/env python

import sys
import Rasterized
import pygame
import random
import logging
from module import ObjImporter
from module.math3d import *
from module.objects import *

def get_renderer():
    return Rasterized.Rasterizer(512, 512)

def get_objects():
    meshes = ObjImporter.load("test.obj")

    objects = []
    for mesh in meshes:
        obj = Object()
        obj.mesh = mesh
        objects.append(obj)

    return objects

def get_camera():
    camera = Camera()
    camera.position[2] = -6
    return camera

def make_light():
    light = Light(POINT_LIGHT)
    light.position = random_vector3()*5
    light.linear_atten = 1/8.0
    return light

def random_vector3():
    return Vector(random.random()*2 - 1,
                  random.random()*2 - 1,
                  random.random()*2 - 1)

def main():
    renderer = get_renderer()
    objects = get_objects()
    camera = get_camera()

    renderer.add_objects(objects)
    #renderer.add_lights([make_light(), make_light()])


    keys = {}
    running = True
    keydown = False
    while running:
        renderer.render(camera)

        maps = {pygame.K_w : Vector(0, 0, 0.1),
                pygame.K_s : Vector(0, 0, -0.1),
                pygame.K_d : Vector(0.1, 0, 0),
                pygame.K_a : Vector(-0.1, 0, 0),
                pygame.K_e : Vector(0, 0.1, 0),
                pygame.K_q : Vector(0, -0.1, 0),}
        for key in maps:
            if keys.get(key, False):
                camera.position += maps[key]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys[event.key] = True
            if event.type == pygame.KEYUP:
                keys[event.key] = False

if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        logging.exception("")
    pygame.quit()
