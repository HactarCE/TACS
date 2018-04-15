import pygame
import colors

ALIGN_LEFT   = lambda text_w, surf_w: 0
ALIGN_CENTER = lambda text_w, surf_w: (surf_w - text_w) / 2
ALIGN_RIGHT  = lambda text_w, surf_w: surf_w - text_w

pygame.font.init()

fonts = {
    'title': pygame.font.Font('font/DAGGERSQUARE.otf', 96),
    'big_button': pygame.font.Font('font/DAGGERSQUARE.otf', 48)
}

def get_font(font):
    if isinstance(font, pygame.font.Font):
        return font
    elif font in fonts:
        return fonts[font]
    else:
        raise Exception(f'font "{font}" not found')

def render_text(text, font, fg=colors.BLACK, bg=None, align=ALIGN_LEFT, antialias=True, **kwargs):
    f = get_font(font)
    if isinstance(text, str):
        text = [text]
    line_surfs = [f.render(line, antialias, fg, bg) for line in text]
    height = sum(s.get_height() for s in line_surfs)
    width = max(s.get_width() for s in line_surfs)
    surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    if bg:
        surf.fill(bg)
    total_w = surf.get_width()
    h = 0
    for line_surf in line_surfs:
        surf.blit(line_surf, (align(line_surf.get_width(), total_w), h))
        h += line_surf.get_height()
    return surf

def wrap_text(text, font, max_width, **kwargs):
    f = get_font(font)
    remaining = text
    words = re.findall(r'(\W*)(\w+)')
    lines = ['']
    while remaining:
        if font.size(lines[-1] + words[0].group(0)) > max_width:
            lines.append(words.pop(0).group(1))
        else:
            lines[-1].append(words.pop(0).group(0))
    return '\n'.join(lines)

def render_wrapped_text(text, font, max_width, *args, **kwargs):
    return render_text(font, wrap_text(text, font, max_width), *args, **kwargs)
