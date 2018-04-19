from text_engine import ALIGN_CENTER
import colors
from colors import hex

TITLE = {
    'font': 'title',
    'align': ALIGN_CENTER
}

MAIN_MENU_BUTTON = {
    'font': 'big_button',
    'bg': None,
    'fg_hover': hex(0x00007f),
    'fg_click': hex(0x0000df),
    'antialias': False
}

MAIN_MENU_QUIT_BUTTON = {
    **MAIN_MENU_BUTTON,
    'fg_hover': hex(0x7f0000),
    'fg_click': hex(0xdf0000)
}
