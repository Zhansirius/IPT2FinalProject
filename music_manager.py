import arcade

class MusicManager:
    current_player = None
    current_sound = None
    current_path = None  # Храним путь к текущему проигрываемому файлу

    @classmethod
    def play_music(cls, path, volume=1.0, loop=True):
        # Если этот трек УЖЕ играет прямо сейчас, ничего не делаем
        if cls.current_path == path and cls.current_player:
            return

        # Если запрашивается новый трек, останавливаем старый
        cls.stop_music()

        try:
            cls.current_sound = arcade.load_sound(path)
            # В Arcade 3.x метод возвращает медиаплеер pyglet
            cls.current_player = cls.current_sound.play(
                volume=volume,
                loop=loop
            )
            cls.current_path = path  # Запоминаем путь к новому треку
        except Exception as e:
            print(f"Ошибка воспроизведения музыки {path}: {e}")

    @classmethod
    def stop_music(cls):
        if cls.current_player:
            try:
                # ВНИМАНИЕ: В Pyglet/Arcade 3.x используется .pause() для остановки звука!
                cls.current_player.pause()
            except Exception as e:
                print(f"Ошибка остановки музыки: {e}")
            cls.current_player = None
        cls.current_path = None  # Сбрасываем путь при полной остановке