import time

def damage_flash():
    """
    Generator for invincibility flashing effect
    """

    while True:
        yield 150
        yield 255

def measure_time(func):
    """
    Decorator that measures function execution time.
    """

    def wrapper(*args, **kwargs):

        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()

        print(
            f"{func.__name__} executed in "
            f"{end_time - start_time:.5f} seconds"
        )

        return result

    return wrapper