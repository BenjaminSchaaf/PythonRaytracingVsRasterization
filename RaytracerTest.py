#!/usr/bin/env python

import sys
import Raytraced
import pygame
import random
import logging
from module import ObjImporter
from module.math3d import *
from module.objects import *

def get_renderer():
    return Raytraced.Raytracer(512, 512)

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
    renderer.add_lights([make_light(), make_light()])

    running = True
    keydown = False
    while running:
        renderer.render(camera)

        if keydown:
            camera.position += random_vector3()*0.2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keydown = True
            if event.type == pygame.KEYUP:
                keydown = False

if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        logging.exception("")
    pygame.quit()
