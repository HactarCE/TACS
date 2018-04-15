hex = lambda hex_int: tuple(hex_int >> (8 * i) & 0xff for i in range(3)[::-1])

#region Generic colors
RED             = hex(0xff0000)
GREEN           = hex(0x00ff00)
BLUE            = hex(0x0000ff)

MAGENTA         = hex(0xff00ff)
CYAN            = hex(0x00ffff)
YELLOW          = hex(0xffff00)

BLACK           = hex(0x000000)
DARK_GREY       = hex(0x3f3f3f)
GREY            = hex(0x7f7f7f)
LIGHT_GREY      = hex(0xbfbfbf)
WHITE           = hex(0xffffff)
#endregion

#region Game colors
ICE             = hex(0xc0e7e7)
#endregion
