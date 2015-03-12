#include "framework.h"

#include <stddef.h>
#include <stdio.h>

#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>

#include <EGL/egl.h>

Display     *x_display;
Window      x_window;
char        *x_display_name = NULL;
Atom        wm_delete;

EGLSurface  egl_surface;
EGLContext  egl_context;
EGLDisplay  egl_display;

static void
print_egl_info(void)
{
    const char *s;
    s = eglQueryString(egl_display, EGL_VERSION);
    printf("EGL version: %s\n", s);

    s = eglQueryString(egl_display, EGL_VENDOR);
    printf("EGL vendor: %s\n", s);

    s = eglQueryString(egl_display, EGL_EXTENSIONS);
    printf("EGL extentions: %s\n", s);

    s = eglQueryString(egl_display, EGL_CLIENT_APIS);
    printf("EGL client APIs: %s\n", s);
}

static int
init_EGL()
{
    EGLint egl_major, egl_minor;

    if ((egl_display = eglGetDisplay(x_display)) == NULL) {
        fprintf(stderr, "Error: eglGetDisplay() failed\n");
        return 0;
    }

    if (!eglInitialize(egl_display, &egl_major, &egl_minor)) {
        printf("Error: eglInitialize() failed\n");
        return 0;
    }

    eglBindAPI(EGL_OPENGL_ES_API);

    EGLint attributes[] = {
        EGL_BUFFER_SIZE, 16,
        EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
        EGL_NONE
    };

    EGLConfig  egl_config;
    EGLint     num_config;
    if (!eglChooseConfig(egl_display, attributes, &egl_config, 1, &num_config)) {
        fprintf(stderr, "Failed to choose config (eglError: %s)\n" , eglGetError());
        return 0;
    }

    if ((egl_surface = eglCreateWindowSurface(egl_display, egl_config, x_window, NULL)) == EGL_NO_SURFACE) {
        fprintf(stderr, "Unable to create EGL surface (eglError: %s)\n", eglGetError());
        return 1;
    }

    EGLint context_attributes[] = {
        EGL_CONTEXT_CLIENT_VERSION, 2,
        EGL_NONE
    };

    if ((egl_context = eglCreateContext(egl_display, egl_config, EGL_NO_CONTEXT, context_attributes)) == EGL_NO_CONTEXT) {
        fprintf(stderr,  "Unable to create EGL context (eglError: %s)\n", eglGetError());
        return 1;
    }

    print_egl_info();

    eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context);

    glLoadFunctions();
}

static void
swap_EGL_buffer()
{
    eglSwapBuffers(egl_display, egl_surface);
}

static void
clenup_EGL()
{
    eglDestroyContext(egl_display, egl_context);
    eglDestroySurface(egl_display, egl_surface);
    eglTerminate(egl_display);
}

int
openDisplay(const char *title, int width, int height, int fullscreen, int cursor)
{
    if ((x_display = XOpenDisplay(x_display_name)) == NULL) {
        fprintf(stderr, "Error: Cannot open display %s\n", x_display_name);
        return 0;
    }

    Window root = DefaultRootWindow(x_display);

    XSetWindowAttributes  swa;
    swa.event_mask  =  ExposureMask | PointerMotionMask | KeyPressMask;

    x_window = XCreateWindow(x_display, root,
                  0, 0, width, height,   0,
                  CopyFromParent, InputOutput,
                  CopyFromParent, CWEventMask,
                  &swa );

    if (fullscreen == 1) {
        XSetWindowAttributes  xattr;
        Atom  atom;
        int   one = 1;

        xattr.override_redirect = False;
        XChangeWindowAttributes(x_display, x_window, CWOverrideRedirect, &xattr);

        atom = XInternAtom(x_display, "_NET_WM_STATE_FULLSCREEN", True);
        XChangeProperty(x_display, x_window,
                    XInternAtom ( x_display, "_NET_WM_STATE", True ),
                    XA_ATOM,  32,  PropModeReplace,
                    (unsigned char*) &atom,  1 );

        XChangeProperty(x_display, x_window,
                    XInternAtom ( x_display, "_HILDON_NON_COMPOSITED_WINDOW", True ),
                    XA_INTEGER,  32,  PropModeReplace,
                    (unsigned char*) &one,  1);

        Atom wm_state   = XInternAtom ( x_display, "_NET_WM_STATE", False );
        Atom wm_fullscreen = XInternAtom ( x_display, "_NET_WM_STATE_FULLSCREEN", False );

        XEvent xev;
        memset(&xev, 0, sizeof(xev));

        xev.type                 = ClientMessage;
        xev.xclient.window       = x_window;
        xev.xclient.message_type = wm_state;
        xev.xclient.format       = 32;
        xev.xclient.data.l[0]    = 1;
        xev.xclient.data.l[1]    = wm_fullscreen;
        XSendEvent(x_display,
                   DefaultRootWindow ( x_display ),
                   False,
                   SubstructureNotifyMask,
                   &xev );
    }

    wm_delete = XInternAtom(x_display, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(x_display, x_window, &wm_delete, 1);

    XWMHints hints;
    hints.input = True;
    hints.flags = InputHint;
    XSetWMHints(x_display, x_window, &hints);

    XMapWindow(x_display , x_window);
    XStoreName(x_display , x_window, title);

    init_EGL();

    return 1;
}

void
updateDisplay(void)
{
    XEvent event;
    while(XPending(x_display) > 0)
    {
        XNextEvent(x_display, &event);

        switch(event.type) {
        case ClientMessage:
            if (event.xclient.format == 32 && event.xclient.data.l[0] == wm_delete)
                onQuit();
            break;
        }
    }

    swap_EGL_buffer();
}

void
closeDisplay(void)
{
    clenup_EGL();

    XCloseDisplay(x_display);
}
