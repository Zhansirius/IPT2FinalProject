import arcade
from music_manager import MusicManager

class GameOverView(arcade.View):

    def __init__(self, score, highscore, level):

        super().__init__()
        self.need_ui_update = False
        # UI camera for fullscreen/resizing
        self.ui_camera = arcade.Camera2D()

        self.final_score = score
        self.highscore = highscore
        self.level = level

        arcade.set_background_color(
            arcade.color.BLACK
        )

        self.game_over_text = arcade.Text(
            "GAME OVER",
            0,
            0,
            arcade.color.RED,
            font_size=50,
            anchor_x="center"
        )

        self.score_text = arcade.Text(
            "",
            0,
            0,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center"
        )

        self.highscore_text = arcade.Text(
            "",
            0,
            0,
            arcade.color.YELLOW,
            font_size=24,
            anchor_x="center"
        )

        self.restart_text = arcade.Text(
            "Press ENTER to Restart",
            0,
            0,
            arcade.color.GREEN,
            font_size=20,
            anchor_x="center"
        )

        self.menu_text = arcade.Text(
            "Press ESC for Menu",
            0,
            0,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center"
        )

        self.update_text_positions()

    def on_draw(self):

        self.clear()

        self.ui_camera.use()

        self.game_over_text.draw()
        self.score_text.draw()
        self.highscore_text.draw()
        self.restart_text.draw()
        self.menu_text.draw()

    def on_key_press(self, key, modifiers):

        # Fullscreen toggle
        if key == arcade.key.F4:
            self.window.set_fullscreen(
                not self.window.fullscreen
            )

            self.ui_camera.match_window()

            self.update_text_positions()

        # Restart game
        if key == arcade.key.ENTER:

            from GameView import GameView

            game_view = GameView()
            game_view.level = self.level
            game_view.setup()

            self.window.show_view(game_view)

        # Return to menu
        elif key == arcade.key.ESCAPE:

            from MenuView import MenuView

            menu_view = MenuView()

            self.window.show_view(menu_view)

    def update_text_positions(self):

        center_x = self.window.width / 2
        center_y = self.window.height / 2

        self.game_over_text.x = center_x
        self.game_over_text.y = center_y + 150

        self.score_text.text = f"Final Score: {self.final_score}"
        self.score_text.x = center_x
        self.score_text.y = center_y + 50

        self.highscore_text.text = f"High Score: {self.highscore}"
        self.highscore_text.x = center_x
        self.highscore_text.y = center_y

        self.restart_text.x = center_x
        self.restart_text.y = center_y - 100

        self.menu_text.x = center_x
        self.menu_text.y = center_y - 150

    def on_resize(self, width, height):

        super().on_resize(width, height)

        # Update camera for new window size
        self.ui_camera.match_window()

        # Recalculate all text positions
        self.update_text_positions()

    def on_update(self, delta_time):

        if self.need_ui_update:
            self.update_text_positions()

            self.need_ui_update = False

    def on_show_view(self):
        from music_manager import MusicManager
        MusicManager.stop_music()
        arcade.set_background_color(arcade.color.BLACK)

        from music_manager import MusicManager

        MusicManager.play_music("assets/sounds/death.mp3", loop=True)