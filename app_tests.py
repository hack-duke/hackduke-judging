import os, app, unittest

from judging_sessions import SimpleSession, CHOICE_A, CHOICE_B
class TestSimpleSession(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(ValueError):
            SimpleSession('asdf')
        for i in [-1, 0, 1]:
            with self.assertRaises(ValueError):
                SimpleSession(i)

    def test_voting(self):
        n = 10
        curr_session = SimpleSession(n)
        judge_1, judge_2 = 'judge_1', 'judge_2'
        self.assertEqual((0,1), curr_session.get_decision(judge_1))
        self.assertEqual((0,1), curr_session.get_decision(judge_1)) # Should be the same thing when requesting same judge
        self.assertEqual((2,3), curr_session.get_decision(judge_2))

        self.assertEqual(curr_session.judge_counts[judge_1],  0)
        self.assertEqual(curr_session.judge_counts[judge_2], 0)

        self.assertTrue(curr_session.perform_decision('wrong_judge', CHOICE_A) != '')
        self.assertTrue(curr_session.perform_decision(judge_1, 'invalid_choice') != '')
        self.assertTrue(curr_session.perform_decision(judge_1, CHOICE_A) == '')
        self.assertTrue(curr_session.perform_decision(judge_2, CHOICE_B) == '')
        self.assertEqual(curr_session.judge_counts[judge_1], 1)
        self.assertEqual(curr_session.judge_counts[judge_2], 1)
        self.assertEqual(len(curr_session.judge_counts), 2)
        self.assertEqual(curr_session.votes[0], 1)
        self.assertEqual(curr_session.votes[1], 0)
        self.assertEqual(curr_session.votes[2], 0)
        self.assertEqual(curr_session.votes[3], 1)
        for i in range(4,n):
            self.assertEqual(curr_session.votes[i], 0)

        curr_session.get_decision(judge_1)
        curr_session.perform_decision(judge_1, CHOICE_A)
        self.assertEqual(curr_session.judge_counts[judge_1], 2)

if __name__ == '__main__':
    unittest.main()

