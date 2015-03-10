#pragma once

enum
{
    KEY_BACKSPACE       = 0x08,
    KEY_ENTER           = 0x0d,
    KEY_LSHIFT          = VK_LSHIFT,
    KEY_RSHIFT          = VK_RSHIFT,
    KEY_LCTRL		= VK_LCONTROL,
    KEY_RCTRL		= VK_RCONTROL,
    KEY_LALT		= VK_LMENU,
    KEY_RALT		= VK_RMENU,
    KEY_PAUSE           = 0x13,
    KEY_ESCAPE          = 0x1b,
    KEY_SPACE           = 0x20,
    KEY_LEFT            = 0x25,
    KEY_UP, KEY_RIGHT, KEY_DOWN,

    KEY_TAB             = 0x09,

    KEY_0               = 0x30,
    KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7,
    KEY_8, KEY_9,

    KEY_A               = 0x41,
    KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H,
    KEY_I, KEY_J, KEY_K, KEY_L, KEY_M, KEY_N, KEY_O,
    KEY_P, KEY_Q, KEY_R, KEY_S, KEY_T, KEY_U, KEY_V,
    KEY_W, KEY_X, KEY_Y, KEY_Z,

    KEY_NUMPAD0         = 0x60,
    KEY_NUMPAD1, KEY_NUMPAD2, KEY_NUMPAD3, KEY_NUMPAD4,
    KEY_NUMPAD5, KEY_NUMPAD6, KEY_NUMPAD7, KEY_NUMPAD8,
    KEY_NUMPAD9,

    KEY_NUMPAD_PLUS     = 0x6b,
    KEY_NUMPAD_MINUS    = 0x6d,

    KEY_F1              = 0x70,
    KEY_F2, KEY_F3, KEY_F4,  KEY_F5,  KEY_F6, KEY_F7,
    KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12,
    MAX_KEY
};

enum
{
    MBUTTON0 = 0x01,
    MBUTTON1 = 0x02,
    MBUTTON2 = 0x04,
    MBUTTON3 = 0x08,
    MBUTTON4 = 0x10
};

enum KEYMOD
{
    KEYMOD_CTRL    = 0x0001,
    KEYMOD_SHIFT   = 0x0002,
    KEYMOD_ALT     = 0x0003,
    MAX_KEYMOD
};

enum KEYMOD_MASK
{
    MODMASK_CTRL = 1 << KEYMOD_CTRL,
    MODMASK_SHIFT = 1 << KEYMOD_SHIFT,
    MODMASK_ALT = 1 << KEYMOD_ALT
};
