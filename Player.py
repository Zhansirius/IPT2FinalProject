from constants import *
import arcade
class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.character_face_direction = 0  # 0 - вправо, 1 - влево
        self.cur_texture = 0
        self.time_elapsed = 0.0
        self.is_attacking = False
        self.hit_1_done = False
        self.hit_2_done = False

        # Сохраняем текущее состояние, чтобы сбрасывать кадры при смене анимации
        self.current_state = "IDLE"

        self.idle_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Idle.png", 200, 200, 8, 8
        )
        self.jump_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Jump.png", 200, 200, 2, 2
        )

        self.walk_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Run.png", 200, 200, 8, 8
        )

        self.attack_textures = []
        self.attack_textures.extend(self._load_sheet_pairs("assets/pr_sprites/Attack1.png", 200, 200, 6, 6))
        self.attack_textures.extend(self._load_sheet_pairs("assets/pr_sprites/Attack2.png", 200, 200, 6, 6))

        self.texture = self.idle_textures[0][0]

    def _load_sheet_pairs(self, filename, width, height, cols, count):
        try:
            sheet = arcade.SpriteSheet(filename)
            textures = sheet.get_texture_grid(
                size=(width, height),
                columns=cols,
                count=count
            )
            return [[tex, tex.flip_left_right()] for tex in textures]
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
            return [[arcade.make_soft_square_texture(width, (255, 0, 255)),
                     arcade.make_soft_square_texture(width, (255, 0, 255))]]

    def update_animation(self, is_on_ground, delta_time: float = 1 / 60):
        if not self.is_attacking:
            if self.change_x < 0 and self.character_face_direction == 0:
                self.character_face_direction = 1
            elif self.change_x > 0 and self.character_face_direction == 1:
                self.character_face_direction = 0

        self.time_elapsed += delta_time
        if self.is_attacking:
            time_per_frame = 0.04
        else:
            time_per_frame = 0.08

        new_state = "IDLE"
        if self.is_attacking:
            new_state = "ATTACK"
        elif not is_on_ground:
            new_state = "JUMP"
        elif self.change_x != 0:
            new_state = "WALK"

        if new_state != self.current_state:
            self.cur_texture = 0
            self.time_elapsed = 0
            self.current_state = new_state

        if self.time_elapsed >= time_per_frame:
            self.time_elapsed = 0
            self.cur_texture += 1

        if self.current_state == "ATTACK":
            if self.cur_texture >= len(self.attack_textures):
                self.is_attacking = False
                self.cur_texture = 0
                self.current_state = "IDLE"
            else:
                self.texture = self.attack_textures[self.cur_texture][self.character_face_direction]

        elif self.current_state == "JUMP":
            if self.cur_texture >= len(self.jump_textures):
                self.cur_texture = len(self.jump_textures) - 1
            self.texture = self.jump_textures[self.cur_texture][self.character_face_direction]

        elif self.current_state == "WALK":
            if self.cur_texture >= len(self.walk_textures):
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

        else:
            if self.cur_texture >= len(self.idle_textures):
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture][self.character_face_direction]