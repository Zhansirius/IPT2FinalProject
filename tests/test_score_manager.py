import unittest
from score_manager import ScoreManager


class TestScoreManager(unittest.TestCase):

    def setUp(self):
        """
        Creates fresh ScoreManager before every test
        """
        self.score_manager = ScoreManager()

    def test_highscore_is_integer(self):
        """
        Check that highscore is integer
        """
        self.assertIsInstance(
            self.score_manager.highscore,
            int
        )

    def test_save_highscore(self):
        """
        Check that new highscore saves correctly
        """

        old_score = self.score_manager.highscore

        self.score_manager.save_highscore(
            old_score + 100
        )

        self.assertEqual(
            self.score_manager.highscore,
            old_score + 100
        )


if __name__ == "__main__":
    unittest.main()