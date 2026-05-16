import arcade
from GameView import GameView
from constants import *

class MenuView(arcade.View):

    def __init__(self):
        super().__init__()

        self.background_color = arcade.csscolor.DARK_BLUE

    def on_show_view(self):
        arcade.set_background_color(self.background_color)

    def on_draw(self):
        self.clear()

        # Draw game title
        self.title_text = arcade.Text(
            "PLATFORMER GAME",
            self.window.width / 2,
            self.window.height / 2 + 100,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center"
        )

        # Draw start instruction
        self.start_text = arcade.Text(
            "Press ENTER to Start",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.YELLOW,
            font_size=24,
            anchor_x="center"
        )

        self.title_text.draw()
        self.start_text.draw()

    def on_key_press(self, key, modifiers):

        # Fullscreen toggle
        if key == arcade.key.F4:
            self.window.set_fullscreen(
                not self.window.fullscreen
            )

        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()

            self.window.show_view(game_view)