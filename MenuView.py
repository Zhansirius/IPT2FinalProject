import arcade
from GameView import GameView
from constants import *

class MenuView(arcade.View):

    def __init__(self):
        super().__init__()

        self.background_color = arcade.csscolor.DARK_BLUE

        # Button settings
        self.button_width = 300
        self.button_height = 80

        # Button colors
        self.button_color = arcade.color.DARK_GREEN
        self.button_hover_color = arcade.color.GREEN

        # Hover state
        self.is_hovered = False

    def on_show_view(self):
        arcade.set_background_color(self.background_color)

    def on_draw(self):

        self.clear()

        # Dynamic button position (works with fullscreen)
        button_x = self.window.width / 2
        button_y = self.window.height / 2

        # Dynamic title position
        title_x = self.window.width / 2
        title_y = self.window.height / 2 + 180

        # Hover color logic
        current_color = (
            self.button_hover_color
            if self.is_hovered
            else self.button_color
        )

        # Draw title
        self.title_text = arcade.Text(
            "PLATFORMER GAME",
            title_x,
            title_y,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center"
        )

        self.title_text.draw()

        # Draw button
        arcade.draw_rect_filled(
            arcade.LBWH(
                button_x - self.button_width / 2,
                button_y - self.button_height / 2,
                self.button_width,
                self.button_height
            ),
            current_color
        )

        # Button border
        arcade.draw_rect_outline(
            arcade.LBWH(
                button_x - self.button_width / 2,
                button_y - self.button_height / 2,
                self.button_width,
                self.button_height
            ),
            arcade.color.WHITE,
            border_width=4
        )

        # Button text
        self.start_text = arcade.Text(
            "START GAME",
            button_x,
            button_y,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="center"
        )

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

    def on_mouse_motion(self, x, y, dx, dy):

        button_x = self.window.width / 2
        button_y = self.window.height / 2

        self.is_hovered = (
                button_x - self.button_width / 2 <= x <= button_x + self.button_width / 2
                and
                button_y - self.button_height / 2 <= y <= button_y + self.button_height / 2
        )

    def on_mouse_press(self, x, y, button, modifiers):

        button_x = self.window.width / 2
        button_y = self.window.height / 2

        if (
                button_x - self.button_width / 2 <= x <= button_x + self.button_width / 2
                and
                button_y - self.button_height / 2 <= y <= button_y + self.button_height / 2
        ):
            game_view = GameView()
            game_view.setup()

            self.window.show_view(game_view)