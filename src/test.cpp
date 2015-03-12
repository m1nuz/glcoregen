#include <framework.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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

GLuint vertex_buffer;
GLuint shader_program;

#ifdef USE_OPENGL_33
char vertex_shader_text[] =
{
    "#version 330 core\n"
    "layout(location = 0) in vec3 vertex;\n"
    "void main() {\n"
    "gl_Position = vec4(vertex, 1.0);\n"
    "}"
};

char fragment_shader_text[] =
{
    "#version 330 core\n"
    "out vec4 color;\n"
    "void main() {\n"
    "color = vec4(1, 0, 0, 1);\n"
    "}"
};
#endif // USE_OPENGL_33

#ifdef USE_OPENGL_ES2
char vertex_shader_text[] =
{
    "attribute vec3 vertex;\n"
    "void main() {\n"
    "gl_Position = vec4(vertex, 1.0);\n"
    "}"
};

char fragment_shader_text[] =
{
    "precision mediump float;\n"
    "void main() {\n"
    "gl_FragColor = vec4(1, 0, 0, 1);\n"
    "}"
};
#endif // USE_OPENGL_ES2

char shader_log[4096];

static GLuint
compileShader(GLenum type, const char *source)
{
    GLuint sh = glCreateShader(type);

    const char *fullsource[] =  {source, 0};

    glShaderSource(sh, 1, fullsource, 0);
    glCompileShader(sh);

    GLint status = 0;
    glGetShaderiv(sh, GL_COMPILE_STATUS, &status);

    if (!status) {
        GLsizei written = 0;
        glGetShaderInfoLog(sh, sizeof(shader_log), &written, shader_log);

        fprintf(stderr, "%s\n", shader_log);

        return -1;
    }

    return sh;
}

static void
linkShaderProgram(GLuint program)
{
    GLint status = 0;

    glLinkProgram(program);
    glGetProgramiv(program, GL_LINK_STATUS, &status);

    if (!status) {
        GLsizei written = 0;
        glGetProgramInfoLog(program, sizeof(shader_log), &written, shader_log);

        fprintf(stderr, "%s\n", shader_log);
    }
}

void
onInit()
{
    // Create and fill vertex buffer
    const GLfloat vertex_buffer_data[] = {
        -1.0f, -1.0f, 0.0f,
        1.0f, -1.0f, 0.0f,
        0.0f,  1.0f, 0.0f,
    };

    glGenBuffers(1, &vertex_buffer);
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertex_buffer_data), vertex_buffer_data, GL_STATIC_DRAW);

    // Create shader program
    GLuint vertex_shader = compileShader(GL_VERTEX_SHADER, vertex_shader_text);
    GLuint fragment_shader = compileShader(GL_FRAGMENT_SHADER, fragment_shader_text);

    shader_program = glCreateProgram();

    glAttachShader(shader_program, vertex_shader);
    glAttachShader(shader_program, fragment_shader);

    linkShaderProgram(shader_program);

    glDeleteShader(vertex_shader);
    glDeleteShader(fragment_shader);
}

void
onDraw()
{
    glUseProgram(shader_program);

    glEnableVertexAttribArray(0);
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);

    glDrawArrays(GL_TRIANGLES, 0, 3);

    glDisableVertexAttribArray(0);

    glUseProgram(0);
}

void
onCleanup()
{
    glDeleteBuffers(1, &vertex_buffer);
    glDeleteProgram(shader_program);
}

int
main(int argc, char *argv[])
{
    const int width = 800;
    const int height = 600;

    if (!openDisplay("Test application", width, height, 0, 1))
        return EXIT_FAILURE;

    const char *version = (const char*)glGetString(GL_VERSION);
    const char *renderer = (const char*)glGetString(GL_RENDERER);
    const char *vendor = (const char*)glGetString(GL_VENDOR);
    const char *glsl_version = (const char*)glGetString(GL_SHADING_LANGUAGE_VERSION);
    const char *extensions = (const char*)glGetString(GL_EXTENSIONS);;

    printf("GL version: %s\nGL renderer: %s\nGL vendor: %s\nGL shading language version: %s\n", version, renderer, vendor, glsl_version);
    printf("GL extensions:\n %s\n", extensions);

    //glGetIntegerv(GL_NUM_EXTENSIONS, &extensions);
    //for(int i = 0; i < extensions; i++)
    //    printf("\t%s\n", (const char*)glGetStringi(GL_EXTENSIONS, i));

    onInit();

    while (!quit) {
        glViewport(0, 0, width, height);
        glClearColor(0.3f, 0.3f, 0.3f, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        onDraw();

        updateDisplay();
    }

    onCleanup();

    closeDisplay();

    return EXIT_SUCCESS;
}
