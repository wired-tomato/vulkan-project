#!/bin/bash

find ./res/shaders -type f -name "*" -not -name "*.spv" -exec glslc {} -I "res/shaders" --target-env=vulkan -O -o {}.spv \;
