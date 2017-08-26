#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as etree

CORE_FILE = ''
EXT_FILE = ''
CORE_PROFILE = 'GL'
COMMANDS = []
COMMANDS_PROTO = []
EXT_COMMANDS = []
FEATURES = []
EXTENTIONS = []
GEN_HEADER = 'glcore.h'
GEN_SOURCE = 'glcore.c'

GL_DIRECTORIES = ['include/GL', 'src', 'spec']
GL_HEADERS = [{'header': 'glcorearb.h', 'path': 'include/GL', 'url': 'https://www.khronos.org/registry/OpenGL/api/GL/glcorearb.h'}]
ES2_DIRECTORIES = ['include/GLES2', 'src', 'include/KHR']
ES2_HEADERS = [{'header': 'gl2.h', 'path': 'include/GLES2', 'url': 'https://www.khronos.org/registry/OpenGL/api/GLES2/gl2.h'},
{'header': 'gl2platform.h', 'path': 'include/GLES2', 'url': 'https://www.khronos.org/registry/OpenGL/api/GLES2/gl2platform.h'},
{'header': 'khrplatform.h', 'path': 'include/KHR', 'url': 'https://www.khronos.org/registry/EGL/api/KHR/khrplatform.h'}]

def noneStr(str):
    if (str):
        return str
    else:
        return ''

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
	parser.add_argument('-f', '--file', dest='core_file', type=lambda x: is_valid_file(parser, x), help='features text file', metavar='FILE', default=None)
	parser.add_argument('-e', '--ext', dest='ext_file', type=lambda x: is_valid_file(parser, x), help='extentions text file', metavar='FILE', default=None)
	parser.add_argument('-p', '--profile', dest='profile', help='Core profile GL, ES2, ES3 (default: GL)', metavar='PROFILE', default='GL')
	parser.add_argument('-gh', '--header', dest='header', help='Generated header file (default: glcore.h)', metavar='HEADER', default='glcore.h')
	parser.add_argument('-gs', '--source', dest='source', help='Generated source file (default: glcore.c)', metavar='SOURCE', default='glcore.c')
	return parser

# Create directories
def create_directories():
	global GL_DIRECTORIES
	global CORE_PROFILE
	if CORE_PROFILE == 'GL':
		directories = GL_DIRECTORIES
	else:
		directories = ES2_DIRECTORIES
	print('Create directories')
	for dr in directories:
		if not os.path.exists(dr):
			os.makedirs(dr)
			print('Make directory ' + dr)

# Download glcorearb.h
def download_headers():
	global GL_HEADERS
	for header in GL_HEADERS:
		if not os.path.exists('%s/%s' % (header['path'], header['header'])):
			print('Downloading %s to %s...' % (header['header'], header['path']))
			web = urllib.request.urlopen(header['url'])
			with open('%s/%s' % (header['path'], header['header']), 'wb') as f:
				f.writelines(web.readlines())
		else:
			print('Reusing %s from %s...' % (header['header'], header['path'])) 

# Download gl.xml
def download_specifications():
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
def read_configs():
	global CORE_FILE
	global EXT_FILE
	global FEATURES
	global EXTENTIONS

	with open(CORE_FILE, 'r') as f:
		FEATURES = f.read().splitlines()
		f.close()
	
	if EXT_FILE:
		with open(EXT_FILE, 'r') as f:
			EXTENTIONS = f.read().splitlines()
			f.close()

def find_command(proc_name):
	global COMMANDS_PROTO
	for command in COMMANDS_PROTO:
		if command.find('proto').find('name').text == proc_name:
			return command
	return None	

def get_proto(proc_name):
	tdecl = 'typedef '
	command = find_command(proc_name)
	proto = command.find('proto')
	tdecl += noneStr(proto.text)
	for elem in proto:
		text = noneStr(elem.text)
		tail = noneStr(elem.tail)
		if (elem.tag == 'name'):
			tdecl += '(' + ' APIENTRYP ' + 'PFN' + text.upper() + 'PROC' + tail + ')'
		else:
			tdecl += text + tail

	params = command.findall('param')
	n = len(params)
	paramdecl = ' ('
	if n > 0:
		for i in range(0,n):
			paramdecl += ''.join([t for t in params[i].itertext()])
			if (i < n - 1):
				paramdecl += ', '
	else:
		paramdecl += 'void'
	paramdecl += ");";
	return tdecl + paramdecl

# Parce gl.xml
def parce_specifications():
	global COMMANDS
	global COMMANDS_PROTO
	global EXT_COMMANDS
	tree = etree.parse('spec/gl.xml')
	root = tree.getroot()

	all_commands = root.findall('commands')
	COMMANDS_PROTO = all_commands[0].findall('command')

	#print(find_command('glCheckFramebufferStatus').find('proto').find('name').text)
	#print(get_proto('glGetShaderiv'))
# Parce features
	requirements = []
	features = root.findall('feature')
	print('Features:')
	for feature in features:
		if feature.attrib['name'] in FEATURES:
			print('\t' + feature.attrib['name'])
			for require in feature.findall('require'):
				if require.attrib.get('profile') != 'compatibility':
					requirements.append(require)

# Build commands list

	for require in requirements:
		for command in require.findall('command'):
			COMMANDS.append(command.attrib['name'])

	remove_commands = []

# remove commands with remove features
	for feature in features:
		if feature.attrib['name'] in FEATURES:
			for require in feature.findall('require'):
				for remove in feature.findall('remove'):
					for command in remove.findall('command'):
						remove_commands.append(command.attrib['name'])

	COMMANDS = [command for command in COMMANDS if command not in remove_commands]

# Parce extensions
	print('Extensions:')
	extensions = root.find('extensions').findall('extension')
	for extension in extensions:
		if extension.attrib['name'] in EXTENTIONS:
			print('\t' + extension.attrib['name'])
			for require in extension.findall('require'):
				for command in require.findall('command'):
					EXT_COMMANDS.append(command.attrib['name'])
					#print(command.attrib['name'])
					
# Generate glcore.h
def generate_gl_header():
	global COMMANDS
	global GEN_HEADER
	print('Generating %s in include/GL...' % GEN_HEADER)
	with open('include/GL/%s' % GEN_HEADER, 'wb') as f:
		f.write(bytes('''/* Generated by glcoregen v2 */
#pragma once

#include <GL/glcorearb.h>

#ifndef __gl_h_
#define __gl_h_
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* GLcore API */
int glLoadFunctions(void);
int glLoadExtensions(void);
void *nativeGetProcAddress(const char *proc);

/* OpenGL functions */
''', 'utf8'))	
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('extern %s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('#define %s %s\n' % (proc['name'], proc['variable']), 'utf8'))
		f.write(bytes('''
/* Extensions functions prototypes */
''', 'utf8'))
		for command in EXT_COMMANDS:
			proc = proc_t(command)
			f.write(bytes('%s\n' % get_proto(proc['name']), 'utf8'))
		f.write(bytes('''
/* Extensions functions */
''', 'utf8'))
		for command in EXT_COMMANDS:
			proc = proc_t(command)
			f.write(bytes('extern %s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		for command in EXT_COMMANDS:
			proc = proc_t(command)
			f.write(bytes('#define %s %s\n' % (proc['name'], proc['variable']), 'utf8'))
		f.write(bytes('''
#ifdef __cplusplus
}
#endif

''', 'utf8'))
		f.close()

# Generate glcore.h
def generate_es_header():
	global COMMANDS
	global GEN_HEADER
	print('Generating %s in include/GL...' % GEN_HEADER)
	with open('include/GL/%s' % GEN_HEADER, 'wb') as f:
		f.write(bytes('''/* Generated by glcoregen v2 */
#pragma once

#include <GLES2/gl2.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Core GL API */
int glLoadFunctions(void);
void *nativeGetProcAddress(const char *proc);
''', 'utf8'))
		f.write(bytes('''
/* OpenGL function prototypes */
#define APIENTRYP *

''', 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('%s\n' % get_proto(proc['name']), 'utf8'))
		f.write(bytes('''
/* OpenGL functions*/
''', 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('extern %s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('#define %s %s\n' % (proc['name'], proc['variable']), 'utf8'))

		f.write(bytes('''
#ifdef __cplusplus
}
#endif

''', 'utf8'))
		f.close()

# Generate glcore.c
def generate_gl_source():
	global GEN_SOURCE
	global CORE_PROFILE
	print('Generating source %s in src/GL... of %s loader' % (GEN_SOURCE, CORE_PROFILE))
	with open('src/%s' % GEN_SOURCE, 'wb') as f:
		f.write(bytes('''/* Generated by glcoregen v2 */
#include <GL/%s>

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
static void load_exts(void);

int glLoadFunctions(void)
{
	open_libgl();
	load_procs();
	close_libgl();
	return 1;
}

int glLoadExtensions(void)
{
	open_libgl();
	load_exts();
	close_libgl();
	return 1;
}

void *nativeGetProcAddress(const char *proc)
{
	return get_proc(proc);
}

''' % GEN_HEADER, 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('%s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		f.write(bytes('''
static void load_procs(void)
{
''', 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('\t%s = (%s) get_proc(\"%s\");\n' % (proc['variable'], proc['prototype'], proc['name']), "utf8"))
		f.write(bytes('}\n', 'utf8'))

		for command in EXT_COMMANDS:
			proc = proc_t(command)
			f.write(bytes('%s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		f.write(bytes('''
static void load_exts(void)
{
''', 'utf8'))
		for command in EXT_COMMANDS:
			proc = proc_t(command)
			f.write(bytes('\t%s = (%s) get_proc(\"%s\");\n' % (proc['variable'], proc['prototype'], proc['name']), "utf8"))
		f.write(bytes('}\n', 'utf8'))
		f.close()

def generate_es_source():
	global GEN_SOURCE
	global CORE_PROFILE
	print('Generating source %s in src/GL... of %s loader' % (GEN_SOURCE, CORE_PROFILE))
	with open('src/%s' % GEN_SOURCE, 'wb') as f:
		f.write(bytes('''/* Generated by glcoregen v2 */
#include <GL/%s>
#include <EGL/egl.h>

static void open_libgl(void)
{
}

static void close_libgl(void)
{
}

static __eglMustCastToProperFunctionPointerType get_proc(const char *proc)
{
	return eglGetProcAddress(proc);
}

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

''' % GEN_HEADER, 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('%s %s;\n' % (proc['prototype'], proc['variable']), "utf8"))
		f.write(bytes('''
static void load_procs(void)
{
''', 'utf8'))
		for command in COMMANDS:
			proc = proc_t(command)
			f.write(bytes('\t%s = (%s) get_proc(\"%s\");\n' % (proc['variable'], proc['prototype'], proc['name']), "utf8"))
		f.write(bytes('}\n', 'utf8'))
		f.close()

def main():
	global CORE_FILE
	global CORE_PROFILE
	global GEN_HEADER
	global GEN_SOURCE
	global EXT_FILE
	args = get_parser().parse_args()
	print('Get features and extentions from:\n \t' + args.core_file + ' \n\t' + noneStr(args.ext_file))
	print('With core profile ' + args.profile)
	CORE_FILE = args.core_file
	EXT_FILE = args.ext_file
	CORE_PROFILE = args.profile
	GEN_HEADER = args.header
	GEN_SOURCE = args.source

	generate_header = None
	generate_source = None
	if CORE_PROFILE == 'GL':
		generate_header = generate_gl_header 
		generate_source = generate_gl_source
	else:
		generate_source = generate_es_source
		generate_header = generate_es_header 
	
	create_directories()
	download_headers()
	download_specifications()
	read_configs()
	parce_specifications()
	generate_header()
	generate_source()

if __name__ == '__main__':
	main()
