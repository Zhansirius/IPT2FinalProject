import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 1.5
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


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



        # --- ЗАГРУЗКА СПРАЙТ-ЛИСТОВ ---
        # ВАЖНО: Я поставил везде 200x200. Если Idle в файле тоже в больших квадратах,
        # то 38x53 использовать нельзя — это разрежет картинку пополам.

        # 1. Покой (Idle)
        self.idle_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Idle.png", 200, 200, 8, 8
        )

        # 2. Прыжок (Jump) - теперь тоже как спрайт-лист!
        # Даже если там 1-2 кадра, используем нарезку, чтобы не видеть "всю простыню"
        self.jump_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Jump.png", 200, 200, 2, 2
        )

        # 3. Ходьба (Run)
        self.walk_textures = self._load_sheet_pairs(
            "assets/pr_sprites/Run.png", 200, 200, 8, 8
        )

        # 4. Атака (Attack)
        self.attack_textures = []
        self.attack_textures.extend(self._load_sheet_pairs("assets/pr_sprites/Attack1.png", 200, 200, 6, 6))
        self.attack_textures.extend(self._load_sheet_pairs("assets/pr_sprites/Attack2.png", 200, 200, 6, 6))

        # Устанавливаем начальную текстуру
        self.texture = self.idle_textures[0][0]

    def _load_sheet_pairs(self, filename, width, height, cols, count):
        """Универсальный метод загрузки для Arcade 3.x"""
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
            # Возврат пустой заглушки, чтобы игра не вылетала
            return [[arcade.make_soft_square_texture(width, (255, 0, 255)),
                     arcade.make_soft_square_texture(width, (255, 0, 255))]]

    def update_animation(self, is_on_ground, delta_time: float = 1 / 60):
        # 1. Направление взгляда (БЛОКИРУЕМ ПРИ АТАКЕ)
        if not self.is_attacking:
            if self.change_x < 0 and self.character_face_direction == 0:
                self.character_face_direction = 1
            elif self.change_x > 0 and self.character_face_direction == 1:
                self.character_face_direction = 0

        self.time_elapsed += delta_time

        # 2. ДИНАМИЧЕСКАЯ СКОРОСТЬ КАДРОВ
        if self.is_attacking:
            time_per_frame = 0.04  # Анимация атаки в 2 раза быстрее! (Можешь менять число)
        else:
            time_per_frame = 0.08  # Обычная скорость

        # Определяем состояние с учетом приземления
        new_state = "IDLE"
        if self.is_attacking:
            new_state = "ATTACK"
        elif not is_on_ground:
            new_state = "JUMP"
        elif self.change_x != 0:
            new_state = "WALK"

        # Сброс кадра при смене анимации
        if new_state != self.current_state:
            self.cur_texture = 0
            self.time_elapsed = 0
            self.current_state = new_state

        # Логика смены кадров
        if self.time_elapsed >= time_per_frame:
            self.time_elapsed = 0
            self.cur_texture += 1

        # Выбор текстуры
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

        else:  # IDLE
            if self.cur_texture >= len(self.idle_textures):
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture][self.character_face_direction]

class GameView(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        # Player's hp
        self.p_hp = 5
        # Invincible frames
        self.i_frame = 0
        # Are they looking at right?
        self.facing_right = True

        self.draw_attack_rect = None

        # Default sounds
        self.sound_attack = arcade.load_sound("assets/sounds/ShovelHitDefault.mp3")
        self.sound_hit = arcade.load_sound("assets/sounds/hurt grunt .wav")
        self.sound_hit1 = arcade.load_sound("assets/sounds/hurt grunt 2.wav")
        self.sound_hurt = arcade.load_sound("assets/sounds/isaac dies new 1.wav")

        self.bg_camera = arcade.Camera2D()

        # Calling a map
        self.tile_map = None

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level number to load
        self.level = 1

        # Variable to hold our texture for our player
        self.player_texture = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Replacing all of our SpriteLists with a Scene variable
        self.scene = None

        # A variable to store our camera object
        self.camera = None

        # A variable to store our gui camera object
        self.gui_camera = None

        # This variable will store our score as an integer.
        self.score = 0

        # Direction flags
        self.left_pressed = False
        self.right_pressed = False

        # Should we reset the score?
        self.reset_score = True

        # This variable will store the text for score that we will draw to the screen.
        self.score_text = None

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):

        """Настройка игры. Вызывайте для перезапуска."""
        layer_options = {
            "Tile Layer 1": {
                "use_spatial_hash": True
            }
        }

        self.tile_map = arcade.load_tilemap(
            f"assets/lvls/test_lvl{self.level}.tmx",
            scaling=TILE_SCALING,
            layer_options=layer_options
        )

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling

        self.player_sprite = PlayerCharacter() # Используем наш новый класс
        self.scene.add_sprite("Player", self.player_sprite)

        if "SpawnPoint" in self.tile_map.object_lists:
            for obj in self.tile_map.object_lists["SpawnPoint"]:
                if obj.name == "SpawnPoint":
                    self.player_sprite.center_x = obj.shape[0] * TILE_SCALING
                    self.player_sprite.center_y = obj.shape[1] * TILE_SCALING

        try:
            enemy_list = self.scene.get_sprite_list("Enemy")


            for enemy in enemy_list:
                enemy.is_smart = enemy.properties.get("smart", False)
                # Берем жизни из свойств (из твоего Tiled)
                enemy.health = int(enemy.properties.get("health", 1))
                enemy.change_x = float(enemy.properties.get("speed", 2))

            print(f"Врагов загружено: {len(enemy_list)}")
        except KeyError:
            # Если слоя "Enemy" нет в карте, Arcade выкинет KeyError
            print("Предупреждение: Слой 'Enemy' не найден в сцене!")
            self.scene.add_sprite_list("Enemy")

        # 6. Физика (стены берем из слоя Tile Layer 1)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Tile Layer 1"],
            gravity_constant=GRAVITY
        )

        # Камеры и интерфейс
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        if self.reset_score:
            self.score = 0
            self.p_hp = 5
        self.reset_score = True
        self.i_frame = 0

        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate our game camera before drawing game world objects
        self.camera.use()

        # Draw our Scene (draws walls, slimes, player properly)
        self.scene.draw()


        if self.draw_attack_rect:
            arcade.draw_sprite(self.draw_attack_rect)
            # Убираем его, чтобы он не "завис" навсегда
            self.draw_attack_rect = None

        self.gui_camera.use()

        # Draw our Score
        self.score_text.draw()

    def update_player_speed(self):
        self.player_sprite.change_x = 0

        if self.left_pressed:
            self.player_sprite.change_x -= PLAYER_MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.change_x += PLAYER_MOVEMENT_SPEED

        if self.player_sprite.change_x < 0:
            self.facing_right = False
        elif self.player_sprite.change_x > 0:
            self.facing_right = True

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Move the player using our physics engine
        self.physics_engine.update()

        self.bg_camera.position = (self.camera.position[0] * 0.2, self.camera.position[1] * 0.2)

        # Передаем статус "на земле" в анимацию
        is_on_ground = self.physics_engine.can_jump()
        self.player_sprite.update_animation(is_on_ground, delta_time)

        # --- ЛОГИКА НАНЕСЕНИЯ УРОНА (ДВОЙНОЙ УДАР) ---
        if self.player_sprite.is_attacking:
            # Определяем кадры для ударов (подбери индексы под свою анимацию)
            # Если Attack1 (6 кадров) и Attack2 (6 кадров)
            first_hit_frame = 3  # Первый взмах
            second_hit_frame = 9  # Второй взмах

            # Проверяем, наступил ли момент для какого-то из ударов
            current_frame = self.player_sprite.cur_texture
            should_hit = False

            if current_frame == first_hit_frame and not self.player_sprite.hit_1_done:
                self.player_sprite.hit_1_done = True
                should_hit = True
            elif current_frame == second_hit_frame and not self.player_sprite.hit_2_done:
                self.player_sprite.hit_2_done = True
                should_hit = True

            # Если пора бить — спавним хитбокс
            if should_hit:
                attack_hitbox = arcade.SpriteSolidColor(70, 50, color=arcade.color.RED)
                attack_hitbox.bottom = self.player_sprite.bottom

                if self.player_sprite.character_face_direction == 0:  # Вправо
                    attack_hitbox.left = self.player_sprite.right
                else:  # Влево
                    attack_hitbox.right = self.player_sprite.left

                self.draw_attack_rect = attack_hitbox

                # Проверка столкновений с врагами
                hit_enemies = arcade.check_for_collision_with_list(attack_hitbox, self.scene["Enemy"])
                for enemy in hit_enemies:
                    if hasattr(enemy, "health"):
                        enemy.health -= 1
                        arcade.play_sound(self.sound_hit1)
                        if enemy.health <= 0:
                            enemy.remove_from_sprite_lists()
                            self.score += 50
                            self.score_text.text = f"Score: {self.score}"

        # Center our camera on the player
        self.camera.position = self.player_sprite.position

        # --- ЛОГИКА ДВИЖЕНИЯ ВРАГОВ ---
        try:
            enemy_list = self.scene.get_sprite_list("Enemy")
            walls = self.scene["Tile Layer 1"]

            for enemy in enemy_list:

                # --- 1. ГРАВИТАЦИЯ (Оставляем, чтобы они корректно вставали на пол при спавне) ---
                enemy.change_y -= GRAVITY
                enemy.center_y += enemy.change_y

                # Проверка столкновения с полом
                hit_list_y = arcade.check_for_collision_with_list(enemy, walls)
                for wall in hit_list_y:
                    if enemy.change_y < 0:  # Враг падает на пол
                        enemy.bottom = wall.top
                        enemy.change_y = 0
                    elif enemy.change_y > 0:  # Враг ударяется головой
                        enemy.top = wall.bottom
                        enemy.change_y = 0

                # Если скорость по оси X равна 0, пропускаем логику ходьбы
                if enemy.change_x == 0:
                    continue

                # --- 2. ПРОВЕРКА ПРОПАСТИ ДЛЯ ВСЕХ ВРАГОВ ---
                # Теперь мы не проверяем is_smart. Каждый слизень смотрит себе под ноги.
                look_ahead = 15 if enemy.change_x > 0 else -15
                check_point = (enemy.center_x + look_ahead, enemy.bottom - 5)

                ground_ahead = arcade.get_sprites_at_point(check_point, walls)

                if not ground_ahead:
                    # Земли впереди нет! Разворачиваемся
                    enemy.change_x *= -1

                # --- 3. ДВИЖЕНИЕ ПО X ---
                enemy.center_x += enemy.change_x

                # --- 4. ПРОВЕРКА СТЕН ---
                if arcade.check_for_collision_with_list(enemy, walls):
                    # Если врезались в стену, меняем направление
                    enemy.change_x *= -1
                    enemy.center_x += enemy.change_x

        except KeyError:
            pass

        # --- Invincibility ---
        if self.i_frame > 0:
            self.i_frame -= delta_time
            self.player_sprite.alpha = 150
        else:
            self.player_sprite.alpha = 255

            hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Enemy"])

            if len(hit_list) > 0:
                self.p_hp -= 1
                arcade.play_sound(self.sound_hit)
                self.i_frame = 1.5

                if self.p_hp <= 0:
                    arcade.play_sound(self.sound_hurt)
                    self.setup()

        # Check if player fall to the abyss
        if self.player_sprite.center_y < -100:
            self.level = 1
            self.reset_score = True
            self.setup()

        # Check if the player got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1
            # Turn off score reset when advancing level
            self.reset_score = False
            # Reload game with new level
            self.setup()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.ESCAPE:
            self.setup()

        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)

        # Moveset and turning sides
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        # Attack
        if key == arcade.key.SPACE:
            # Если уже атакуем — выходим, не даем сбросить анимацию
            if self.player_sprite.is_attacking:
                return

            arcade.play_sound(self.sound_attack)
            self.player_sprite.is_attacking = True
            self.player_sprite.cur_texture = 0
            self.player_sprite.hit_1_done = False
            self.player_sprite.hit_2_done = False  # Готовим персонажа нанести урон

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()




def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()