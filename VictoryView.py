import arcade
from music_manager import MusicManager

class VictoryView(arcade.View):

    def __init__(self, score, highscore):
        super().__init__()

        self.score = score
        self.highscore = highscore

        self.background_color = arcade.color.BLACK

        self.ui_camera = arcade.Camera2D()

        self.need_ui_update = False

        self.update_ui_positions()

    def update_ui_positions(self):

        self.ui_center_x = self.window.width / 2
        self.ui_center_y = self.window.height / 2

    def on_show_view(self):

        arcade.set_background_color(self.background_color)

    def on_draw(self):

        self.clear()

        self.ui_camera.use()

        if self.need_ui_update:
            self.update_ui_positions()
            self.need_ui_update = False

        arcade.draw_text(
            "YOU WIN",
            self.ui_center_x,
            self.ui_center_y + 100,
            arcade.color.GOLD,
            48,
            anchor_x="center"
        )

        arcade.draw_text(
            f"Score: {self.score}",
            self.ui_center_x,
            self.ui_center_y,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )

        arcade.draw_text(
            f"High Score: {self.highscore}",
            self.ui_center_x,
            self.ui_center_y - 50,
            arcade.color.LIGHT_GRAY,
            20,
            anchor_x="center"
        )

        arcade.draw_text(
            "Press ENTER to return menu",
            self.ui_center_x,
            self.ui_center_y - 150,
            arcade.color.GRAY,
            18,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):

        # FULLSCREEN
        if key == arcade.key.F4:

            self.window.set_fullscreen(
                not self.window.fullscreen
            )

            self.ui_camera.match_window()

        if key == arcade.key.ENTER:
            from MenuView import MenuView

            menu_view = MenuView()

            self.window.show_view(menu_view)

    def on_resize(self, width, height):

        super().on_resize(width, height)

        self.ui_camera.match_window()

        self.need_ui_update = True

    def on_show_view(self):
        from music_manager import MusicManager
        arcade.set_background_color(self.background_color)
        # Включаем тему победы
        MusicManager.play_music("assets/sounds/end.mp3", loop=True)
