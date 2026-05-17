import arcade
from GameView import GameView
from constants import *

class MenuView(arcade.View):

    def __init__(self):
        super().__init__()
        self.need_ui_update = False

        # Main menu music
        self.menu_music = arcade.load_sound(
            "assets/MainMenuMusic/Menumusic.mp3"
        )

        self.music_player = None

        self.background_color = arcade.csscolor.DARK_BLUE
        # Animated background frames
        self.background_frames = []

        for i in range(1, 8):
            texture = arcade.load_texture(
                f"assets/MainMenuBackground/{i}cadr.png"
            )

            self.background_frames.append(texture)

        # Animation state
        self.current_frame = 0
        self.animation_timer = 0

        # Button settings
        self.button_width = 300
        self.button_height = 80

        # Button colors
        self.button_color = arcade.color.DARK_GREEN
        self.button_hover_color = arcade.color.GREEN

        # Hover state
        self.is_hovered = False

        self.update_ui_positions()

    def on_show_view(self):

        arcade.set_background_color(
            self.background_color
        )

        if self.music_player is None:
            self.music_player = self.menu_music.play(
                volume=0.5,
                loop=True
            )

    def on_update(self, delta_time):

        # Animation timer
        self.animation_timer += delta_time

        # Change frame every 0.12 seconds
        if self.animation_timer >= 0.12:

            self.current_frame += 1

            # Loop animation
            if self.current_frame >= len(self.background_frames):
                self.current_frame = 0

            self.animation_timer = 0

    def on_draw(self):
        if self.need_ui_update:
            self.update_ui_positions()
            self.need_ui_update = False

        self.clear()

        # Use default window coordinates
        self.window.default_camera.use()

        current_texture = self.background_frames[
            self.current_frame
        ]

        arcade.draw_texture_rect(
            current_texture,
            arcade.LRBT(
                0,
                self.window.width,
                0,
                self.window.height
            )
        )

        # Dynamic button position (works with fullscreen)
        button_x = self.button_x
        button_y = self.button_y

        # Dynamic title position
        title_x = self.title_x
        title_y = self.title_y

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

            was_playing = self.music_player is not None

            if self.music_player:
                self.music_player.pause()
                self.music_player = None

            self.window.set_fullscreen(
                not self.window.fullscreen
            )

            if was_playing:
                self.music_player = self.menu_music.play(
                    volume=0.5,
                    loop=True
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

            if self.music_player:
                self.music_player.pause()

            game_view = GameView()
            game_view.setup()

            self.window.show_view(game_view)

    def on_resize(self, width, height):

        super().on_resize(width, height)

        self.need_ui_update = True

    def update_ui_positions(self):

        self.button_x = self.window.width / 2
        self.button_y = self.window.height / 2

        self.title_x = self.window.width / 2
        self.title_y = self.window.height / 2 + 180

    def on_hide_view(self):

        if self.music_player:
            self.music_player.pause()