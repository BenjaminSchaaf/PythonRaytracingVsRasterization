from __future__ import division

import time
import os, sys

from rasterized import Rasterizer
from raytraced import Raytracer
from module import ObjImporter
from module.objects import Camera
import pygame

RENDERERS = Rasterizer, Raytracer
RESOLUTIONS = [
    (500, 500),
]
TEST_LENGTH = 20

def load_objects():
    objects = []

    #Load all files from tests directory
    for file in os.listdir("tests"):
        objects += ObjImporter.load(os.path.join("tests", file))

    return objects

def get_camera():
    camera = Camera()
    camera.position[2] = -6
    return camera

def main():
    objects = load_objects()
    camera = get_camera()

    #Redirect stdout and stderr to nothing
    devnull = open(os.devnull, 'w')
    stdout = sys.stdout
    sys.stdout = devnull

    results = []
    for renderer in RENDERERS:
        renderer_results = []

        for object in objects:
            for resolution in RESOLUTIONS:
                instance = renderer(resolution, object)
                #Warmup render
                try:
                    instance.render(camera)
                except:
                    renderer_results.append(None)
                    continue

                start_time = time.time()
                object_times = []
                while time.time() - start_time < TEST_LENGTH:
                    #Test framerate
                    start = time.clock()
                    instance.render(camera)
                    total = time.clock() - start
                    fps = 1 / total
                    #Add result
                    object_times.append(fps)
                    #Fix pygame shit
                    pygame.event.get()

                average_fps = sum(object_times) / len(object_times)
                renderer_results.append(average_fps)
                instance.close()

        results.append(renderer_results)

    #Direct stdout back to stdout
    sys.stdout = stdout
    devnull.close()

    #Print Results
    for index in range(len(RENDERERS)):
        renderer = RENDERERS[index]
        print("Results for %s:" % renderer.__name__)
        for result_index in range(len(results[index])):
            result_name = objects[result_index].file
            result = results[index][result_index]

            if result is not None:
                print("  %s: %s" % (result_name, result))
            else:
                print("  %s: FAIL!" % result_name)

if __name__ == "__main__":
    main()
