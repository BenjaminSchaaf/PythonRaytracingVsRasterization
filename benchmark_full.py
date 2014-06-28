#!/usr/bin/env python
import sys, os
import benchmark

RENDERERS = "raytraced", "rasterized"
RESOLUTIONS = [
    (500, 500),
]
TEST_LENGTH = 20

def main():
    #Redirect stdout and stderr to nothing
    devnull = open(os.devnull, 'w')
    stdout = sys.stdout
    sys.stdout = devnull

    for renderer in RENDERERS:
        print(renderer)
        for resolution in RESOLUTIONS:
            print(" %sx%s" % resolution)
            for test in os.listdir("tests"):
                result = benchmark.main(renderer, test, TEST_LENGTH, *resolution)
                print("  %s: %s" % (test, result))


    #Direct stdout back to stdout
    sys.stdout = stdout
    devnull.close()

if __name__ == "__main__":
    main()
