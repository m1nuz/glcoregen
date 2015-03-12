#pragma once

//#define USE_OPENGL_33
//#define USE_OPENGL_43
//#define USE_OPENGL_45
#define USE_OPENGL_ES2

#ifdef USE_OPENGL_33
#define OPENGL_MAJOR_VERSION 3
#define OPENGL_MINOR_VERSION 3
#endif

#ifdef USE_OPENGL_43
#define OPENGL_MAJOR_VERSION 4
#define OPENGL_MINOR_VERSION 3
#endif

#ifdef USE_OPENGL_45
#define OPENGL_MAJOR_VERSION 4
#define OPENGL_MINOR_VERSION 5
#endif

#ifdef USE_OPENGL_ES2
#define OPENGL_MAJOR_VERSION 2
#define OPENGL_MINOR_VERSION 0
#endif

#ifdef _WIN32

#define VC_EXTRALEAN
#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <windowsx.h>
#include <win32keys.h>

#endif

#if defined(USE_OPENGL_33) || defined(USE_OPENGL_43) || defined(USE_OPENGL_45)
#include <GL/glcore.h>
#endif

#ifdef USE_OPENGL_ES2
#include <GL/glcore.h>
#endif

#ifdef __cplusplus
#define NATIVE_CALL extern "C"
#else
#define NATIVE_CALL extern
#endif // __cplusplus

#ifdef __cplusplus
extern "C" {
#endif

int openDisplay(const char *title, int width, int height, int fullscreen, int cursor);
void updateDisplay(void);
void closeDisplay(void);
void setTitle(const char *title);

float time(void);

void* createThread(void (*func)(void *), void *user);
void destroyThread(void* thread);

#ifdef __cplusplus
} // extern "C"
#endif

NATIVE_CALL void onQuit(void);
NATIVE_CALL void onKeyPress(unsigned char key);
NATIVE_CALL void onKeyRelease(unsigned char key);
NATIVE_CALL void onMousePress(int x, int y, unsigned char buttons);
NATIVE_CALL void onMouseRelease(int x, int y, unsigned char buttons);
NATIVE_CALL void onMouseMove(int x, int y, unsigned char buttons);
