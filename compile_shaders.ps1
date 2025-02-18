$shaders = Get-ChildItem res/shaders -Recurse -File -Exclude "*.spv"

foreach ($shader in $shaders) {
    glslc $shader -I "res/shaders" --target-env=vulkan -O -o "$($shader.FullName).spv"
}
