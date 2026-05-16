from MenuView import MenuView
from constants import *
import arcade
from GameView import GameView
from Player import PlayerCharacter

def load_texture_pair(filename):
    """ Загружает пару текстур: обычную и отзеркаленную. Работает в Arcade 3.x """
    texture = arcade.load_texture(filename)
    return [
        texture,
        texture.flip_left_right() # Создает зеркальную копию
    ]

def main():
    """Main function"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    menu_view = MenuView()
    window.show_view(menu_view)

    arcade.run()


if __name__ == "__main__":
    main()