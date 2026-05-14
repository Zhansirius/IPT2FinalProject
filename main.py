from constants import *
import arcade
from GameView import GameView
from Player import PlayerCharacter

def load_texture_pair(filename):
    """
    Загружает пару текстур: обычную и отзеркаленную.
    Работает в Arcade 3.x
    """
    texture = arcade.load_texture(filename)
    return [
        texture,
        texture.flip_left_right() # Создает зеркальную копию
    ]

def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()