import arcade
import math

class BossEnemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.attack_hitbox = None
        self.frame_width = 288
        self.frame_height = 160

        self.dead_finished = False

        # Позиционирование
        self.center_x = x
        self.center_y = y

        # Характеристики босса
        self.max_hp = 5
        self.hp = self.max_hp
        self.speed = 5.0
        self.attack_range = 200  # Радиус атаки босса

        # Состояния босса
        self.state = "IDLE"
        self.character_face_direction = 0  # 0 - вправо, 1 - влево
        self.cur_texture = 0
        self.time_elapsed = 0.0
        self.time_per_frame = 0.1

        self.is_invincible = False
        self.invincible_timer = 0.0
        self.invincible_duration = 3.0

        self.scale = 2.4  # Масштаб босса

        self.idle_textures = self._load_individual_pairs("assets/boss/individual sprites/01_demon_idle/demon_idle", 6)
        self.walk_textures = self._load_individual_pairs("assets/boss/individual sprites/02_demon_walk/demon_walk", 12)
        self.attack_textures = self._load_individual_pairs("assets/boss/individual sprites/03_demon_cleave/demon_cleave", 15)
        self.hurt_textures = self._load_individual_pairs("assets/boss/individual sprites/04_demon_take_hit/demon_take_hit", 5)
        self.death_textures = self._load_individual_pairs("assets/boss/individual sprites/05_demon_death/demon_death", 22)

        self.texture = self.idle_textures[0][0]

    def _load_individual_pairs(self, base_path, frame_count):
        textures = []

        for i in range(1, frame_count + 1):
            filename = f"{base_path}_{i}.png"

            texture = arcade.load_texture(filename)

            textures.append([
                texture.flip_left_right(),
                texture
            ])

        return textures

    def update_boss_ai(self, player):

        # НЕ прерываем смерть/урон
        if self.state in ["HURT", "DEAD"]:
            self.change_x = 0
            return

        # ВАЖНО:
        # Во время атаки не меняем сторону
        if self.state == "ATTACK":
            self.change_x = 0
            return

        distance_x = player.center_x - self.center_x
        distance_y = abs(player.bottom - self.bottom)

        # Поворот только если НЕ атакуем
        if distance_x > 0:
            self.character_face_direction = 0
        else:
            self.character_face_direction = 1

        # Если игрок слишком высоко — стоим
        if distance_y > 180:
            self.change_x = 0
            self.state = "IDLE"
            return

        # Движение к игроку
        if abs(distance_x) > self.attack_range:

            self.state = "WALK"

            if distance_x > 0:
                self.change_x = self.speed
            else:
                self.change_x = -self.speed

        else:
            self.change_x = 0

            # НЕ запускаем атаку заново если уже атакуем
            if self.state != "ATTACK":
                self.state = "ATTACK"
                self.cur_texture = 0

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_elapsed += delta_time

        if self.state == "DEAD":
            current_textures = self.death_textures
        elif self.state == "HURT":
            current_textures = self.hurt_textures
        elif self.state == "ATTACK":
            current_textures = self.attack_textures
        elif self.state == "WALK":
            current_textures = self.walk_textures
        else:
            current_textures = self.idle_textures

        if not current_textures:
            return

        if self.time_elapsed >= self.time_per_frame:
            self.time_elapsed = 0.0
            self.cur_texture += 1

            if self.state == "DEAD":
                if self.cur_texture >= len(current_textures):
                    self.dead_finished = True

                    self.cur_texture = len(current_textures) - 1
            elif self.state == "HURT":

                if self.cur_texture >= len(current_textures):
                    self.state = "IDLE"
                    self.cur_texture = 0
            elif self.state == "ATTACK":
                if self.cur_texture >= len(current_textures):
                    self.state = "IDLE"
                    self.cur_texture = 0
            else:
                if self.cur_texture >= len(current_textures):
                    self.cur_texture = 0

        if self.cur_texture < len(current_textures):
            self.texture = current_textures[self.cur_texture][self.character_face_direction]

        if self.is_invincible and self.state != "DEAD":
            self.invincible_timer += delta_time
            if self.invincible_timer >= self.invincible_duration:
                self.is_invincible = False
                self.invincible_timer = 0.0

        # Эффект прозрачности во время бессмертия
        if self.is_invincible and self.state != "DEAD":
            self.alpha = 140
        else:
            self.alpha = 255

    def get_attack_hitbox(self):

        if self.state != "ATTACK":
            return None

        # Только активные кадры удара
        if not (10 <= self.cur_texture <= 12):
            return None

        hitbox = arcade.SpriteSolidColor(
            190,
            180,
            color=arcade.color.RED
        )

        hitbox.center_y = self.center_y - 85

        if self.character_face_direction == 0:
            hitbox.left = self.right
        else:
            hitbox.right = self.left

        return hitbox