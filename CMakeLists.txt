cmake_minimum_required(VERSION 2.8)

project("GL coregen Test")

list(APPEND CMAKE_C_FLAGS "-std=c11 -Wall -w -pedantic -static-libgcc -U__STRICT_ANSI__")

set(headers
include/framework.h
)

set(sources
src/glcore.c
#src/gles2core.c
#src/wglextensions.c
#windows.c
#threads.c
src/test.cpp
src/sdl/framework.c
#src/x11/window.c
)

include_directories("./include")
add_definitions(-DUSING_SDL)

add_executable(test ${headers} ${sources})
#target_link_libraries(test -lopengl32 -lmingw32)
#target_link_libraries(test -lSDL2 -lEGL -lGLESv2 -lX11)
target_link_libraries(test -lSDL2)
