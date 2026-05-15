import json
import os


class ScoreManager:
    """
    Handles saving and loading high scores using JSON.
    """

    SAVE_FILE = "highscore.json"

    def __init__(self):
        self.highscore = self.load_highscore()

    def load_highscore(self):
        """
        Load high score from JSON file.
        Returns 0 if file doesn't exist or is corrupted.
        """

        # Check if file exists
        if not os.path.exists(self.SAVE_FILE):
            return 0

        try:
            with open(self.SAVE_FILE, "r") as file:
                data = json.load(file)

                # Return stored highscore
                return data.get("highscore", 0)

        except json.JSONDecodeError:
            print("Error: JSON file is corrupted.")
            return 0

        except Exception as e:
            print(f"Unexpected error while loading score: {e}")
            return 0

    def save_highscore(self, score):
        """
        Save new high score if current score is higher.
        """

        if score > self.highscore:
            self.highscore = score

            data = {
                "highscore": self.highscore
            }

            try:
                with open(self.SAVE_FILE, "w") as file:
                    json.dump(data, file, indent=4)

                print(f"High score saved: {self.highscore}")

            except Exception as e:
                print(f"Error saving high score: {e}")

    def reset_highscore(self):
        """
        Reset high score to 0.
        """

        self.highscore = 0

        try:
            with open(self.SAVE_FILE, "w") as file:
                json.dump({"highscore": 0}, file, indent=4)

        except Exception as e:
            print(f"Error resetting high score: {e}")