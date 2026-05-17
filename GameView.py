from constants import *
from utils import damage_flash, measure_time
from score_manager import ScoreManager
import arcade
from utils import damage_flash
from shooters import Turret, Bullet
from Player import PlayerCharacter
from GameOverView import GameOverView
from Boss import BossEnemy
from VictoryView import VictoryView
from music_manager import MusicManager


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()
        self.boss_list = None
        # Player's hp
        self.max_hp = 5
        self.p_hp = self.max_hp
        # Invincible frames
        self.i_frame = 0

        self.game_over_triggered = False
        # Generator for damage flashing effect
        self.flash_generator = damage_flash()
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

    @measure_time
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

        # --- УПРАВЛЕНИЕ ФОНОВОЙ МУЗЫКОЙ ---
        if self.level == 10:
            bgm_path = "assets/sounds/boss.mp3"
        elif self.level >= 9:
            bgm_path = "assets/sounds/red.mp3"
        elif self.level >= 7:
            bgm_path = "assets/sounds/blue.mp3"
        elif self.level >= 5:
            bgm_path = "assets/sounds/green.mp3"
        else:
            bgm_path = "assets/sounds/first.mp3"

        MusicManager.play_music(bgm_path, loop=True)

        self.tile_map = arcade.load_tilemap(
            f"assets/lvls/test_lvl{self.level}.tmx",
            scaling=current_tile_scaling,
            layer_options=layer_options
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * self.tile_map.scaling
        self.top_of_map = (self.tile_map.height * self.tile_map.tile_height) * self.tile_map.scaling

        self.player_sprite = PlayerCharacter()
        self.scene.add_sprite("Player", self.player_sprite)

        if "SpawnPoint" in self.tile_map.object_lists:
            for obj in self.tile_map.object_lists["SpawnPoint"]:
                if obj.name == "SpawnPoint":
                    self.player_sprite.center_x = obj.shape[0] * TILE_SCALING
                    self.player_sprite.center_y = obj.shape[1] * TILE_SCALING

        self.hp_text = arcade.Text(
            f"HP: {self.p_hp}",
            x=20,
            y=self.window.height - 40,
            color=arcade.color.YELLOW,
            font_size=14,
            bold=True
        )

        self.turrets_list = []
        try:
            self.scene.add_sprite_list("Bullets")
        except KeyError:
            pass

        if "Shooters" in self.tile_map.object_lists:
            for obj in self.tile_map.object_lists["Shooters"]:
                t_x = obj.shape[0] * current_tile_scaling
                t_y = obj.shape[1] * current_tile_scaling

                interval = float(obj.properties.get("interval", 3.0))
                speed_x = float(obj.properties.get("speed_x", 0.0))
                speed_y = float(obj.properties.get("speed_y", -5.0))

                turret = Turret(t_x, t_y, speed_x, speed_y, interval)
                self.turrets_list.append(turret)
        try:
            enemy_list = self.scene.get_sprite_list("Enemy")
            for enemy in enemy_list:
                enemy.is_smart = enemy.properties.get("smart", False)
                enemy.health = int(enemy.properties.get("health", 1))
                enemy.change_x = float(enemy.properties.get("speed", 2))

            print(f"Врагов загружено: {len(enemy_list)}")
        except KeyError:
            print("Предупреждение: Слой 'Enemy' не найден в сцене!")
            self.scene.add_sprite_list("Enemy")

        try:
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")
            for platform in moving_platforms:
                platform.change_x = float(platform.properties.get("change_x", 0.0))
                platform.change_y = float(platform.properties.get("change_y", 0.0))

                if "move_distance" in platform.properties:
                    platform.move_distance = float(platform.properties.get("move_distance"))
                    platform.distance_traveled = 0.0
                else:
                    platform.move_distance = None
        except KeyError:
            print("Предупреждение: Слой 'Moving Platforms' не найден в карте!")
            self.scene.add_sprite_list("Moving Platforms")
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")

        try:
            self.spikes_list = self.scene.get_sprite_list("Spikes")
            for spike in self.spikes_list:
                spike.max_y = spike.center_y
                spike.hide_time = float(spike.properties.get("hide_time", 2.0))
                spike.active_time = float(spike.properties.get("active_time", 1.5))
                pop_height = float(spike.properties.get("pop_height", 32.0))

                spike.min_y = spike.max_y - pop_height
                spike.center_y = spike.min_y
                spike.state = "hidden"
                spike.timer = 0.0
        except KeyError:
            print("Предупреждение: Слой 'Spikes' не найден в карте!")
            self.scene.add_sprite_list("Spikes")
            self.spikes_list = self.scene.get_sprite_list("Spikes")

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Touchable"],
            platforms=moving_platforms,
            gravity_constant=GRAVITY
        )

        self.camera = arcade.Camera2D()
        self.camera.zoom = 1.2
        self.gui_camera = arcade.Camera2D()
        self.gui_camera.match_window()

        if self.reset_score:
            self.score = 0
            self.p_hp = self.max_hp
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

        self.boss_list = arcade.SpriteList()

        if "BossLayer" in self.tile_map.object_lists:
            for obj in self.tile_map.object_lists["BossLayer"]:
                if obj.type == "Boss" or obj.class_name == "Boss":
                    spawn_x = obj.shape[0]
                    spawn_y = obj.shape[1]

                    boss = BossEnemy(spawn_x, spawn_y + 80)
                    self.boss_list.append(boss)

        if len(self.boss_list) > 0:
            self.boss_physics_engine = arcade.PhysicsEnginePlatformer(
                self.boss_list[0],
                walls=self.scene["Touchable"],
                gravity_constant=GRAVITY
            )
        else:
            self.boss_physics_engine = None

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.camera.use()
        self.scene.draw()

        self.boss_list.draw()

        self.gui_camera.use()
        self.score_text.draw()
        self.highscore_text.draw()
        self.hp_text.draw()

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
        self.hp_text.text = f"HP: {self.p_hp}"
        self.draw_attack_rect = None

        self.physics_engine.update()
        self.bg_camera.position = (self.camera.position[0] * 0.2, self.camera.position[1] * 0.2)

        is_on_ground = self.physics_engine.can_jump()
        self.player_sprite.update_animation(is_on_ground, delta_time)

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

                hit_bosses = arcade.check_for_collision_with_list(attack_hitbox, self.boss_list)
                for boss in hit_bosses:
                    if boss.is_invincible or boss.state in ["HURT", "DEAD"]:
                        continue

                    boss.hp -= 1
                    arcade.play_sound(self.sound_hit1)
                    print("Boss HP:", boss.hp)

                    boss.change_x = 0
                    boss.state = "HURT"
                    boss.cur_texture = 0
                    boss.is_invincible = True
                    boss.invincible_timer = 0.0

                    if boss.hp <= 0:
                        boss.state = "DEAD"
                        boss.cur_texture = 0
                        self.score_manager.save_highscore(self.score)
                        self.highscore = self.score_manager.highscore

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

        if self.i_frame > 0:
            self.i_frame -= delta_time
            self.player_sprite.alpha = next(self.flash_generator)
        else:
            self.player_sprite.alpha = 255
            hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Enemy"])

            if len(hit_list) > 0:
                self.p_hp -= 1
                arcade.play_sound(self.sound_hit)
                self.i_frame = 1.5

                if self.p_hp <= 0:
                    arcade.play_sound(self.sound_hurt)
                    self.score_manager.save_highscore(self.score)
                    self.highscore = self.score_manager.highscore
                    self.game_over_triggered = True
                    MusicManager.stop_music()
                    game_over_view = GameOverView(self.score, self.highscore, self.level)
                    self.window.show_view(game_over_view)
                    return

        try:
            moving_platforms = self.scene.get_sprite_list("Moving Platforms")
            walls = self.scene["Touchable"]

            distance_platforms = [p for p in moving_platforms if p.move_distance is not None]
            collision_platforms = [p for p in moving_platforms if p.move_distance is None]

            for platform in distance_platforms:
                if platform.change_x != 0:
                    platform.center_x += platform.change_x
                    platform.distance_traveled += abs(platform.change_x)

                if platform.change_y != 0:
                    platform.center_y += platform.change_y
                    platform.distance_traveled += abs(platform.change_y)

                if platform.distance_traveled >= platform.move_distance:
                    if platform.change_x != 0:
                        platform.change_x *= -1
                    if platform.change_y != 0:
                        platform.change_y *= -1
                    platform.distance_traveled = 0.0

            if collision_platforms:
                for platform in collision_platforms:
                    if platform.change_x != 0:
                        platform.center_x += platform.change_x
                    if platform.change_y != 0:
                        platform.center_y += platform.change_y

                broken_platforms_x = set()
                broken_platforms_y = set()

                for platform in collision_platforms:
                    if arcade.check_for_collision_with_list(platform, walls):
                        pid = platform.properties.get("platform_id", 0)
                        if platform.change_x != 0:
                            broken_platforms_x.add(pid)
                        if platform.change_y != 0:
                            broken_platforms_y.add(pid)

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

        try:
            if hasattr(self, "turrets_list"):
                for turret in self.turrets_list:
                    turret.timer += delta_time
                    if turret.timer >= turret.interval:
                        new_bullet = Bullet(turret.center_x, turret.center_y, turret.speed_x, turret.speed_y)
                        self.scene["Bullets"].append(new_bullet)
                        turret.timer = 0.0

            bullets_list = self.scene.get_sprite_list("Bullets")
            bullets_list.update()

            walls = self.scene["Touchable"]
            for bullet in list(bullets_list):

                if arcade.check_for_collision_with_list(bullet, walls):
                    bullet.remove_from_sprite_lists()
                    continue

                if arcade.check_for_collision(bullet, self.player_sprite):
                    if self.i_frame <= 0:
                        self.p_hp -= 1
                        arcade.play_sound(self.sound_hit)
                        self.i_frame = 1.5
                        bullet.remove_from_sprite_lists()

                        if self.p_hp <= 0:
                            arcade.play_sound(self.sound_hurt)
                            self.score_manager.save_highscore(self.score)
                            self.highscore = self.score_manager.highscore
                            self.game_over_triggered = True
                            MusicManager.stop_music()
                            game_over_view = GameOverView(self.score, self.highscore, self.level)
                            self.window.show_view(game_over_view)
                            return

                if (bullet.right < 0 or bullet.left > self.end_of_map or
                        bullet.top < 0 or bullet.bottom > self.top_of_map):
                    bullet.remove_from_sprite_lists()

        except KeyError:
            pass

        try:
            for spike in self.spikes_list:
                spike.timer += delta_time

                if spike.state == "hidden":
                    if spike.timer >= spike.hide_time:
                        spike.state = "rising"
                        spike.timer = 0.0

                elif spike.state == "rising":
                    spike.center_y += 4.0
                    if spike.center_y >= spike.max_y:
                        spike.center_y = spike.max_y
                        spike.state = "active"
                        spike.timer = 0.0

                elif spike.state == "active":
                    if spike.timer >= spike.active_time:
                        spike.state = "falling"
                        spike.timer = 0.0
                    if arcade.check_for_collision(self.player_sprite, spike):
                        if self.i_frame <= 0:
                            self.p_hp -= 1
                            arcade.play_sound(self.sound_hit)
                            self.i_frame = 1.5

                            if self.p_hp <= 0:
                                arcade.play_sound(self.sound_hurt)
                                self.score_manager.save_highscore(self.score)
                                self.highscore = self.score_manager.highscore
                                self.game_over_triggered = True
                                MusicManager.stop_music()
                                game_over_view = GameOverView(self.score, self.highscore, self.level)
                                self.window.show_view(game_over_view)
                                return

                elif spike.state == "falling":
                    spike.center_y -= 4.0
                    if spike.center_y <= spike.min_y:
                        spike.center_y = spike.min_y
                        spike.state = "hidden"
                        spike.timer = 0.0

        except KeyError:
            pass

        if self.player_sprite.center_y < -100:
            if self.level >= 8:
                self.level += 1
                self.reset_score = False
                self.setup()
                return
            else:
                arcade.play_sound(self.sound_hurt)
                self.score_manager.save_highscore(self.score)
                self.highscore = self.score_manager.highscore
                self.game_over_triggered = True
                MusicManager.stop_music()
                game_over_view = GameOverView(self.score, self.highscore, self.level)
                self.window.show_view(game_over_view)
                return

        if self.player_sprite.center_x >= self.end_of_map:
            self.level += 1
            self.reset_score = False
            self.setup()

        if self.boss_physics_engine is not None:
            for boss in self.boss_list:
                boss.update_boss_ai(self.player_sprite)
                boss.update_animation(delta_time)
                if boss.dead_finished:
                    victory_view = VictoryView(self.score, self.highscore)
                    self.window.show_view(victory_view)
                    return

            self.boss_physics_engine.update()

        for boss in self.boss_list:
            attack_hitbox = boss.get_attack_hitbox()
            if attack_hitbox:
                self.draw_attack_rect = attack_hitbox
                if arcade.check_for_collision(attack_hitbox, self.player_sprite):
                    if self.i_frame <= 0:
                        self.p_hp -= 1
                        self.i_frame = 1.5
                        arcade.play_sound(self.sound_hit)
                        if self.p_hp <= 0:
                            arcade.play_sound(self.sound_hurt)
                            self.score_manager.save_highscore(self.score)
                            self.highscore = self.score_manager.highscore
                            self.game_over_triggered = True
                            MusicManager.stop_music()
                            game_over_view = GameOverView(self.score, self.highscore, self.level)
                            self.window.show_view(game_over_view)
                            return

            if arcade.check_for_collision(boss, self.player_sprite):
                if self.i_frame <= 0 and boss.state != "DEAD":
                    self.p_hp -= 1
                    self.i_frame = 1.5
                    arcade.play_sound(self.sound_hit)
                    if self.p_hp <= 0:
                        arcade.play_sound(self.sound_hurt)
                        self.score_manager.save_highscore(self.score)
                        self.highscore = self.score_manager.highscore
                        self.game_over_triggered = True
                        MusicManager.stop_music()
                        game_over_view = GameOverView(self.score, self.highscore, self.level)
                        self.window.show_view(game_over_view)
                        return

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.F4:
            self.window.set_fullscreen(not self.window.fullscreen)

        if key == arcade.key.ESCAPE:
            MusicManager.stop_music()
            self.setup()

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        if key == arcade.key.SPACE:
            if self.player_sprite.is_attacking:
                return

            arcade.play_sound(self.sound_attack)
            self.player_sprite.is_attacking = True
            self.player_sprite.cur_texture = 0
            self.player_sprite.hit_1_done = False
            self.player_sprite.hit_2_done = False
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

        self.window.ctx.viewport = (0, 0, width, height)

        if hasattr(self, "camera") and self.camera:
            self.camera.match_window()

        if hasattr(self, "gui_camera") and self.gui_camera:
            self.gui_camera.match_window()

        if hasattr(self, "bg_camera") and self.bg_camera:
            self.bg_camera.match_window()

        self.hp_text.x = 20
        self.hp_text.y = height - 50

        self.score_text.x = 20
        self.score_text.y = height - 90

        self.highscore_text.x = 20
        self.highscore_text.y = height - 130