#include <framework.h>
#include <stdio.h>
#include <stdlib.h>

static int quit = 0;

void
onQuit()
{
    quit = 1;
}

void
onKeyPress(unsigned char key)
{

}

void
onKeyRelease(unsigned char key)
{
}

void
onMousePress(int x, int y, unsigned char buttons)
{

}

void
onMouseRelease(int x, int y, unsigned char buttons)
{

}

void
onMouseMove(int x, int y, unsigned char buttons)
{

}

int
main(int argc, char *argv[])
{
    const int width = 800;
    const int height = 600;

    if (!openDisplay("test!!!!", width, height, 0, 1))
        return EXIT_FAILURE;

    const char *version = (const char*)glGetString(GL_VERSION);
    const char *renderer = (const char*)glGetString(GL_RENDERER);
    const char *vendor = (const char*)glGetString(GL_VENDOR);

    int extensions = 0;
    glGetIntegerv(GL_NUM_EXTENSIONS, &extensions);

    printf("opengl version: %s\nopengl renderer: %s\nopengl vendor: %s\n", version, renderer, vendor);
    printf("opengl extensions(%d):\n", extensions);

    for(int i = 0; i < extensions; i++)
        printf("\t%s\n", (const char*)glGetStringi(GL_EXTENSIONS, i));

    while (!quit)
    {
        glViewport(0, 0, width, height);
        glClearColor(0.3f, 0.3f, 0.3f, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        updateDisplay();
    }

    closeDisplay();

    return EXIT_SUCCESS;
}
