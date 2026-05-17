import time

def damage_flash():
    """
    Generator for invincibility flashing effect
    """

    while True:
        yield 150
        yield 255

# We implemented a custom Python decorator to measure
# level loading performance.
# The decorator wraps the setup() function and records
# its execution time automatically.

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