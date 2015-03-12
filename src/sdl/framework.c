#include <SDL2/SDL.h>

#include "framework.h"

SDL_Window *window;
SDL_GLContext context;

int
openDisplay(const char *title, int width, int height, int fullscreen, int cursor)
{
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "%s\n", SDL_GetError());
        return 0;
    }

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, OPENGL_MAJOR_VERSION);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, OPENGL_MINOR_VERSION);

#ifdef USE_OPENGL_ES2
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES);
#elif defined(USE_OPENGL_33) || defined(USE_OPENGL_43) || defined(USE_OPENGL_45)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG);
#endif

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);

    Uint32 flags = SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN;

    if(fullscreen != 0)
        flags |= SDL_WINDOW_FULLSCREEN;

    if ((window = SDL_CreateWindow(title, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, flags)) == NULL) {
        fprintf(stderr, "%s\n", SDL_GetError());
        return 0;
    }

    if ((context = SDL_GL_CreateContext(window)) == NULL) {
        fprintf(stderr, "%s\n", SDL_GetError());
        return 0;
    }

    SDL_ShowCursor(cursor == 1);

    glLoadFunctions();

    return 1;
}

void
updateDisplay(void)
{
    SDL_Event event;

    while (SDL_PollEvent(&event))
        switch (event.type) {
        case SDL_QUIT:
            onQuit();
            break;
        }


    SDL_GL_SwapWindow(window);
}

void
closeDisplay(void)
{
    SDL_GL_DeleteContext(context);
    SDL_DestroyWindow(window);
    SDL_Quit();
}

void
setTitle(const char *title)
{
    SDL_SetWindowTitle(window, title);
}

float
time(void)
{
    Uint64 current = 0;
    Uint64 last = 0;

    last = current;
    current = SDL_GetPerformanceCounter();
    Uint64 freq = SDL_GetPerformanceFrequency();

    float delta = (double)(current - last) / (double)freq;

    return delta;
}

void*
createThread(void (*func)(void *), void *user)
{
    return SDL_CreateThread(func, NULL, user);
}

void
destroyThread(void* thread)
{
    SDL_DetachThread(thread);
}
