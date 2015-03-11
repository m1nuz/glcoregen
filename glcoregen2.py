#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as etree

EXT_FILE = ''
CORE_PROFILE = ''

# Check if arg is a valid file that already exists on the file system
def is_valid_file(parser, arg):
	arg = os.path.abspath(arg)
	if not os.path.exists(arg):
		parser.error('The file %s does not exist!' % arg)
	else:
		return arg

# Parce command line
def get_parser():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-f', '--file', dest='ext_file', type=lambda x: is_valid_file(parser, x), help='features and extentions text file', metavar='FILE')
	parser.add_argument('-p', '--profile', dest='profile', help='Core profile GL, ES (default: GL)', metavar='PROFILE', default='GL')
	return parser

if __name__ == '__main__':
	args = get_parser().parse_args()
	print('Get features and extentions from ' + args.ext_file)
	print('With core profile ' + args.profile)
	EXT_FILE = args.ext_file
	CORE_PROFILE = args.profile

# Create directories
if not os.path.exists('include/GL'):
    os.makedirs('include/GL')
if not os.path.exists('src'):
    os.makedirs('src')
if not os.path.exists('spec'):
    os.makedirs('spec')

# Download glcorearb.h
if not os.path.exists('include/GL/glcorearb.h'):
    print('Downloading glcorearb.h to include/GL...')
    web = urllib.request.urlopen('http://www.opengl.org/registry/api/glcorearb.h')
    with open('include/GL/glcorearb.h', 'wb') as f:
        f.writelines(web.readlines())
else:
    print('Reusing glcorearb.h from include/GL...')

# Download gl.xml
if not os.path.exists('spec/gl.xml'):
    print('Downloading gl.xml...')
    web = urllib.request.urlopen('https://cvs.khronos.org/svn/repos/ogl/trunk/doc/registry/public/api/gl.xml')
    with open('spec/gl.xml', 'wb') as f:
        f.writelines(web.readlines())
else:
    print('Reusing gl.xml from spec/...')

def proc_t(proc):
    return { 'name': proc,
             'variable': '_gl' + proc[2:],
             'prototype': 'PFN' + proc.upper() + 'PROC' }

# Read config
with open(EXT_FILE, 'r') as f:
	extentions_needed = f.read().splitlines()
	f.close()

# Parce gl.xml
tree = etree.parse('spec/gl.xml')
root = tree.getroot()

all_commands = root.findall('commands')
all_commands = all_commands[0].findall('command')

# Parce features
requirements = []
features = root.findall('feature')
print('Features:')
for feature in features:
	if feature.attrib['name'] in extentions_needed:
		print('\t' + feature.attrib['name'])
		for require in feature.findall('require'):
			if require.attrib.get('profile') != 'compatibility':
				requirements.append(require)

# Build commands list
commands = []

for require in requirements:
	for command in require.findall('command'):
		commands.append(command.attrib['name'])

remove_commands = []

# remove commands with remove features
for feature in features:
	if feature.attrib['name'] in extentions_needed:
		for require in feature.findall('require'):
			for remove in feature.findall('remove'):
				for command in remove.findall('command'):
					remove_commands.append(command.attrib['name'])

commands = [command for command in commands if command not in remove_commands]

# Parce extensions
print('Extensions:')
extensions = root.find('extensions').findall('extension')
for extension in extensions:
	if extension.attrib['name'] in extentions_needed:
		print('\t' + extension.attrib['name'])
		for require in feature.findall('require'):
			for command in require.findall('command'):
				commands.append(command.attrib['name'])

# Generate glcore.h
print('Generating glcore.h in include/GL...')
with open('include/GL/glcore.h', 'wb') as f:
	f.write(bytes('''/* Generated by glcoregen v2 */
#pragma once
#include <GL/glcorearb.h>

#ifndef __gl_h_
#define __gl_h_
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Core GL API */
int glLoadFunctions(void);
void *nativeGetProcAddress(const char *proc);

/* OpenGL functions */
''', 'utf8'))	
	for command in commands:
		proc = proc_t(command)
		f.write(bytes('extern %s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
	for command in commands:
		proc = proc_t(command)
		f.write(bytes('#define %s %s\n' % (proc['name'], proc['variable']), 'utf8'))
	f.write(bytes('''
#ifdef __cplusplus
}
#endif

''', 'utf8'))
	f.close()

# Generate glcore.c
print('Generating glcore.c in src/GL...')
with open('src/glcore.c', 'wb') as f:
	f.write(bytes('''/* Generated by glcoregen v2 */
#include <GL/glcore.h>

#ifdef USING_SDL

#include <SDL2/SDL.h>

static void open_libgl(void)
{
	SDL_GL_LoadLibrary(NULL);
}

static void close_libgl(void)
{
	SDL_GL_UnloadLibrary();
}

typedef void (*VOIDFUNC)(void);

static VOIDFUNC get_proc(const char *proc)
{
    // no valid cast between pointer to function and pointer to object
    union {
        void *p;
        VOIDFUNC f;
    } ptr;

    ptr.p = SDL_GL_GetProcAddress(proc);

    return ptr.f;
}

#else

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN 1
#include <windows.h>

static HMODULE libgl;

static void open_libgl(void)
{
	libgl = LoadLibraryA("opengl32.dll");
}

static void close_libgl(void)
{
	FreeLibrary(libgl);
}

static void *get_proc(const char *proc)
{
	void *res;

	res = wglGetProcAddress(proc);
	if (!res)
		res = GetProcAddress(libgl, proc);
	return res;
}
#elif defined(__APPLE__) || defined(__APPLE_CC__)
#include <Carbon/Carbon.h>

CFBundleRef bundle;
CFURLRef bundleURL;

static void open_libgl(void)
{
	bundleURL = CFURLCreateWithFileSystemPath(kCFAllocatorDefault,
		CFSTR("/System/Library/Frameworks/OpenGL.framework"),
		kCFURLPOSIXPathStyle, true);

	bundle = CFBundleCreate(kCFAllocatorDefault, bundleURL);
	assert(bundle != NULL);
}

static void close_libgl(void)
{
	CFRelease(bundle);
	CFRelease(bundleURL);
}

static void *get_proc(const char *proc)
{
	void *res;

	CFStringRef procname = CFStringCreateWithCString(kCFAllocatorDefault, proc,
		kCFStringEncodingASCII);
	res = CFBundleGetFunctionPointerForName(bundle, procname);
	CFRelease(procname);
	return res;
}
#else
#include <dlfcn.h>
#include <GL/glx.h>

static void *libgl;

static void open_libgl(void)
{
	libgl = dlopen("libGL.so.1", RTLD_LAZY | RTLD_GLOBAL);
}

static void close_libgl(void)
{
	dlclose(libgl);
}

static void *get_proc(const char *proc)
{
	void *res;

	res = glXGetProcAddress((const GLubyte *) proc);
	if (!res)
		res = dlsym(libgl, proc);
	return res;
}
#endif

#endif /* USING_SDL */

static void load_procs(void);

int glLoadFunctions(void)
{
	open_libgl();
	load_procs();
	close_libgl();
	return 1;
}

void *nativeGetProcAddress(const char *proc)
{
	return get_proc(proc);
}

''', 'utf8'))
	for command in commands:
		proc = proc_t(command)
		f.write(bytes('%s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
	f.write(bytes('''
static void load_procs(void)
{
''', 'utf8'))
	for command in commands:
		proc = proc_t(command)
		f.write(bytes('\t%s = (%s) get_proc(\"%s\");\n' % (proc['variable'], proc['prototype'], proc['name']), "utf8"))
	f.write(bytes('}\n', 'utf8'))
	f.close()