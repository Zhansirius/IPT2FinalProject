from constants import *
from score_manager import ScoreManager
import arcade
from Player import PlayerCharacter
class GameView(arcade.Window):
    """ Main application class. """

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

        # Initialization of score on screen + loading it
        self.score_manager = ScoreManager()
        self.highscore = self.score_manager.highscore

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

        # 1. Определяем индивидуальный масштаб для каждого уровня
        if self.level >= 5:
            current_tile_scaling = 1.0
        else:
            current_tile_scaling = 1.5
        """Настройка игры. Вызывайте для перезапуска."""
        layer_options = {
            "Touchable": {
                "use_spatial_hash": True
            }
        }

        self.tile_map = arcade.load_tilemap(
            f"assets/lvls/test_lvl{self.level}.tmx",
            scaling=current_tile_scaling,
            layer_options=layer_options
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling

        self.top_of_map = (self.tile_map.height * self.tile_map.tile_height) * self.tile_map.scaling

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
            walls=self.scene["Touchable"],
            gravity_constant=GRAVITY
        )

        # Камеры и интерфейс
        self.camera = arcade.Camera2D()
        self.camera.zoom = 1.2  # <--- ДОБАВЛЯЕМ ПРИБЛИЖЕНИЕ (сделайте персонажа крупнее)
        self.gui_camera = arcade.Camera2D()
        self.gui_camera.match_window()

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

        #Displays the highest score on the screen
        highscore_text = arcade.Text(
            f"High Score: {self.highscore}",
            x=0,
            y=35
        )

        highscore_text.draw()

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

        # --- УМНОЕ ЦЕНТРИРОВАНИЕ И ОГРАНИЧЕНИЕ КАМЕРЫ ---
        zoom = self.camera.zoom

        # Вычисляем реальный размер видимой зоны в игровом мире с учетом масштаба
        visible_width = self.width / zoom
        visible_height = self.height / zoom

        half_w = visible_width / 2
        half_h = visible_height / 2

        # Ограничение по горизонтали (ось X)
        if self.end_of_map < visible_width:
            # Если уровень узкий/вертикальный, фиксируем камеру строго по центру ширины карты
            camera_x = self.end_of_map / 2
        else:
            # Если уровень широкий, плавно ведем за игроком
            camera_x = self.player_sprite.center_x
            if camera_x < half_w:
                camera_x = half_w
            elif camera_x > self.end_of_map - half_w:
                camera_x = self.end_of_map - half_w

        # Ограничение по вертикали (ось Y)
        if self.top_of_map < visible_height:
            # Если уровень низкий, фиксируем по центру высоты карты
            camera_y = self.top_of_map / 2
        else:
            # Если уровень высокий, ведем камеру вверх/вниз за прыжками
            camera_y = self.player_sprite.center_y
            if camera_y < half_h:
                camera_y = half_h
            elif camera_y > self.top_of_map - half_h:
                camera_y = self.top_of_map - half_h

        # Применяем выверенные координаты
        self.camera.position = (camera_x, camera_y)

        # ENEMY MOVEMENT LOGIC
        try:
            enemy_list = self.scene.get_sprite_list("Enemy")
            walls = self.scene["Touchable"]

            for enemy in enemy_list:

                # 1. GRAVITY (We leave it so that they stand on the floor correctly when they spawn)
                enemy.change_y -= GRAVITY
                enemy.center_y += enemy.change_y

                # Floor collision check
                hit_list_y = arcade.check_for_collision_with_list(enemy, walls)
                for wall in hit_list_y:
                    if enemy.change_y < 0:  # The enemy falls to the floor
                        enemy.bottom = wall.top
                        enemy.change_y = 0
                    elif enemy.change_y > 0:  # The enemy hits his head
                        enemy.top = wall.bottom
                        enemy.change_y = 0

                # If the X-speed is 0, skip the walking logic.
                if enemy.change_x == 0:
                    continue

                # --- 2. CHECK THE ABYSS FOR ALL ENEMIES ---
                # We don't check is_smart anymore. Every slug looks at its feet.
                look_ahead = 15 if enemy.change_x > 0 else -15
                check_point = (enemy.center_x + look_ahead, enemy.bottom - 5)

                ground_ahead = arcade.get_sprites_at_point(check_point, walls)

                if not ground_ahead:
                    # There's no land ahead! We're turning around.
                    enemy.change_x *= -1

                # 3. MOVEMENT ALONG X
                enemy.center_x += enemy.change_x

                # 4. CHECKING THE WALLS
                if arcade.check_for_collision_with_list(enemy, walls):
                    # If you hit a wall, change direction
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

                #Save new high score if current score is higher
                # and updating display of that score
                if self.p_hp <= 0:
                    arcade.play_sound(self.sound_hurt)
                    self.score_manager.save_highscore(self.score)
                    self.highscore = self.score_manager.highscore
                    self.setup()

        # Check if player fall to the abyss
        # Check if player fall to the abyss
        if self.player_sprite.center_y < -100:
            # Убрали self.level = 1, чтобы игра запомнила текущий уровень
            self.reset_score = True  # Оставляем, чтобы сбросить здоровье и очки до начальных
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
        # ПОЛНЫЙ ЭКРАН НА F4
        if key == arcade.key.F4:
            self.set_fullscreen(not self.fullscreen)

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

    def on_resize(self, width: int, height: int):
        """Вызывается автоматически, когда окно меняет свой размер."""
        super().on_resize(width, height)

        # Обновляем область вывода графического контекста
        self.ctx.viewport = (0, 0, width, height)

        # Корректируем внутренние параметры камер под новое разрешение окна
        if hasattr(self, "camera") and self.camera:
            self.camera.match_window()

        if hasattr(self, "gui_camera") and self.gui_camera:
            self.gui_camera.match_window()

        if hasattr(self, "bg_camera") and self.bg_camera:
            self.bg_camera.match_window()