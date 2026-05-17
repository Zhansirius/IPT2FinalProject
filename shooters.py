import arcade
import math


class Bullet(arcade.Sprite):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__("assets/images/bullet.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.change_x = speed_x
        self.change_y = speed_y

        angle_radians = math.atan2(speed_y, speed_x)
        self.angle = math.degrees(-1 * angle_radians)


class Turret:
    def __init__(self, x, y, speed_x, speed_y, interval):
        self.center_x = x
        self.center_y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.interval = interval  # Как часто стреляет (в секундах)

        self.timer = interval