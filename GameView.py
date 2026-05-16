from constants import *
from score_manager import ScoreManager
import arcade
from Player import PlayerCharacter
class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()
        # Player's hp
        self.p_hp = 5
        # Invincible frames
        self.i_frame = 0
        # Are they looking at right?
        self.facing_right = True

        self.draw_attack_rect = None

        # Default sounds
        self.sound_attack = arcade.load_sound("assets/sounds/undertale-slash.mp3")
        self.sound_hit = arcade.load_sound("assets/sounds/undertale-damage-taken.mp3")
        self.sound_hit1 = arcade.load_sound("assets/sounds/undertale-sound-effect-attack-hit.mp3")
        self.sound_hurt = arcade.load_sound("assets/sounds/undertale-soul-shatter.mp3")

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

        # 6. Физика (базовая настройка) - ЭТОТ БЛОК СТАТИЧНЫХ СТЕН УДАЛИ И ОСТАВЬ ТОЛЬКО НИЖНИЙ
        # --- ЗАГРУЗКА ДВИЖУЩИХСЯ ПЛАТФОРМ ---
        try:
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")
            for platform in moving_platforms:
                # Считываем скорость (теперь можно задавать и change_y для вертикальных)
                platform.change_x = float(platform.properties.get("change_x", 0.0))
                platform.change_y = float(platform.properties.get("change_y", 0.0))

                # Проверяем, задана ли дистанция движения в Tiled
                if "move_distance" in platform.properties:
                    platform.move_distance = float(platform.properties.get("move_distance"))
                    platform.distance_traveled = 0.0  # Счетчик пройденных пикселей
                else:
                    platform.move_distance = None  # Значит, эта платформа работает по коллизиям
        except KeyError:
            print("Предупреждение: Слой 'Moving Platforms' не найден в карте!")
            self.scene.add_sprite_list("Moving Platforms")
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")

        # --- ЗАГРУЗКА ДИНАМИЧЕСКИХ ШИПОВ ---
        try:
            self.spikes_list = self.scene.get_sprite_list("Spikes")
            for spike in self.spikes_list:
                # Запоминаем верхнюю (активную) точку
                spike.max_y = spike.center_y

                # Считываем настройки из Tiled
                spike.hide_time = float(spike.properties.get("hide_time", 2.0))
                spike.active_time = float(spike.properties.get("active_time", 1.5))
                pop_height = float(spike.properties.get("pop_height", 32.0))

                # Вычисляем нижнюю (скрытую) точку и прячем шип сразу при старте
                spike.min_y = spike.max_y - pop_height
                spike.center_y = spike.min_y

                # Задаем начальное состояние
                spike.state = "hidden"
                spike.timer = 0.0
        except KeyError:
            print("Предупреждение: Слой 'Spikes' не найден в карте!")
            self.scene.add_sprite_list("Spikes")
            self.spikes_list = self.scene.get_sprite_list("Spikes")

        # Создаем физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Touchable"],
            platforms=moving_platforms,
            gravity_constant=GRAVITY
        )
        # Создаем физический движок ОДИН раз, передавая ВСЁ сразу
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Touchable"],
            platforms=moving_platforms,
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

        self.score_text = arcade.Text(
            f"Score: {self.score}",
            x=20,
            y=self.window.height - 80
        )
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.highscore_text = arcade.Text(
            f"High Score: {self.highscore}",
            x=20,
            y=self.window.height - 120
        )

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


        # Draw saved high score on the GUI layer
        self.highscore_text.draw()

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
            first_hit_frame = 3
            second_hit_frame = 9

            current_frame = self.player_sprite.cur_texture
            should_hit = False

            if current_frame == first_hit_frame and not self.player_sprite.hit_1_done:
                self.player_sprite.hit_1_done = True
                should_hit = True
            elif current_frame == second_hit_frame and not self.player_sprite.hit_2_done:
                self.player_sprite.hit_2_done = True
                should_hit = True

            if should_hit:
                attack_hitbox = arcade.SpriteSolidColor(70, 50, color=arcade.color.RED)
                attack_hitbox.bottom = self.player_sprite.bottom

                if self.player_sprite.character_face_direction == 0:
                    attack_hitbox.left = self.player_sprite.right
                else:
                    attack_hitbox.right = self.player_sprite.left

                self.draw_attack_rect = attack_hitbox

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
        visible_width = self.width / zoom
        visible_height = self.height / zoom

        half_w = visible_width / 2
        half_h = visible_height / 2

        if self.end_of_map < visible_width:
            camera_x = self.end_of_map / 2
        else:
            camera_x = self.player_sprite.center_x
            if camera_x < half_w:
                camera_x = half_w
            elif camera_x > self.end_of_map - half_w:
                camera_x = self.end_of_map - half_w

        if self.top_of_map < visible_height:
            camera_y = self.top_of_map / 2
        else:
            camera_y = self.player_sprite.center_y
            if camera_y < half_h:
                camera_y = half_h
            elif camera_y > self.top_of_map - half_h:
                camera_y = self.top_of_map - half_h

        self.camera.position = (camera_x, camera_y)

        # ENEMY MOVEMENT LOGIC
        try:
            enemy_list = self.scene.get_sprite_list("Enemy")
            walls = self.scene["Touchable"]

            for enemy in enemy_list:
                enemy.change_y -= GRAVITY
                enemy.center_y += enemy.change_y

                hit_list_y = arcade.check_for_collision_with_list(enemy, walls)
                for wall in hit_list_y:
                    if enemy.change_y < 0:
                        enemy.bottom = wall.top
                        enemy.change_y = 0
                    elif enemy.change_y > 0:
                        enemy.top = wall.bottom
                        enemy.change_y = 0

                if enemy.change_x == 0:
                    continue

                look_ahead = 15 if enemy.change_x > 0 else -15
                check_point = (enemy.center_x + look_ahead, enemy.bottom - 5)
                ground_ahead = arcade.get_sprites_at_point(check_point, walls)

                if not ground_ahead:
                    enemy.change_x *= -1

                enemy.center_x += enemy.change_x

                if arcade.check_for_collision_with_list(enemy, walls):
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
                    # Save new high score to JSON file if current score is higher
                    self.score_manager.save_highscore(self.score)
                    # Update loaded high score
                    self.highscore = self.score_manager.highscore
                    # Update text on screen
                    self.highscore_text.text = f"High Score: {self.highscore}"
                    self.setup()

        # --- ЛОГИКА ДВИЖУЩИХСЯ ПЛАТФОРМ (ДВА РЕЖИМА) ---
        try:
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")
            walls = self.scene["Touchable"]

            # Разделяем платформы на две группы по их поведению
            distance_platforms = [p for p in moving_platforms if p.move_distance is not None]
            collision_platforms = [p for p in moving_platforms if p.move_distance is None]

            # === РЕЖИМ 1: РАЗВОР ОТ ПО ДИСТАНЦИИ (Новый код) ===
            for platform in distance_platforms:
                # Смещаем по X и считаем расстояние
                if platform.change_x != 0:
                    platform.center_x += platform.change_x
                    platform.distance_traveled += abs(platform.change_x)

                # Смещаем по Y и считаем расстояние
                if platform.change_y != 0:
                    platform.center_y += platform.change_y
                    platform.distance_traveled += abs(platform.change_y)

                # Если прошли нужную дистанцию — разворачиваемся
                if platform.distance_traveled >= platform.move_distance:
                    if platform.change_x != 0:
                        platform.change_x *= -1
                    if platform.change_y != 0:
                        platform.change_y *= -1
                    platform.distance_traveled = 0.0  # Сбрасываем счетчик для обратного пути

            # === РЕЖИМ 2: РАЗВОР ОТ ОТ СТЕН (Твой прошлый рабочий код с platform_id) ===
            if collision_platforms:
                # 1. Двигаем вперед
                for platform in collision_platforms:
                    if platform.change_x != 0:
                        platform.center_x += platform.change_x
                    if platform.change_y != 0:
                        platform.center_y += platform.change_y

                broken_platforms_x = set()
                broken_platforms_y = set()

                # 2. Проверяем коллизии со стенами Touchable
                for platform in collision_platforms:
                    if arcade.check_for_collision_with_list(platform, walls):
                        pid = platform.properties.get("platform_id", 0)
                        if platform.change_x != 0:
                            broken_platforms_x.add(pid)
                        if platform.change_y != 0:
                            broken_platforms_y.add(pid)

                # 3. Синхронно разворачиваем группу
                for platform in collision_platforms:
                    pid = platform.properties.get("platform_id", 0)
                    if pid in broken_platforms_x:
                        platform.change_x *= -1
                        platform.center_x += platform.change_x
                    if pid in broken_platforms_y:
                        platform.change_y *= -1
                        platform.center_y += platform.change_y

        except KeyError:
            pass

        # --- ЛОГИКА РАБОТЫ ШИПОВ (КОНЕЧНЫЙ АВТОМАТ) ---
        try:
            for spike in self.spikes_list:
                spike.timer += delta_time

                # Состояние 1: Сидят под землей и ждут
                if spike.state == "hidden":
                    if spike.timer >= spike.hide_time:
                        spike.state = "rising"
                        spike.timer = 0.0

                # Состояние 2: Вылезают вверх
                elif spike.state == "rising":
                    spike.center_y += 4.0  # Скорость вылета шипов
                    if spike.center_y >= spike.max_y:
                        spike.center_y = spike.max_y
                        spike.state = "active"
                        spike.timer = 0.0

                # Состояние 3: Полностью вылезли, опасны!
                elif spike.state == "active":
                    if spike.timer >= spike.active_time:
                        spike.state = "falling"
                        spike.timer = 0.0

                    # НАНОСИМ УРОН: Только если шип активен и игрок наступил на хитбокс кончика
                    if arcade.check_for_collision(self.player_sprite, spike):
                        if self.i_frame <= 0:  # Проверка фреймов неуязвимости
                            self.p_hp -= 1
                            arcade.play_sound(self.sound_hit)
                            self.i_frame = 1.5

                            # Если здоровье упало до нуля — перезапуск
                            if self.p_hp <= 0:
                                arcade.play_sound(self.sound_hurt)
                                self.score_manager.save_highscore(self.score)
                                self.highscore = self.score_manager.highscore
                                self.setup()
                                break

                # Состояние 4: Уходят обратно под землю
                elif spike.state == "falling":
                    spike.center_y -= 4.0  # Скорость ухода
                    if spike.center_y <= spike.min_y:
                        spike.center_y = spike.min_y
                        spike.state = "hidden"
                        spike.timer = 0.0

        except KeyError:
            pass
        # Check if player fall to the abyss
        if self.player_sprite.center_y < -100:
            self.reset_score = True
            self.setup()

        # Check if the player got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            self.level += 1
            self.reset_score = False
            self.setup()
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        # ПОЛНЫЙ ЭКРАН НА F4
        if key == arcade.key.F4:
            # Toggle fullscreen mode
            self.window.set_fullscreen(
                not self.window.fullscreen
            )

            # Update cameras to new window size
            self.camera.match_window()
            self.gui_camera.match_window()
            self.bg_camera.match_window()

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
        self.window.ctx.viewport = (0, 0, width, height)

        # Корректируем внутренние параметры камер под новое разрешение окна
        if hasattr(self, "camera") and self.camera:
            self.camera.match_window()

        if hasattr(self, "gui_camera") and self.gui_camera:
            self.gui_camera.match_window()

        if hasattr(self, "bg_camera") and self.bg_camera:
            self.bg_camera.match_window()

        # Reposition GUI text after window resize
        self.score_text.x = 20
        self.score_text.y = height - 100

        self.highscore_text.x = 20
        self.highscore_text.y = height - 130