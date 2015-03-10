#include "framework.h"

extern float
time()
{
    static __int64 start = 0;
    static __int64 frequency = 0;

    if (start == 0)
    {
        QueryPerformanceCounter((LARGE_INTEGER*)&start);
        QueryPerformanceFrequency((LARGE_INTEGER*)&frequency);
        return 0.0f;
    }

    __int64 counter = 0;
    QueryPerformanceCounter((LARGE_INTEGER*)&counter);
    return (float) ((counter - start) / (double)frequency);
}

extern void*
createThread(void (*func)(void *), void *user)
{
    return CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)func, user, 0, NULL);
}

extern void
destroyThread(void* thread)
{
    CloseHandle((HANDLE)thread);
}
