##
## Lab 30: CMake Recomp Project
##
## Complete this CMakeLists.txt to build a recompilation project with:
##   - A static library from generated/ sources
##   - A static library from shims/ sources
##   - An executable linking both libraries
##

# TODO: Set the minimum CMake version to 3.14.
# Hint: cmake_minimum_required(VERSION 3.14)

# TODO: Declare the project. Name it "recomp_project" with language C.
# Hint: project(recomp_project C)

# TODO: Set the C standard to C11.
# Hint: set(CMAKE_C_STANDARD 11)
#       set(CMAKE_C_STANDARD_REQUIRED ON)

## -----------------------------------------------------------------------
## Library 1: recomp_generated
## -----------------------------------------------------------------------
## This library contains the auto-generated lifted code.

# TODO: Create a STATIC library called "recomp_generated" from
#       the source file generated/sample_lifted.c.
# Hint: add_library(recomp_generated STATIC generated/sample_lifted.c)

# TODO: Add the shims/ directory as an include path for recomp_generated
#       so it can #include "stub_shim.h".
# Hint: target_include_directories(recomp_generated PRIVATE shims)

## -----------------------------------------------------------------------
## Library 2: recomp_shims
## -----------------------------------------------------------------------
## This library contains hand-written hardware abstraction stubs.

# TODO: Create a STATIC library called "recomp_shims" from
#       the source file shims/stub_shim.c.
# Hint: add_library(recomp_shims STATIC shims/stub_shim.c)

# TODO: Make the shims/ headers available to anything that links this
#       library (use PUBLIC include directories).
# Hint: target_include_directories(recomp_shims PUBLIC shims)

## -----------------------------------------------------------------------
## Executable: recomp_runner
## -----------------------------------------------------------------------

# TODO: Create an executable called "recomp_runner" from main.c.
# Hint: add_executable(recomp_runner main.c)

# TODO: Link both libraries to the executable.
# Hint: target_link_libraries(recomp_runner PRIVATE recomp_generated recomp_shims)
