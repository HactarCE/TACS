from .base import Scene
from .game import Game
from text_engine import ALIGN_CENTER
import colors
import drawables
import layers
import styles

__all__ = ['MainMenu']

TITLE_WRAPPED = ["Totally Accurate", "Curling Simulator"]


class MainMenu(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # bg = drawables.SolidColor(colors.ICE, self.disp.rect.size)
        bg = drawables.Image('img/ice.png')
        self.add(bg, layers.BG)

        title = drawables.Text(TITLE_WRAPPED, **styles.TITLE)
        self.add(title, layers.UI_FG)

        buttons = []
        for label, action in (('Play', self.buttonpush_play),
                              ('About', self.buttonpush_about),
                              ('Quit', self.buttonpush_quit)):
            style = styles.MAIN_MENU_QUIT_BUTTON if label == 'Quit' else styles.MAIN_MENU_BUTTON
            b = drawables.TextButton(label, action, **style)
            buttons.append(b)
            self.add(b, layers.UI_FG)

        self.temp = buttons[1]

        # this is probably way more complicated than it needs to be
        mid_x = self.disp.rect.width // 2
        title_height = title.rect.height
        button_height = buttons[0].rect.height
        button_count = len(buttons)
        button_spacing = 20
        title_spacing = 150
        all_buttons_height = (button_height + button_spacing) * button_count - button_spacing
        title_y = (self.disp.rect.height - title_height - title_spacing - all_buttons_height) // 2
        button_y = title_y + title_height + title_spacing

        title.move_center_to((mid_x, title_y + title_height // 2))
        for i in range(len(buttons)):
            buttons[i].move_center_to(
                (mid_x, button_y + (button_height + button_spacing) * i + button_height // 2))

    def buttonpush_play(self):
        self.enter('Game')

    def buttonpush_about(self):
        self.enter('about')

    def buttonpush_quit(self):
        self.leave()
