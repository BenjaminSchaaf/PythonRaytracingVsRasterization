from __future__ import division

import time
import sys, os
import pygame

from common import ObjImporter
from common.objects import Camera
from rasterized import Rasterizer
from raytraced import Raytracer

CAMERA = Camera()
CAMERA.position[2] = -6

def main(renderer, test, duration = 20, width = 500, height = 500):
    object = ObjImporter.load(os.path.join("tests", test))[0]

    resolution = int(width), int(height)
    renderer = {
        "rasterized" : Rasterizer,
        "raytraced" : Raytracer,
    }[renderer](resolution, object)

    results = []
    start_time = time.time()
    while time.time() - start_time < int(duration):
        start = time.clock()
        renderer.render(CAMERA)
        fps = 1 / (time.clock() - start)
        results.append(fps)

        #Help pygame stay alive
        pygame.event.get()

    renderer.close()

    #Return average
    return sum(results) / len(results)

if __name__ == "__main__":
    result = main(*sys.argv[1:])
    print(result)
