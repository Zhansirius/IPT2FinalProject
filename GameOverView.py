import arcade

class GameOverView(arcade.View):

    def __init__(self, final_score, highscore):

        super().__init__()

        self.final_score = final_score
        self.highscore = highscore

        arcade.set_background_color(
            arcade.color.BLACK
        )

    def on_draw(self):

        self.clear()

        center_x = self.window.width / 2
        center_y = self.window.height / 2

        # GAME OVER title
        game_over_text = arcade.Text(
            "GAME OVER",
            center_x,
            center_y + 150,
            arcade.color.RED,
            font_size=50,
            anchor_x="center"
        )

        game_over_text.draw()

        # Final score
        score_text = arcade.Text(
            f"Final Score: {self.final_score}",
            center_x,
            center_y + 50,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center"
        )

        score_text.draw()

        # Highscore
        highscore_text = arcade.Text(
            f"High Score: {self.highscore}",
            center_x,
            center_y,
            arcade.color.YELLOW,
            font_size=24,
            anchor_x="center"
        )

        highscore_text.draw()

        # Restart info
        restart_text = arcade.Text(
            "Press ENTER to Restart",
            center_x,
            center_y - 100,
            arcade.color.GREEN,
            font_size=20,
            anchor_x="center"
        )

        restart_text.draw()

        # Menu info
        menu_text = arcade.Text(
            "Press ESC for Menu",
            center_x,
            center_y - 150,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center"
        )

        menu_text.draw()

    def on_key_press(self, key, modifiers):

        # Restart game
        if key == arcade.key.ENTER:

            from GameView import GameView

            game_view = GameView()
            game_view.setup()

            self.window.show_view(game_view)

        # Return to menu
        elif key == arcade.key.ESCAPE:

            from MenuView import MenuView

            menu_view = MenuView()

            self.window.show_view(menu_view)